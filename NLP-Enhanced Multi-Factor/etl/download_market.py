import akshare as ak
import pandas as pd
import os
from datetime import datetime, timedelta
import time

def download_market_data(symbol="000300", period="365"):
    """
    下载沪深300成分股的日线数据
    """
    print(f"正在获取 {symbol} 成分股列表...")
    
    # 1. 设置目标股票池 (用户指定)
    # 金风科技, 明阳智能, 铜陵有色, 云南铜业, 吉电股份, 振华股份
    stocks = ['002202', '601615', '000630', '000878', '000875', '603067']
    print(f"目标股票列表: {stocks}")

    # 创建保存目录
    save_dir = "data/equity/daily"
    os.makedirs(save_dir, exist_ok=True)

    # 2. 循环下载日线数据
    # 为了回测能覆盖研报历史，我们下载过去3年的数据 (365*3 = 1095)
    # 如果 AKShare 接口受限，可能不会返回这么久，但尽量请求
    target_days = 365 * 3 
    start_date = (datetime.now() - timedelta(days=target_days)).strftime("%Y%m%d")
    end_date = datetime.now().strftime("%Y%m%d")
    print(f"请求数据时间跨度: {start_date} - {end_date}")

    for stock in stocks: 
        print(f"正在下载 {stock} ...")
        try:
            # 使用 stock_zh_a_hist 接口
            df = ak.stock_zh_a_hist(symbol=stock, start_date=start_date, end_date=end_date, adjust="qfq")
            
            if df.empty:
                print(f"{stock} 数据为空，跳过")
                continue

            # 重命名列以符合 Lean 习惯 (Date, Open, High, Low, Close, Volume)
            # AKShare 返回: 日期, 开盘, 收盘, 最高, 最低, 成交量, ...
            df = df.rename(columns={
                '日期': 'Date',
                '开盘': 'Open',
                '最高': 'High',
                '最低': 'Low',
                '收盘': 'Close',
                '成交量': 'Volume'
            })
            
            # 只保留需要的列
            df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
            
            # 保存为 CSV
            file_path = os.path.join(save_dir, f"{stock}.csv")
            df.to_csv(file_path, index=False)
            print(f"已保存: {file_path}")
            
            # 礼貌性延时
            time.sleep(0.5)
            
        except Exception as e:
            print(f"下载 {stock} 失败: {e}")

if __name__ == "__main__":
    download_market_data()
