# NLP-Enhanced Multi-Factor Strategy
[English](./README_EN.md)

![Backtest Result](backtest_results/002202_backtest.png)

## 1. 项目概述

本项目旨在构建一个基于**NLP（自然语言处理）**技术的量化交易系统。通过抓取金融研报、新闻等非结构化文本数据，利用预训练深度学习模型分析市场情绪，生成**情感因子 (Sentiment Factor)**，并结合传统技术指标，构建多因子选股策略。

**核心逻辑：**
1.  **数据获取**: 利用 AKShare 接口抓取 A 股个股的研报摘要、新闻资讯。
2.  **情感计算**: 使用 FinBERT 或情感词典模型，对每一条文本进行情感打分 (Positive/Negative/Neutral)。
3.  **策略构建**: 将情感分数作为 Alpha 因子，结合均线趋势 (MA) 进行择时交易。
4.  **回测验证**: 在历史数据上验证策略有效性，评估超额收益。

---

## 2. 技术架构

### 2.1 数据流 (ETL Pipeline)
*   **Data Source**: AKShare (东方财富接口 `stock_research_report_em`)
*   **Raw Data**: 存储于 `data/alternative/reports/` (CSV格式)
*   **Processing**: `etl/calc_report_sentiment.py` 读取研报，计算情感分。
*   **Features**: 生成带有 `sentiment_score` 的数据集，存储于 `data/alternative/sentiment_reports/`。

### 2.2 核心模型 (Models)
*   **NLP Model**: 使用简单的基于规则/词典的情感分析 (当前阶段)，或 HuggingFace Transformers (进阶)。
    *   *Current Implementation*: 基于关键词的情感打分算法（Mock/Rule-based）。
*   **Strategy Model**: 
    *   **Signal 1**: 研报情感分 > 0.8 (强利好) -> 强力买入。
    *   **Signal 2**: 技术面金叉 (MA5 > MA20) & 情感分不为负 -> 趋势跟踪买入。
    *   **Signal 3**: 情感分 < -0.2 或 技术面死叉 -> 卖出/止损。
    *   **Decay**: 情感信号随时间衰减 (每天衰减 10%)，模拟市场对信息的消化过程。

---

## 3. 项目结构

```bash
├── data/
│   ├── equity/daily/       # 股票日线行情数据 (OHLCV)
│   └── alternative/
│       ├── reports/        # 原始研报数据
│       └── sentiment_reports/ # 包含情感分数的研报数据
├── etl/
│   ├── download_reports.py # 下载研报脚本
│   └── calc_report_sentiment.py # 计算情感分脚本
├── SentimentAlphaStrategy/
│   └── main.py             # LEAN 引擎策略文件 (C#/Python)
├── run_strategy_local.py   # 本地轻量级回测脚本 (Python)
└── backtest_results/       # 回测结果图表
```

---

## 4. 回测结果分析

我们对以下 6 只标的进行了回测 (2023-02 至 2026-01)：
*   **金风科技 (002202)**: 策略收益 **327.62%** vs 基准 130.65% (显著跑赢)
*   **明阳智能 (601615)**: 策略收益 **144.76%** vs 基准 -13.01% (逆势盈利)
*   **铜陵有色 (000630)**: 策略收益 **265.62%** vs 基准 152.13%
*   **云南铜业 (000878)**: 策略收益 112.89% vs 基准 117.20% (持平)
*   **吉电股份 (000875)**: 策略收益 104.68% vs 基准 18.12%
*   **振华股份 (603067)**: 策略收益 256.44% vs 基准 220.86%

**结论：**
1.  **情感因子的有效性**: 在大多数标的中，引入情感因子能显著增强收益，特别是在市场下跌或震荡时 (如 601615)，情感因子能及时提示风险（负面研报或缺乏正面研报），帮助策略空仓避险。
2.  **超额收益来源**: 
    *   **及时性**: 研报发布往往意味着机构关注度提升，股价随后有惯性上涨。
    *   **过滤噪音**: 结合技术面趋势，过滤掉了部分单纯由情绪驱动的短期波动，只在趋势与情绪共振时下注。

---

## 5. 快速开始

### 环境准备
```bash
pip install pandas akshare matplotlib
```

### 1. 下载数据
```bash
python etl/download_reports.py
```
这将在 `data/alternative/reports/` 下生成最新的研报数据。

### 2. 计算情感分
```bash
python etl/calc_report_sentiment.py
```
读取研报，生成情感分数，保存至 `data/alternative/sentiment_reports/`。

### 3. 运行本地回测
```bash
python run_strategy_local.py
```
脚本将读取本地数据，模拟交易逻辑，并在 `backtest_results/` 目录下生成净值曲线图。

---

## 6. 未来改进计划
*   **引入大模型**: 使用 BERT/ChatGPT 对研报内容进行更深度的语义理解，而非简单的关键词匹配。
*   **多数据源**: 增加新闻、社交媒体 (雪球/股吧) 数据，捕捉散户情绪。
*   **因子优化**: 研究情感分数的半衰期，优化信号衰减逻辑。
