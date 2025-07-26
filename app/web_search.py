import json
import requests
from config import Config
from serpapi.google_search import GoogleSearch
from typing import Self
import requests
import json
import geocoder
import time

class SearchQuery:
    def __init__(self, language: str, country: str, location: str):
        self.language = language
        self.country = country
        self.location = location

    def set_query(self, query: str) -> Self:
        self.query = query
        return self

    @property
    def params(self) -> dict:
            params = {
                "q": self.query,
                "location": self.location,
                "hl": self.language,
                "gl": self.country,
                "google_domain": "google.com",
                "api_key": Config.API_KEY
            }
            return params

    def search(self) -> dict:
        return GoogleSearch(self.params).get_dict()
    

if __name__ == "__main__":
    query = SearchQuery(language="pl", country="pl", location="Lublin")
    print(query.set_query("firma programistyczna").search())


class LocationSearch:
    def __init__(self, location: str = "Polska", query: str = ""):
        self.location = location
        self.query = query

    @property
    def coordinates(self) -> dict:
        return self.coordinates_from_address(self.location)

    
    def coordinates_from_address(self, address: str) -> dict:
        g = geocoder.arcgis(address)
        if g.ok:
            return {
                "latitude": g.latlng[0],
                "longitude": g.latlng[1],
            }
        else:
            return {"error": address}

    def search_places(self) -> dict:
        url = 'https://places.googleapis.com/v1/places:searchText'
        
        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': Config.GOOGLE_location_API_KEY,
            'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.websiteUri,places.nationalPhoneNumber,places.businessStatus'
        }
        
        data = {
            "textQuery": f"{self.query} in {self.location}",
            "languageCode": "pl",
            "regionCode": "PL",
            "maxResultCount": 1000,
            "locationBias": {
                "circle": {
                    "center": {
                        "latitude": self.coordinates["latitude"],
                        "longitude": self.coordinates["longitude"]
                    },
                    "radius": 50000.0
                }
            }
        }
        
        response = requests.post(url, json=data, headers=headers)
        return response.json()

    def save(self, results: dict) -> None:
        with open("location_search_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    location_search = LocationSearch(location="Lublin", query="firmy informatyczne")
    results = location_search.search_places()
    location_search.save(results)

