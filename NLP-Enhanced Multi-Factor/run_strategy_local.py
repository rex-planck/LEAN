
import pandas as pd
import glob
import os
import matplotlib.pyplot as plt

def run_simple_backtest():
    """
    一个简单的纯 Python 回测，用于验证 Sentiment 因子。
    使用 data/alternative/sentiment_reports/ 下的研报情感数据。
    """
    print("开始运行简单回测 (Mock Backtest)...")
    
    # 1. 加载数据
    price_dir = "data/equity/daily"
    # 切换到 研报情感数据
    sentiment_dir = "data/alternative/sentiment_reports" 
    
    # 金风科技, 明阳智能, 铜陵有色, 云南铜业, 吉电股份, 振华股份
    stocks = ['002202', '601615', '000630', '000878', '000875', '603067']
    
    results = {}
    
    for stock in stocks:
        print(f"Backtesting {stock}...")
        
        # 读取价格
        price_path = os.path.join(price_dir, f"{stock}.csv")
        if not os.path.exists(price_path):
            print(f"  Missing price data for {stock}")
            continue
            
        df_price = pd.read_csv(price_path)
        # 统一转为小写 date, open, high, low, close, volume 以便处理
        df_price.columns = df_price.columns.str.lower()
        
        # 确保日期列存在
        date_col = None
        if 'date' in df_price.columns:
            date_col = 'date'
        elif '日期' in df_price.columns:
            date_col = '日期'
            
        if not date_col:
            print(f"  Warning: No date column in price data for {stock}")
            continue

        df_price[date_col] = pd.to_datetime(df_price[date_col])
        df_price.set_index(date_col, inplace=True)
        df_price.sort_index(inplace=True)
        
        # 计算日收益率
        df_price['Daily_Return'] = df_price['close'].pct_change()

        # --- 多因子逻辑：计算技术指标 (MA) ---
        df_price['MA5'] = df_price['close'].rolling(window=5).mean()
        df_price['MA20'] = df_price['close'].rolling(window=20).mean()
        
        # 读取情感数据 (研报)
        # 文件名格式: {stock}_report_sentiment.csv
        sent_path = os.path.join(sentiment_dir, f"{stock}_report_sentiment.csv")
        sentiment_map = {}
        
        if os.path.exists(sent_path):
            df_sent = pd.read_csv(sent_path)
            
            # 研报接口通常返回 '日期' 列
            sent_date_col = None
            if '日期' in df_sent.columns:
                sent_date_col = '日期'
            elif 'date' in df_sent.columns:
                sent_date_col = 'date'
            elif '发布时间' in df_sent.columns:
                sent_date_col = '发布时间'
                
            if sent_date_col and 'sentiment_score' in df_sent.columns:
                # 转换为 datetime
                df_sent[sent_date_col] = pd.to_datetime(df_sent[sent_date_col], errors='coerce').dt.normalize()
                
                # 去除无效日期
                df_sent = df_sent.dropna(subset=[sent_date_col])

                # 按日期聚合 Sentiment Score (如果一天多条研报，取平均)
                daily_sentiment = df_sent.groupby(sent_date_col)['sentiment_score'].mean()
                
                # 转为字典 {timestamp: score}
                sentiment_map = daily_sentiment.to_dict()
            else:
                print(f"  Warning: Could not parse date or sentiment_score from {sent_path}")
                
        # 策略逻辑
        capital = 10000.0
        position = 0 # 0 or 1
        equity_curve = []
        
        # DEBUG: 打印日期范围交集
        price_dates = set(df_price.index)
        sentiment_dates = set(sentiment_map.keys())
        common_dates = price_dates.intersection(sentiment_dates)
        
        print(f"  Price dates: {len(price_dates)} (Start: {df_price.index[0]}, End: {df_price.index[-1]})")
        print(f"  Sentiment dates: {len(sentiment_dates)}")
        if len(sentiment_dates) > 0:
            print(f"  Sentiment Sample: {list(sentiment_dates)[0]} Value: {sentiment_map[list(sentiment_dates)[0]]}")
        print(f"  Common dates: {len(common_dates)}")

        if len(common_dates) == 0:
             print("  [WARNING] No common dates found! Check date parsing.")

        # 信号衰减参数
        current_sentiment = 0.0
        decay_factor = 0.9 # 每天衰减 10%
        
        for date, row in df_price.iterrows():
            # 获取当日是否有新信号
            # 注意：DataFrame index 是 Timestamp，sentiment_map key 也是 Timestamp，可以直接匹配
            new_sentiment = sentiment_map.get(date, 0.0)
            
            if new_sentiment != 0.0:
                # 如果有新消息，更新当前情绪
                current_sentiment = new_sentiment
                # print(f"  [NEWS] Date: {date}, New Sentiment: {new_sentiment:.4f}")
            else:
                # 否则情绪随时间衰减
                current_sentiment *= decay_factor
            
            # --- 融合策略逻辑 (Multi-Factor) ---
            
            # 1. 技术面信号 (Trend)
            ma5 = row['MA5']
            ma20 = row['MA20']
            tech_signal = 0 # 中性
            
            if pd.notna(ma5) and pd.notna(ma20):
                if ma5 > ma20:
                    tech_signal = 1 # 金叉/多头排列
                elif ma5 < ma20:
                    tech_signal = -1 # 死叉/空头排列
            
            # 2. 舆情面信号 (Sentiment)
            # current_sentiment 已经在上面计算并衰减了
            
            # 3. 信号融合
            # 逻辑：技术面看多 + 舆情不看空 = 买入
            #      技术面看空 + 舆情不看多 = 卖出
            #      舆情极度看多 (>0.8) = 强力买入 (忽略技术面)
            
            target_position = position
            
            if current_sentiment > 0.8:
                # 舆情强驱动
                target_position = 1
            elif tech_signal == 1:
                # 技术面看多
                if current_sentiment > -0.2: # 只要舆情不是太差，就跟进
                    target_position = 1
                else:
                    target_position = 0 # 舆情太差，过滤掉技术面信号
            elif tech_signal == -1:
                # 技术面看空
                if current_sentiment > 0.5: # 除非舆情非常好，否则卖出
                    target_position = 1
                else:
                    target_position = 0
            
            # 执行
            position = target_position
                
            # 计算当日盈亏
            ret = row['Daily_Return']
            if pd.isna(ret): ret = 0.0
            
            if position == 1:
                capital = capital * (1 + ret)
                
            equity_curve.append(capital)
            
        df_price['Equity'] = equity_curve
        # 计算基准曲线（买入持有）
        initial_price = df_price['close'].iloc[0]
        df_price['Benchmark'] = 10000.0 * (df_price['close'] / initial_price)
        
        results[stock] = {
            'Equity': df_price['Equity'],
            'Benchmark': df_price['Benchmark']
        }
        
        final_return = (capital - 10000) / 10000 * 100
        benchmark_return = (df_price['Benchmark'].iloc[-1] - 10000) / 10000 * 100
        print(f"  Final Return: {final_return:.2f}% (Benchmark: {benchmark_return:.2f}%)")

    # 创建结果目录
    output_dir = "backtest_results"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # 分别绘图
    for i, (stock, data) in enumerate(results.items()):
        if not data['Equity'].empty:
            plt.figure(figsize=(10, 6))
            
            # 策略曲线（实线）
            plt.plot(data['Equity'].index, data['Equity'].values, 
                    label=f"{stock} Strategy", color='red', linewidth=2)
            # 基准曲线（虚线）
            plt.plot(data['Benchmark'].index, data['Benchmark'].values, 
                    label=f"{stock} Buy & Hold", color='blue', linestyle='--', alpha=0.7)
            
            plt.title(f"{stock}: Strategy vs Buy & Hold")
            plt.xlabel("Date")
            plt.ylabel("Portfolio Value (Initial: 10000)")
            plt.legend()
            plt.grid(True)
            
            save_path = os.path.join(output_dir, f"{stock}_backtest.png")
            plt.savefig(save_path)
            plt.close() # 关闭图形，释放内存
            print(f"Saved chart for {stock} to {save_path}")

    print(f"所有回测结果图已保存至 {output_dir}/ 目录")

if __name__ == "__main__":
    run_simple_backtest()
