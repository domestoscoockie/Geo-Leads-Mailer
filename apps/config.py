import logging
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

from apps.web.mail_extract import EmailExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)    

class Config(BaseSettings):

    serpapi_key: str
    google_location_api_key: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: str

    django_secret_key: str

    class Config:
        env_file = ".env"
        case_sensitive = False

config = Config()
email_extractor = EmailExtractor()
