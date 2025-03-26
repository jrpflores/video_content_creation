import os
import base64
import pickle  # Save token
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

class GmailOAuthSender:
    def __init__(self, credentials_file, token_file="token.pickle"):
        """Initialize Gmail API with OAuth 2.0, using saved tokens."""
        self.scopes = ["https://www.googleapis.com/auth/gmail.send"]
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = self.authenticate_gmail()

    def authenticate_gmail(self):
        """Authenticate and get Gmail API service without opening a browser every time."""
        creds = None

        # Load saved credentials if they exist
        if os.path.exists(self.token_file):
            with open(self.token_file, "rb") as token:
                creds = pickle.load(token)

        # If credentials are invalid, refresh them
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())  # Refresh token without browser
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, self.scopes)
                creds = flow.run_local_server(port=0)  # First time only

            # Save the new credentials
            with open(self.token_file, "wb") as token:
                pickle.dump(creds, token)

        return build("gmail", "v1", credentials=creds)

    def send_email(self, sender_email, recipient_email, subject, body):
        """Send an email using Gmail API."""
        if not self.service:
            print("❌ Gmail API service is not available.")
            return

        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        message_data = {"raw": raw_message}

        try:
            self.service.users().messages().send(userId="me", body=message_data).execute()
            print("✅ Email sent successfully!")
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
