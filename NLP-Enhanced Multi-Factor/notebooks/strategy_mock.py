import pandas as pd
import glob
import os
import matplotlib.pyplot as plt

def run_simple_backtest():
    """
    一个简单的纯 Python 回测，用于验证 Sentiment 因子。
    假设策略：
    1. 每日读取Sentiment Score。
    2. 如果 Score > 0.5 (且昨日收益率 > 0，即动量为正)，则持有。
    3. 否则空仓。
    """
    print("开始运行简单回测 (Mock Backtest)...")
    
    # 1. 加载数据
    price_dir = "data/equity/daily"
    # 切换到 全文情感数据
    sentiment_dir = "data/alternative/sentiment_fulltext" 
    
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
        # 根据 read_file 结果，列名为 Date,Open,High,Low,Close,Volume (英文首字母大写)
        # 我们统一转为小写 date, open, high, low, close, volume 以便处理
        df_price.columns = df_price.columns.str.lower()
        
        df_price['date'] = pd.to_datetime(df_price['date'])
        df_price.set_index('date', inplace=True)
        df_price.sort_index(inplace=True)
        
        # 计算日收益率
        df_price['Daily_Return'] = df_price['close'].pct_change()

        # --- 多因子逻辑：计算技术指标 (MA) ---
        df_price['MA5'] = df_price['close'].rolling(window=5).mean()
        df_price['MA20'] = df_price['close'].rolling(window=20).mean()
        
        # 读取情感数据 (全文)
        # 注意文件名变成了 _fulltext_sentiment.csv
        sent_path = os.path.join(sentiment_dir, f"{stock}_fulltext_sentiment.csv")
        sentiment_map = {}
        
        if os.path.exists(sent_path):
            df_sent = pd.read_csv(sent_path)
            
            # 研报接口通常返回 '日期' 列
            date_col = None
            if '日期' in df_sent.columns:
                date_col = '日期'
            elif 'date' in df_sent.columns:
                date_col = 'date'
            elif '发布时间' in df_sent.columns:
                date_col = '发布时间'
                
            if date_col:
                # 转换为 datetime
                df_sent[date_col] = pd.to_datetime(df_sent[date_col]).dt.normalize() # 只取日期部分
                
                # 按日期聚合 Sentiment Score (如果一天多条新闻，取平均)
                daily_sentiment = df_sent.groupby(date_col)['sentiment_score'].mean()
                
                # 转为字典 {timestamp: score}
                sentiment_map = daily_sentiment.to_dict()
                
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
            print(f"  Sentiment Sample: {list(sentiment_dates)[0]}")
        print(f"  Common dates: {len(common_dates)}")

        if len(common_dates) == 0:
             print("  [WARNING] No common dates found! Check date parsing.")

        # 信号衰减参数
        current_sentiment = 0.0
        decay_factor = 0.9 # 每天衰减 10%
        
        for date, row in df_price.iterrows():
            # 获取当日是否有新信号
            new_sentiment = sentiment_map.get(date, 0.0)
            
            if new_sentiment != 0.0:
                # 如果有新消息，更新当前情绪 (加权平均或直接覆盖，这里选择直接更新)
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
        results[stock] = df_price['Equity']
        
        final_return = (capital - 10000) / 10000 * 100
        print(f"  Final Return: {final_return:.2f}%")

    # 简单绘图
    plt.figure(figsize=(10, 6))
    for stock, curve in results.items():
        plt.plot(curve.index, curve.values, label=f"{stock}")
    
    plt.title("NLP-Enhanced Strategy Mock Backtest")
    plt.legend()
    plt.savefig("backtest_result.png")
    print("回测结束，结果已保存至 backtest_result.png")

if __name__ == "__main__":
    run_simple_backtest()
