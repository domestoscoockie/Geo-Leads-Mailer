import requests
import re
from pydantic import BaseModel 


class Organization(BaseModel):
    name: str
    website: str
    emails: list[str] = []
    phones: list[str] = []


class EmailExtractor:
    def __init__(self, url: str):
        self.url = url

    def fetch_data(self):
        response = requests.request('GET', self.url)
        return response.text

    def extract_mail(self, data):
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        return re.findall(email_pattern, data)
    
    def extract_phone(self, data):
        phone_pattern = r'\+?\d[\d -]{8,}\d'
        return re.findall(phone_pattern, data)

    @staticmethod
    def create_organization(name: str, url: str, emails: list[str], phones: list[str]) -> Organization:
        return Organization(name=name, website=url, emails=emails, phones=phones)



if __name__ == "__main__":
    url = "https://sqlsoft.pl/"
    extractor = EmailExtractor(url=url)
    organization = extractor.create_organization(name="SQLSoft", url=url,
                    emails=extractor.extract_mail(extractor.fetch_data()),
                    phones=extractor.extract_phone(extractor.fetch_data()))
    print(organization)
