from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from gmail_api import get_latest_email
from nlp_processing import process_email_content
import uvicorn

app = FastAPI()

# Enable CORS to allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all domains for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Email Processing API Running"}

@app.get("/process-email")
def process_email():
    email = get_latest_email()
    if not email:
        return {"error": "No emails found"}

    # Call NLP processing to analyze email
    processed_results = process_email_content(email["body"])

    return {
        "subject": email["subject"] or "No Subject",
        "from": email["from"] or "Unknown Sender",
        "body": email["body"] or "No Email Body Found",
        "sentiment": processed_results["sentiment"],
        "summary": processed_results["summary"],
        "reply": processed_results["reply"]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
