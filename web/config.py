import os
from dotenv import load_dotenv

class Config():
    load_dotenv()  
    SERAPI_KEY = os.getenv("SERPAPI_KEY")
    GOOGLE_LOCATION_API_KEY = os.getenv("GOOGLE_LOCATION_API_KEY")
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    DJANGO_SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")