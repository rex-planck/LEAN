import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import pandas as pd
import os
import glob
from tqdm import tqdm

# 复用 calc_sentiment.py 中的模型加载逻辑，但改为处理 reports 目录
# 并且针对研报标题进行打分

def load_sentiment_model():
    # 依然使用 Erlangshen
    device = torch.device("cpu")
    model_name = "IDEA-CCNL/Erlangshen-Roberta-110M-Sentiment"
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name).to(device)
        return tokenizer, model, device
    except:
        return None, None, None

def calc_score(text, tokenizer, model, device):
    if not tokenizer: return 0.0
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128).to(device)
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        # 1: Positive, 0: Negative
        return probs[0][1].item() - probs[0][0].item()

def process_report_sentiment():
    report_dir = "data/alternative/reports"
    save_dir = "data/alternative/sentiment_reports" # 区分新闻情感
    os.makedirs(save_dir, exist_ok=True)
    
    tokenizer, model, device = load_sentiment_model()
    if not tokenizer:
        print("模型加载失败")
        return

    files = glob.glob(os.path.join(report_dir, "*.csv"))
    for file in files:
        stock_code = os.path.basename(file).split('_')[0]
        print(f"正在处理 {stock_code} 研报情感...")
        
        df = pd.read_csv(file)
        if df.empty: continue
        
        scores = []
        # 处理所有研报
        for index, row in tqdm(df.iterrows(), total=len(df)):
            # 研报标题通常在 '报告名称' (AKShare default) 或 'title' 列
            text = str(row.get('报告名称', row.get('title', '')))
            
            # 研报标题通常包含 "买入", "增持", "超预期" 等强情感词
            score = calc_score(text, tokenizer, model, device)
            scores.append(score)
            
        df['sentiment_score'] = scores
        
        save_path = os.path.join(save_dir, f"{stock_code}_report_sentiment.csv")
        df.to_csv(save_path, index=False)
        print(f"已保存: {save_path}")

if __name__ == "__main__":
    process_report_sentiment()
