# NLP-Enhanced Multi-Factor Strategy

[中文](./README.md)

![Backtest Result](backtest_results/002202_backtest.png)
*(Chart: Equity curve of Goldwind Science 002202, showing significant outperformance against the benchmark)*

## 1. Project Overview

This project aims to build a cutting-edge **Quantitative Trading System based on NLP (Natural Language Processing)** technology. By automatically scraping unstructured text data from the financial market (such as stock research reports and news) and using deep learning models or sentiment dictionaries to analyze market sentiment, it generates a tradable **Sentiment Factor**. This factor is combined with traditional technical indicators (such as Moving Averages) to construct a robust multi-factor stock selection strategy, aiming to capture excess returns driven by changes in institutional sentiment.

**Core Logic:**
1.  **Multi-Source Data Acquisition (Data ETL)**: Use the `AKShare` interface to scrape A-share stock research report summaries, announcements, and news in real-time.
2.  **Sentiment Quantification (Sentiment Analysis)**: Use FinBERT models or financial sentiment dictionaries to score each research report (Positive/Negative/Neutral), converting unstructured text into structured `sentiment_score`.
3.  **Multi-Factor Strategy Construction (Factor Combinations)**:
    *   **Alpha Factor**: Research report sentiment score (reflecting institutional bullish/bearish attitude).
    *   **Beta Factor**: Trend confirmation via Moving Averages (MA5/MA20 Golden Cross/Death Cross).
    *   **Risk Control**: Dynamic position management based on sentiment scores.
4.  **Backtesting & Validation**: Validate strategy effectiveness on historical data using the LEAN engine or local Python scripts, evaluating annualized returns, maximum drawdown, and Sharpe ratio.

---

## 2. Technical Architecture & Workflow

### 2.1 Data Pipeline (ETL)
*   **Data Source**:
    *   Research Reports: AKShare `stock_research_report_em` (East Money)
    *   News Data: AKShare `stock_news_em` (Optional)
*   **Raw Data Storage**: Raw data is stored in CSV format in `data/alternative/reports/`.
*   **Feature Engineering**: The `etl/calc_report_sentiment.py` script reads raw reports, performs cleaning, tokenization, and sentiment scoring.
*   **Processed Data**: Generates time-series data with `sentiment_score`, stored in `data/alternative/sentiment_reports/`, ready for direct consumption by the strategy engine.

### 2.2 Core Models
*   **NLP Model**:
    *   *Current Implementation*: Rule-based/Dictionary scoring model based on specific financial keywords (e.g., "Buy", "Overweight", "Exceeds Expectations" vs "Downgrade", "Risk").
    *   *Future Upgrade*: Plan to integrate HuggingFace Transformers (FinBERT) for more precise contextual semantic analysis.
*   **Trading Strategy**:
    *   **Buy Signal**: New report published today AND Sentiment Score > 0.8 (Strongly Positive) AND Price above Moving Averages.
    *   **Sell Signal**: Sentiment Score < -0.2 (Negative/Below Expectations) OR Technical Death Cross.
    *   **Signal Decay**: Sentiment signal decays linearly over time (10% daily decay) to simulate the market's gradual digestion of information.

---

## 3. Project Structure

```bash
├── data/
│   ├── equity/daily/          # Stock Daily Market Data (OHLCV)
│   └── alternative/
│       ├── reports/           # Raw Research Report Data
│       └── sentiment_reports/ # Processed Reports with Sentiment Scores
├── etl/
│   ├── download_reports.py    # Data Download Script (AKShare -> Local)
│   └── calc_report_sentiment.py # Sentiment Calculation Script (Text -> Sentiment Score)
├── SentimentAlphaStrategy/
│   └── main.py                # LEAN Engine Strategy Main File (C#/Python Adapter)
├── run_strategy_local.py      # Local Lightweight Backtest Engine (Python, Pandas-based)
├── backtest_results/          # Backtest Result Charts and Logs
└── README.md                  # Project Documentation
```

---

## 4. Performance

We backtested the following representative targets (Period: Feb 2023 - Jan 2026), and the results show that the strategy possesses significant excess return capabilities in most cases:

| Ticker | Name | Strategy Return | Benchmark (Buy&Hold) | Evaluation |
| :--- | :--- | :--- | :--- | :--- |
| **002202** | **Goldwind Science** | **+327.62%** | +130.65% | 🚀 **Significant Alpha** |
| **601615** | **Mingyang Smart** | **+144.76%** | -13.01% | 🛡️ **Profitable Against Trend** |
| **000630** | **Tongling Nonferrous**| **+265.62%** | +152.13% | ✅ Outperformed Market |
| **603067** | **Zhenhua** | **+256.44%** | +220.86% | ✅ Slight Outperformance |
| **000878** | **Yunnan Copper** | +112.89% | +117.20% | ➖ Neutral |
| **000875** | **Jilin Electric** | +104.68% | +18.12% | ✅ Significant Outperformance |

**Core Insights:**
1.  **Risk Avoidance**: In downtrends (e.g., Mingyang Smart), the sentiment factor effectively identifies negative sentiment or information vacuums, prompting the strategy to hold cash, thus avoiding significant drawdowns seen in the benchmark.
2.  **Trend Enhancement**: In uptrends, frequent report publications often signal institutional accumulation. The strategy leverages sentiment factors to increase positions, amplifying upside returns.

---

## 5. Quick Start

### Prerequisites
Ensure Python 3.8+ is installed along with the following dependencies:
```bash
pip install pandas akshare matplotlib
```

### 1. Data Update
Download the latest stock research report data:
```bash
python etl/download_reports.py
```

### 2. Factor Calculation
Process text data and generate sentiment factor files:
```bash
python etl/calc_report_sentiment.py
```

### 3. Run Backtest
Execute the local backtest script to generate equity curves:
```bash
python run_strategy_local.py
```
Result images will be saved in the `backtest_results/` directory.

---

## 6. Roadmap

*   **Deep LLM Integration**: Integrate ChatGPT/Claude API or deploy local LLaMA models for report summarization and deep logical analysis, moving beyond simple sentiment scoring.
*   **Multi-Modal Data**: Combine macroeconomic data and industry rotation data to build a more multi-dimensional multi-factor model.
*   **High-Frequency Sentiment**: Integrate retail forum data (e.g., Xueqiu, Guba) to develop "Contrarian Indicators" or "Sentiment Overheating" alerts.
*   **Live Trading**: Connect signal generation modules to trading counters (e.g., QMT/Ptrade) for automated trading execution.
