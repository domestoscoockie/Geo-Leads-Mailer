import os
from dotenv import load_dotenv

class Config():
    load_dotenv()  
    API_KEY = os.getenv("SERPAPI_KEY")
    GOOGLE_location_API_KEY = os.getenv("GOOGLE_location_API_KEY")