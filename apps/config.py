import logging
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

from apps.web.mail_extract import EmailExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)    

class Config(BaseSettings):
    app_name: str = "email_bot"

    serpapi_key: str
    google_location_api_key: str

    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: str

    credentials_file: str = "settings/credentials.json"
    token_file: str = "settings/token.json"
    email_attachments_dir: str = "settings/email_attachments"

    rabbitmq_broker_url: str

    django_secret_key: str
    django_settings_module: str

    class Config:
        env_file = ".env"
        case_sensitive = False

config = Config()
email_extractor = EmailExtractor()
