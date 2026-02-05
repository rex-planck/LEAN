
from AlgorithmImports import *
import pandas as pd
import csv
from datetime import datetime

class SentimentAlphaStrategy(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2023, 1, 1)  # Set Start Date
        self.SetEndDate(2025, 12, 31)  # Set End Date (Extended to cover recent data)
        self.SetCash(1000000)  # Set Strategy Cash
        
        # 股票列表
        self.stocks = ['002202', '601615', '000630', '000878', '000875', '603067']
        self.stock_symbols = {}
        self.sentiment_data = {}
        
        for stock in self.stocks:
            # 添加股票行情数据 (Daily Resolution)
            # Lean 会查找 data/equity/daily/{stock}.csv
            # 如果是 A股，Lean 默认没有映射，我们需要确保 Symbol 格式正确
            # 这里我们使用 AddEquity 并指定 Resolution.Daily
            # 假设本地数据文件名如 000630.csv，不带后缀 .SZ/.SH
            # 但是 AddEquity 通常需要 Market.USA 或其他。
            # 为了让 Lean 读取本地 CSV，我们需要确保数据路径和格式匹配。
            # 如果 data/equity/daily/000630.csv 存在，我们可以尝试 AddEquity("000630", Resolution.Daily)
            
            # 注意：默认 Lean 配置可能将 Market 设为 USA。
            # 如果我们使用自定义数据源，我们可以直接用 AddData。
            # 但为了交易，我们需要 Underlying Equity。
            
            # 尝试添加 Equity
            equity = self.AddEquity(stock, Resolution.Daily)
            self.stock_symbols[stock] = equity.Symbol
            
            # 添加自定义情感数据
            # 使用 ReportSentiment 类
            # 关联到对应的股票 Symbol
            self.AddData(ReportSentiment, f"{stock}_sentiment", Resolution.Daily)
            
            # 初始化情感分
            self.sentiment_data[stock] = 0.5 # Neutral start

    def OnData(self, data):
        # 遍历每只股票
        for stock in self.stocks:
            sentiment_symbol = f"{stock}_sentiment"
            
            # 检查是否有新的情感数据
            if data.ContainsKey(sentiment_symbol):
                sentiment = data[sentiment_symbol]
                if sentiment is not None:
                    # 更新该股票的情感分
                    score = sentiment.Value
                    self.sentiment_data[stock] = score
                    self.Debug(f"{self.Time}: {stock} New Sentiment Score: {score}")

            # 获取当前情感分
            current_sentiment = self.sentiment_data[stock]
            
            # 交易逻辑
            # 如果情感分 > 0.6，做多 (Weight 0.15)
            # 如果情感分 < 0.4，清仓
            # 简单策略：基于情感分调整仓位
            
            if not self.Securities[stock].Invested:
                if current_sentiment > 0.6:
                    self.SetHoldings(stock, 0.15)
                    self.Debug(f"{self.Time}: Buy {stock} (Sentiment: {current_sentiment})")
            else:
                if current_sentiment < 0.4:
                    self.Liquidate(stock)
                    self.Debug(f"{self.Time}: Sell {stock} (Sentiment: {current_sentiment})")

class ReportSentiment(PythonData):
    """
    自定义数据类，用于读取研报情感 CSV
    """
    def GetSource(self, config, date, isLiveMode):
        # 构建文件路径
        # config.Symbol.Value 会是 "002202_sentiment"
        stock_code = config.Symbol.Value.split('_')[0]
        # 使用相对路径，假设 Lean 在项目根目录运行
        # 文件路径: data/alternative/sentiment_reports/000630_report_sentiment.csv
        source = f"data/alternative/sentiment_reports/{stock_code}_report_sentiment.csv"
        return SubscriptionDataSource(source, SubscriptionTransportMedium.LocalFile)

    def Reader(self, config, line, date, isLiveMode):
        if not (line.strip() and line[0].isdigit()): return None

        try:
            # 解析 CSV 行
            # 使用 csv module 防止逗号干扰
            # 格式: 序号,股票代码,股票简称,...,日期,链接,sentiment_score
            # 倒数第一列: score
            # 倒数第三列: 日期
            
            # 简单 split 可能会有问题如果字段内有逗号，但这里为了性能先试 split
            parts = line.split(',')
            
            # 如果 split 后列数不对，可能需要 csv reader
            # 假设结构相对固定，最后几列应该没问题
            
            score_str = parts[-1].strip()
            date_str = parts[-3].strip() # 日期列
            
            # 解析日期
            try:
                # 格式 2025-12-09
                time_obj = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                return None

            # 创建对象
            sentiment = ReportSentiment()
            sentiment.Symbol = config.Symbol
            sentiment.Time = time_obj
            sentiment.Value = float(score_str)
            
            # 结束时间 = 开始时间 + 1天 (日频数据)
            sentiment.EndTime = sentiment.Time + timedelta(days=1)
            
            return sentiment
            
        except Exception as e:
            # print(f"Error parsing line: {line} - {e}")
            return None
