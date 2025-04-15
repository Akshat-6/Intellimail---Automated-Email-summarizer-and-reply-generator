import streamlit as st
import requests

def fetch_email():
    response = requests.get("http://127.0.0.1:8000/process-email")
    if response.status_code == 200:
        return response.json()
    return None

def main():
    st.title("📧 Inteli-Mail: Smart Email Assistant")
    
    if st.button("Fetch Latest Email"):
        email_data = fetch_email()
        
        if email_data:
            st.subheader("📨 Email Details")
            st.write(f"**Subject:** {email_data['subject']}")
            st.write(f"**From:** {email_data['from']}")
            st.write("**Body:**")
            st.text_area("Email Content", email_data['body'], height=200)

            st.subheader("🧠 Processed Results")
            st.write(f"**Sentiment:** {email_data['sentiment']['label']} (Score: {email_data['sentiment']['score']:.2f})")
            st.write("**Summary:**")
            st.text_area("Email Summary", email_data['summary'], height=100)
            st.write("**Suggested Reply:**")
            st.text_area("AI-Generated Reply", email_data['reply'], height=100)
        else:
            st.error("No emails found or error fetching email.")

if __name__ == "__main__":
    main()
