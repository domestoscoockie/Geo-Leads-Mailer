import requests
import re


class EmailExtractor:

    def fetch_data(self, url: str) -> str:
        try:
            response = requests.request('GET', url)
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching data from {url}: {e}")
            return ""

    def extract_mail(self, data):
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        return list(set(re.findall(email_pattern, data)))

    def extract_phone(self, data):
        phone_pattern = r'\+?\d[\d -]{8,}\d'
        return list(set(re.findall(phone_pattern, data)))


