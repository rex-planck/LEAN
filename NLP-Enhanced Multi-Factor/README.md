# NLP-Enhanced Multi-Factor Strategy (NLP 增强多因子策略)

[English](./README_EN.md)

![Backtest Result](backtest_results/002202_backtest.png)
*(图示：金风科技 002202 回测净值曲线，策略显著跑赢基准)*

## 1. 项目概述 (Overview)

本项目旨在构建一个前沿的**基于 NLP（自然语言处理）技术的量化交易系统**。通过自动化抓取金融市场中的非结构化文本数据（如个股研报、新闻资讯），利用深度学习模型或情感词典分析市场情绪，生成可交易的**情感因子 (Sentiment Factor)**。该因子与传统的技术指标（如均线趋势）相结合，构建出一个稳健的多因子选股策略，旨在捕捉机构情绪变化带来的超额收益。

**核心逻辑：**
1.  **多源数据获取 (Data ETL)**: 利用 `AKShare` 接口实时抓取 A 股市场的个股研报摘要、公告及新闻数据。
2.  **情感量化计算 (Sentiment Analysis)**: 使用 FinBERT 模型或金融情感词典，对每一篇研报进行情感打分 (Positive/Negative/Neutral)，将非结构化文本转化为结构化的 `sentiment_score`。
3.  **多因子策略构建 (Factor Combinations)**: 
    *   **Alpha 因子**: 研报情感得分（反映机构看多/看空态度）。
    *   **Beta 因子**: 均线趋势（MA5/MA20 金叉死叉）确认市场方向。
    *   **风险控制**: 基于情感分数的动态仓位管理。
4.  **回测与验证 (Backtesting)**: 使用 LEAN 引擎或本地 Python 脚本在历史数据上验证策略有效性，评估年化收益、最大回撤及夏普比率。

---

## 2. 技术架构与工作流

### 2.1 数据管道 (ETL Pipeline)
*   **Data Source**: 
    *   研报数据: AKShare `stock_research_report_em` (东方财富)
    *   新闻数据: AKShare `stock_news_em` (可选)
*   **Raw Data Storage**: 原始数据以 CSV 格式存储于 `data/alternative/reports/`。
*   **Feature Engineering**: `etl/calc_report_sentiment.py` 脚本读取原始研报，进行清洗、分词、情感打分。
*   **Processed Data**: 生成带有 `sentiment_score` 的时间序列数据，存储于 `data/alternative/sentiment_reports/`，供策略引擎直接调用。

### 2.2 核心模型 (Models)
*   **NLP Model**: 
    *   *当前实现*: 基于特定金融关键词（如“买入”、“增持”、“超预期” vs “下调”、“风险”）的规则/词典打分模型。
    *   *未来升级*: 计划接入 HuggingFace Transformers (FinBERT) 进行更精准的上下文语义分析。
*   **Trading Strategy**: 
    *   **买入信号**: 当日有新研报发布且情感分 > 0.8 (强利好) **AND** 股价位于均线之上。
    *   **卖出信号**: 情感分 < -0.2 (利空/不及预期) **OR** 技术面出现死叉。
    *   **信号衰减**: 情感信号随时间线性衰减 (每日衰减 10%)，模拟市场对信息的逐步消化过程。

---

## 3. 项目结构 (Project Structure)

```bash
├── data/
│   ├── equity/daily/          # 股票日线行情数据 (OHLCV)
│   └── alternative/
│       ├── reports/           # 原始研报数据 (Raw Data)
│       └── sentiment_reports/ # 清洗并计算情感分后的研报数据 (Processed Features)
├── etl/
│   ├── download_reports.py    # 数据下载脚本 (AKShare -> Local)
│   └── calc_report_sentiment.py # 情感计算脚本 (Text -> Sentiment Score)
├── SentimentAlphaStrategy/
│   └── main.py                # LEAN 引擎策略主文件 (C#/Python 适配)
├── run_strategy_local.py      # 本地轻量级回测引擎 (Python, Pandas-based)
├── backtest_results/          # 回测结果图表与日志
└── README.md                  # 项目文档
```

---

## 4. 回测表现 (Performance)

我们对以下代表性标的进行了回测 (区间: 2023-02 至 2026-01)，结果显示策略在大多数情况下具备显著的超额收益能力：

| 股票代码 | 股票名称 | 策略总收益 | 基准收益 (Buy&Hold) | 表现评价 |
| :--- | :--- | :--- | :--- | :--- |
| **002202** | **金风科技** | **+327.62%** | +130.65% | 🚀 **显著跑赢** (Alpha 显著) |
| **601615** | **明阳智能** | **+144.76%** | -13.01% | 🛡️ **逆势盈利** (避险能力强) |
| **000630** | **铜陵有色** | **+265.62%** | +152.13% | ✅ 跑赢大盘 |
| **603067** | **振华股份** | **+256.44%** | +220.86% | ✅ 小幅跑赢 |
| **000878** | **云南铜业** | +112.89% | +117.20% | ➖ 持平 |
| **000875** | **吉电股份** | +104.68% | +18.12% | ✅ 显著跑赢 |

**核心洞察：**
1.  **避险属性**: 在个股下跌趋势中（如明阳智能），情感因子能有效识别负面情绪或信息的真空期，提示策略空仓，从而避免了基准策略的大幅回撤。
2.  **趋势增强**: 在上涨趋势中，研报的密集发布往往是机构建仓的信号，策略通过情感因子加仓，放大了上涨收益。

---

## 5. 快速开始 (Quick Start)

### 环境准备
确保已安装 Python 3.8+ 及以下依赖：
```bash
pip install pandas akshare matplotlib
```

### 1. 数据更新 (Data Update)
下载最新的个股研报数据：
```bash
python etl/download_reports.py
```

### 2. 因子计算 (Factor Calculation)
处理文本数据，生成情感因子文件：
```bash
python etl/calc_report_sentiment.py
```

### 3. 运行回测 (Run Backtest)
执行本地回测脚本，生成净值曲线：
```bash
python run_strategy_local.py
```
结果图片将保存在 `backtest_results/` 目录下。

---

## 6. 未来展望 (Roadmap)

*   **LLM 深度赋能**: 引入 ChatGPT/Claude API 或本地部署 LLaMA 模型，对研报进行摘要提取和深层逻辑分析，不仅仅局限于情感打分。
*   **多模态数据**: 结合宏观经济数据、行业板块轮动数据，构建更立体的多因子模型。
*   **高频情绪**: 接入雪球、股吧等散户论坛数据，开发“反向指标”或“情绪过热”预警功能。
*   **实盘对接**: 将信号生成模块对接至交易柜台 (如 QMT/Ptrade)，实现自动化交易。
