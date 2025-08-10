import os.path
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from apps.config import logger
 

SCOPES = ["https://mail.google.com/"]


TITLE = 'Test Email'
MSG = 'Hello, this is a test email message.'
ATTACHMENTS = ''

class MailSend:
  def __init__(self):
    self.creds = None
    if os.path.exists("token.json"):
      self.creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not self.creds or not self.creds.valid:
      if self.creds and self.creds.expired and self.creds.refresh_token:
        self.creds.refresh(Request())
      else:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES
        )
        self.creds = flow.run_local_server(port=0)

      with open("token.json", "w") as token:
        token.write(self.creds.to_json())
    self.service = build("gmail", "v1", credentials=self.creds)



  def create_message(self, sender: str, to: str, subject: str, message_text: str, attachments: list = None) -> dict:
    # Create a multipart message for attachments
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    message['Reply-To'] = sender

    # Attach the plain text message
    part1 = MIMEText(message_text, 'plain')
    message.attach(part1)

    # Attach files if provided
    if attachments:
      for file_path in attachments:
        if not os.path.isfile(file_path):
          continue  # Skip if file does not exist
        with open(file_path, 'rb') as f:
          part = MIMEBase('application', 'octet-stream')
          part.set_payload(f.read())
          encoders.encode_base64(part)
          part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(file_path)}"')
          message.attach(part)

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}




  def send(self, userId: str, title: str, msg: str, attachments: list = None) -> dict:
    message = self.create_message('karol.grabowski852@gmail.com', userId, title, msg, attachments)

    self.service.users().messages().send(
      userId=userId,
      body=message
    ).execute()
      
    logger.info("Email sent successfully.")

    return {
      "status": "200",
      "message": "Email sent successfully."
    }

