# NLP-Enhanced Multi-Factor Strategy
[中文](./README.md)

![Backtest Result](backtest_results/002202_backtest.png)

## 1. Project Overview

This project aims to build a quantitative trading system based on **NLP (Natural Language Processing)** technology. By scraping unstructured text data such as financial research reports and news, and using pre-trained deep learning models to analyze market sentiment, it generates a **Sentiment Factor**. This factor is then combined with traditional technical indicators to construct a multi-factor stock selection strategy.

**Core Logic:**
1.  **Data Acquisition**: Use the AKShare interface to scrape research report summaries and news for A-share stocks.
2.  **Sentiment Calculation**: Use FinBERT or sentiment dictionary models to score each text (Positive/Negative/Neutral).
3.  **Strategy Construction**: Use the sentiment score as an Alpha factor, combining it with Moving Average (MA) trends for timing trades.
4.  **Backtest Validation**: Verify strategy effectiveness on historical data and evaluate excess returns.

---

## 2. Technical Architecture

### 2.1 Data Flow (ETL Pipeline)
*   **Data Source**: AKShare (East Money interface `stock_research_report_em`)
*   **Raw Data**: Stored in `data/alternative/reports/` (CSV format)
*   **Processing**: `etl/calc_report_sentiment.py` reads reports and calculates sentiment scores.
*   **Features**: Generates datasets with `sentiment_score`, stored in `data/alternative/sentiment_reports/`.

### 2.2 Core Models
*   **NLP Model**: Uses simple rule-based/dictionary sentiment analysis (current stage), or HuggingFace Transformers (advanced).
    *   *Current Implementation*: Keyword-based sentiment scoring algorithm (Mock/Rule-based).
*   **Strategy Model**: 
    *   **Signal 1**: Research report sentiment score > 0.8 (Strongly Positive) -> Strong Buy.
    *   **Signal 2**: Technical Golden Cross (MA5 > MA20) & Sentiment score is not negative -> Trend Following Buy.
    *   **Signal 3**: Sentiment score < -0.2 or Technical Death Cross -> Sell/Stop Loss.
    *   **Decay**: Sentiment signal decays over time (10% decay per day) to simulate the market's digestion of information.

---

## 3. Project Structure

```bash
├── data/
│   ├── equity/daily/       # Stock daily market data (OHLCV)
│   └── alternative/
│       ├── reports/        # Raw research report data
│       └── sentiment_reports/ # Research report data with sentiment scores
├── etl/
│   ├── download_reports.py # Script to download reports
│   └── calc_report_sentiment.py # Script to calculate sentiment scores
├── SentimentAlphaStrategy/
│   └── main.py             # LEAN engine strategy file (C#/Python)
├── run_strategy_local.py   # Local lightweight backtest script (Python)
└── backtest_results/       # Backtest result charts
```

---

## 4. Backtest Analysis

We backtested the following 6 targets (2023-02 to 2026-01):
*   **Goldwind Science (002202)**: Strategy Return **327.62%** vs Benchmark 130.65% (Significantly Outperformed)
*   **Mingyang Smart Energy (601615)**: Strategy Return **144.76%** vs Benchmark -13.01% (Profitable against trend)
*   **Tongling Nonferrous (000630)**: Strategy Return **265.62%** vs Benchmark 152.13%
*   **Yunnan Copper (000878)**: Strategy Return 112.89% vs Benchmark 117.20% (Neutral)
*   **Jilin Electric Power (000875)**: Strategy Return 104.68% vs Benchmark 18.12%
*   **Zhenhua (603067)**: Strategy Return 256.44% vs Benchmark 220.86%

**Conclusions:**
1.  **Effectiveness of Sentiment Factor**: In most targets, introducing the sentiment factor significantly enhanced returns. Especially during market downturns or volatility (e.g., 601615), the sentiment factor provided timely risk warnings (negative reports or lack of positive reports), helping the strategy to hold cash and avoid risks.
2.  **Sources of Excess Return**: 
    *   **Timeliness**: The release of research reports often implies increased institutional attention, leading to inertial price increases.
    *   **Noise Filtering**: Combining with technical trends filters out short-term fluctuations driven purely by sentiment, betting only when trend and sentiment resonate.

---

## 5. Quick Start

### Prerequisites
```bash
pip install pandas akshare matplotlib
```

### 1. Download Data
```bash
python etl/download_reports.py
```
This will generate the latest research report data in `data/alternative/reports/`.

### 2. Calculate Sentiment Scores
```bash
python etl/calc_report_sentiment.py
```
Reads reports, generates sentiment scores, and saves to `data/alternative/sentiment_reports/`.

### 3. Run Local Backtest
```bash
python run_strategy_local.py
```
The script will read local data, simulate trading logic, and generate equity curve charts in the `backtest_results/` directory.

---

## 6. Future Improvements
*   **LLM Integration**: Use BERT/ChatGPT for deeper semantic understanding of report content, rather than simple keyword matching.
*   **Multi-Source Data**: Add news and social media (Xueqiu/Guba) data to capture retail sentiment.
*   **Factor Optimization**: Research the half-life of sentiment scores and optimize signal decay logic.
