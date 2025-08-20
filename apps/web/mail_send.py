import os.path
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from django.core.files.base import ContentFile
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from apps.admin_app.models import User
from apps.config import  config, logger
from django.core.files.base import ContentFile
from django.conf import settings

import uuid

SCOPES = ["https://mail.google.com/"]



class MailSend:
  def __init__(self, username: str):
    
    self.user = User.objects.get(username=username)
    self.creds = None
    if self.user.token and self.user.token.name and os.path.exists(self.user.token.path):
      self.creds = Credentials.from_authorized_user_file(self.user.token.path, SCOPES)

    if not self.creds or not self.creds.valid:
      if self.creds and self.creds.expired and self.creds.refresh_token:
        self.creds.refresh(Request())
      else:
        flow = InstalledAppFlow.from_client_secrets_file(
            self.user.credentials.path, SCOPES
        )
        self.creds = flow.run_local_server(port=0)
      self._save_token()

    self.service = build("gmail", "v1", credentials=self.creds)

  def _save_token(self):
      token_json = self.creds.to_json()

      old_name = self.user.token.name if self.user.token and self.user.token.name else None
      filename = f"token_{uuid.uuid4().hex}.json"
      self.user.token.save(filename, ContentFile(token_json), save=True)

      if old_name and old_name != self.user.token.name:
        try:
          old_path = os.path.join(settings.MEDIA_ROOT, old_name)
          if os.path.exists(old_path):
            os.remove(old_path)
        except OSError:
          logger.warning(f"Failed to remove old token file {old_name}. It may not exist or is in use.")


  def create_message(self, sender: str, to: str, subject: str, message_text: str, attachments: list = None) -> dict:
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    message['Reply-To'] = sender

    part1 = MIMEText(message_text, 'plain')
    message.attach(part1)

    if attachments:
      for file_path in attachments:
        if not os.path.isfile(file_path):
          continue  
        
        with open(file_path, 'rb') as f:
          part = MIMEBase('application', 'octet-stream')
          part.set_payload(f.read())
          encoders.encode_base64(part)
          part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(file_path)}"')
          message.attach(part)

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}


  def send(self, to: str, subject: str, text: str, attachments: list = None, sender_email: str | None = None) -> dict:

    sender_email = sender_email or 'me'

    message = self.create_message(sender_email, to, subject, text, attachments)

    self.service.users().messages().send(
      userId='me',
      body=message
    ).execute()

    return {"status": "200", "message": "Email sent successfully."}


