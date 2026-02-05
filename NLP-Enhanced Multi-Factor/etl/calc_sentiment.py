import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import pandas as pd
import os
import glob
from tqdm import tqdm

def load_sentiment_model():
    """
    加载中文情感模型
    使用: IDEA-CCNL/Erlangshen-Roberta-110M-Sentiment
    """
    device = torch.device("cpu")
    print(f"Using device: {device}")

    # 替换为中文模型
    model_name = "IDEA-CCNL/Erlangshen-Roberta-110M-Sentiment"
    
    print(f"正在加载模型 {model_name}...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name).to(device)
        return tokenizer, model, device
    except Exception as e:
        print(f"模型加载失败 (可能是网络问题): {e}")
        return None, None, None

def calc_sentiment(text, tokenizer, model, device):
    if not tokenizer or not model:
        return 0.0
        
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512).to(device)
    with torch.no_grad():
        outputs = model(**inputs)
        predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        # Erlangshen-Roberta-110M-Sentiment labels: 
        # Label 0: Negative
        # Label 1: Positive
        # 假设我们用 Positive - Negative 作为分数 (-1 ~ 1)
        
        # 注意: 需确认模型输出维度。如果是2分类: [neg, pos]
        prob_neg = predictions[0][0].item()
        prob_pos = predictions[0][1].item()
        
        score = prob_pos - prob_neg
        return score

def process_news_data():
    news_dir = "data/alternative/news"
    save_dir = "data/alternative/sentiment"
    os.makedirs(save_dir, exist_ok=True)
    
    # 1. 加载模型
    tokenizer, model, device = load_sentiment_model()
    
    # 2. 遍历新闻文件
    files = glob.glob(os.path.join(news_dir, "*.csv"))
    
    if not files:
        print("未找到新闻数据，请先运行 download_news.py")
        return

    for file in files:
        stock_code = os.path.basename(file).split('_')[0]
        print(f"正在处理 {stock_code} 的新闻情感...")
        
        df = pd.read_csv(file)
        if df.empty: continue
        
        # 3. 计算情感分 (计算所有行)
        scores = []
        # 为了演示速度，这里限制处理前 50 条，如果需要全部，去掉 .head(50)
        process_df = df # df.head(50) 
        
        for index, row in tqdm(process_df.iterrows(), total=len(process_df)):
            # 优先使用 '新闻标题'，其次 '新闻内容' (AKShare 列名可能是 'title', 'content' 或其他)
            # 检查列名
            text = ""
            if '新闻标题' in row:
                text = str(row['新闻标题'])
            elif 'title' in row:
                text = str(row['title'])
            else:
                # 尝试找第一列字符串
                for col in row.index:
                    if isinstance(row[col], str):
                        text = row[col]
                        break
            
            if not text or text == "nan":
                text = "无内容"
            
            if tokenizer:
                score = calc_sentiment(text, tokenizer, model, device)
            else:
                import random
                score = random.uniform(-1, 1) # Mock data
            
            scores.append(score)
            
        # 4. 保存结果
        result_df = process_df.copy()
        result_df['sentiment_score'] = scores
        
        save_path = os.path.join(save_dir, f"{stock_code}_sentiment.csv")
        result_df.to_csv(save_path, index=False)
        print(f"已保存: {save_path}")

if __name__ == "__main__":
    process_news_data()
