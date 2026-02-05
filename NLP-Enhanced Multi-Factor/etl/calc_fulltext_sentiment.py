import pdfplumber
import requests
import pandas as pd
import os
import io
import time
from transformers import pipeline

def download_and_analyze_pdf(url):
    """
    下载 PDF 并提取前 2 页文本
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return ""
        
        with pdfplumber.open(io.BytesIO(response.content)) as pdf:
            text = ""
            # 只读前 2 页，通常包含核心摘要
            pages_to_read = min(2, len(pdf.pages))
            for i in range(pages_to_read):
                page_text = pdf.pages[i].extract_text()
                if page_text:
                    text += page_text + "\n"
            return text
    except Exception as e:
        print(f"Error parsing PDF {url}: {e}")
        return ""

def process_full_text_sentiment():
    print("加载 NLP 模型 (Erlangshen-Roberta)...")
    sentiment_pipeline = pipeline("sentiment-analysis", model="IDEA-CCNL/Erlangshen-Roberta-110M-Sentiment")
    
    report_dir = "data/alternative/reports"
    sentiment_dir = "data/alternative/sentiment_fulltext"
    os.makedirs(sentiment_dir, exist_ok=True)
    
    # 获取所有研报 CSV
    csv_files = [f for f in os.listdir(report_dir) if f.endswith("_reports.csv")]
    
    for csv_file in csv_files:
        stock_code = csv_file.split("_")[0]
        print(f"正在处理 {stock_code} 的研报全文...")
        
        df = pd.read_csv(os.path.join(report_dir, csv_file))
        
        # 为了演示，每只股票只取最近 10 条有 PDF 链接的研报
        # 否则下载几百个 PDF 会非常慢
        if '报告PDF链接' not in df.columns:
            print(f"  {csv_file} 缺少 PDF 链接列，跳过")
            continue
            
        df_target = df.head(10).copy() 
        
        results = []
        
        for index, row in df_target.iterrows():
            pdf_url = row['报告PDF链接']
            title = row['报告名称']
            date = row['日期']
            
            if pd.isna(pdf_url):
                continue
                
            print(f"  分析: {title[:20]}... ({date})")
            
            # 1. 提取全文
            full_text = download_and_analyze_pdf(pdf_url)
            
            if not full_text:
                print("    PDF 下载/解析失败")
                continue
                
            # 2. 截取部分文本进行分析 (模型有长度限制，通常 512 tokens)
            # 我们取前 400 个字符作为摘要
            summary_text = full_text[:400]
            
            # 3. 情感打分
            try:
                result = sentiment_pipeline(summary_text)[0]
                label = result['label'] # Positive / Negative
                score = result['score']
                
                # 映射分数: Positive -> 1, Negative -> -1
                final_score = score if label == 'Positive' else -score
                
                results.append({
                    'date': date,
                    'title': title,
                    'sentiment_score': final_score,
                    'summary': summary_text[:50] + "..."
                })
                print(f"    -> Score: {final_score:.4f}")
                
            except Exception as e:
                print(f"    NLP Error: {e}")
                
            # 礼貌延时
            time.sleep(1)
            
        # 保存结果
        if results:
            df_res = pd.DataFrame(results)
            save_path = os.path.join(sentiment_dir, f"{stock_code}_fulltext_sentiment.csv")
            df_res.to_csv(save_path, index=False)
            print(f"  已保存全文情感: {save_path}")

if __name__ == "__main__":
    process_full_text_sentiment()
