import akshare as ak
import pandas as pd

stock = "002202"

print(f"Testing stock_research_report_em for {stock}...")
try:
    df_report = ak.stock_research_report_em(symbol=stock)
    print("Success! Columns:", df_report.columns.tolist())
    print(df_report.head(1))
except Exception as e:
    print(f"Failed: {e}")

print(f"\nTesting stock_notice_report for {stock}...")
try:
    # 尝试不同的参数或接口，如果 stock_notice_report 不存在或报错
    # 有些版本可能是 stock_notice_report_em
    df_notice = ak.stock_notice_report(symbol=stock)
    print("Success! Columns:", df_notice.columns.tolist())
    print(df_notice.head(1))
except Exception as e:
    print(f"Failed: {e}")
