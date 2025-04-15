from transformers import AutoModelForSequenceClassification, AutoModelForSeq2SeqLM, AutoTokenizer
import torch

# Model names
SENTIMENT_MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment"  # Updated Sentiment Model
SUMMARIZATION_MODEL_NAME = "facebook/bart-large-cnn"
REPLY_GENERATION_MODEL_NAME = "google/flan-t5-large"

# Load models with correct architecture
def load_sentiment_model():
    model = AutoModelForSequenceClassification.from_pretrained(SENTIMENT_MODEL_NAME)
    tokenizer = AutoTokenizer.from_pretrained(SENTIMENT_MODEL_NAME)
    return model, tokenizer

def load_summarization_model():
    model = AutoModelForSeq2SeqLM.from_pretrained(SUMMARIZATION_MODEL_NAME)
    tokenizer = AutoTokenizer.from_pretrained(SUMMARIZATION_MODEL_NAME)
    return model, tokenizer

def load_reply_model():
    model = AutoModelForSeq2SeqLM.from_pretrained(REPLY_GENERATION_MODEL_NAME)
    tokenizer = AutoTokenizer.from_pretrained(REPLY_GENERATION_MODEL_NAME)
    return model, tokenizer

# Load all models
sentiment_model, sentiment_tokenizer = load_sentiment_model()
summarization_model, summarization_tokenizer = load_summarization_model()
reply_model, reply_tokenizer = load_reply_model()

# Sentiment Analysis
def analyze_sentiment(text):
    inputs = sentiment_tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    outputs = sentiment_model(**inputs)
    
    # Log the raw logits to see the distribution (useful for debugging)
    print(outputs.logits)

    label = outputs.logits.argmax().item()

    # Map label to human-readable sentiment
    sentiment_labels = {0: "Negative", 1: "Neutral", 2: "Positive"}
    return {"label": sentiment_labels.get(label, "Unknown"), "score": float(outputs.logits.softmax(dim=1).max())}

# Summarization
def summarize_text(text):
    inputs = summarization_tokenizer(text, return_tensors="pt", truncation=True, max_length=1024)
    summary_ids = summarization_model.generate(**inputs, max_length=100, min_length=30, num_beams=5)
    return summarization_tokenizer.decode(summary_ids[0], skip_special_tokens=True)

# Reply Generation
def generate_reply(email_body):
    prompt = (
        "You are a professional email assistant. Your task is to respond to the email politely and appropriately.\n\n"
        f"Email Content:\n{email_body}\n\n"
        "Reply professionally with specific feedback, acknowledge the person's intent, sentiment."
        "Make sure the reply is personalized, encouraging, and relevant to the context."
    )

    inputs = reply_tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
    reply_ids = reply_model.generate(
        **inputs, 
        max_length=200, 
        min_length=50, 
        num_beams=5,  # Controlled responses with beams
        do_sample=True,  # Enable sampling for diversity
        temperature=0.3,  # Low temperature for focus
        top_p=0.9  # High top-p for diversity in word choice
    )

    return reply_tokenizer.decode(reply_ids[0], skip_special_tokens=True)

# Process Email Content
def process_email_content(email_body):
    return {
        "sentiment": analyze_sentiment(email_body),
        "summary": summarize_text(email_body),
        "reply": generate_reply(email_body)
    }
