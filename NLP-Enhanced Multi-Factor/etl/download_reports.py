import akshare as ak
import pandas as pd
import os
import time

def download_report_data():
    """
    下载个股研报和公告数据 (替代新闻，以获取更长历史)
    使用接口: 
    1. stock_research_report_em (东方财富-个股研报)
    2. stock_notice_report (东方财富-个股公告)
    """
    report_save_dir = "data/alternative/reports"
    notice_save_dir = "data/alternative/notices"
    os.makedirs(report_save_dir, exist_ok=True)
    os.makedirs(notice_save_dir, exist_ok=True)
    
    # 目标股票
    # 金风科技, 明阳智能, 铜陵有色, 云南铜业, 吉电股份, 振华股份
    stocks = ['002202', '601615', '000630', '000878', '000875', '603067']
    
    for stock in stocks:
        # 1. 下载研报
        print(f"正在获取 {stock} 研报数据...")
        try:
            df_report = ak.stock_research_report_em(symbol=stock)
            if not df_report.empty:
                # 简单清洗
                if '日期' in df_report.columns:
                    df_report['日期'] = pd.to_datetime(df_report['日期']).dt.strftime('%Y-%m-%d')
                
                report_path = os.path.join(report_save_dir, f"{stock}_reports.csv")
                df_report.to_csv(report_path, index=False)
                print(f"已保存研报: {report_path} (共 {len(df_report)} 条)")
            else:
                print(f"{stock} 研报为空")
        except Exception as e:
            print(f"获取 {stock} 研报失败: {e}")
            
        # 2. 公告接口暂时不稳定，跳过
        # df_notice = ak.stock_notice_report(symbol=stock)

        # 礼貌性延时
        time.sleep(2)

if __name__ == "__main__":
    download_report_data()
