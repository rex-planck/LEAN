import akshare as ak
import pandas as pd
import os
from datetime import datetime, timedelta
import time

def download_news_data(symbol="000300", period="30"):
    """
    下载个股新闻摘要数据
    """
    save_dir = "data/alternative/news"
    os.makedirs(save_dir, exist_ok=True)
    
    # 获取目标股票 (和 download_market.py 保持一致)
    # 金风科技, 明阳智能, 铜陵有色, 云南铜业, 吉电股份, 振华股份
    stocks = ['002202', '601615', '000630', '000878', '000875', '603067']
    
    for stock in stocks:
        print(f"正在获取 {stock} 新闻...")
        try:
            # 尝试获取更多数据: 
            # 1. stock_news_em (东方财富)
            # 2. stock_info_global_cls (财联社 - 需过滤) - 这里简化仍用东财，但尝试获取更多页面
            # AKShare stock_news_em 默认只返回最近一页，我们这里无法通过参数控制页数
            # 只能作为演示。如果需要更多，可能需要爬虫或付费接口。
            
            # 尝试改用 stock_zh_a_spot_em 等接口不包含新闻
            # 尝试 stock_ud_news_em (个股公告) 也不完全是新闻
            
            # 实际上 AKShare 很多接口受限于源站。
            # 我们这里尝试合并 stock_news_em 的结果
            
            df = ak.stock_news_em(symbol=stock)
            
            if df.empty:
                print(f"{stock} 新闻为空")
                continue
                
            # 保存
            file_path = os.path.join(save_dir, f"{stock}_news.csv")
            df.to_csv(file_path, index=False)
            print(f"已保存: {file_path}")
            
        except Exception as e:
            print(f"获取 {stock} 新闻失败: {e}")
            
if __name__ == "__main__":
    download_news_data()
