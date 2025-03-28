from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import base64
import os
import pickle
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def authenticate_gmail():
    creds = None
    if os.path.exists("token.pkl"):
        with open("token.pkl", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.pkl", "wb") as token:
            pickle.dump(creds, token)

    return build("gmail", "v1", credentials=creds)

def get_latest_email():
    service = authenticate_gmail()

    try:
        results = service.users().messages().list(userId="me", maxResults=5, labelIds=["INBOX"]).execute()
        messages = results.get("messages", [])

        if not messages:
            return None

        latest_email = None
        latest_timestamp = 0

        for msg in messages:
            email_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
            timestamp = int(email_data["internalDate"])  

            if timestamp > latest_timestamp:
                latest_timestamp = timestamp
                latest_email = email_data

        if not latest_email:
            return None

        email_headers = latest_email["payload"]["headers"]
        subject = next((header["value"] for header in email_headers if header["name"] == "Subject"), "No Subject")
        sender = next((header["value"] for header in email_headers if header["name"] == "From"), "Unknown Sender")

        email_body = "No text content available."
        if "parts" in latest_email["payload"]:
            for part in latest_email["payload"]["parts"]:
                if part["mimeType"] == "text/plain":
                    email_body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")

        return {
            "subject": subject,
            "from": sender,
            "body": email_body
        }
    except Exception as e:
        print("Error fetching email:", e)
        return None
