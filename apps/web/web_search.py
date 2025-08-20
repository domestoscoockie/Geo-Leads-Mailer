import json
import  httpx
from apps.config import config, logger
from typing import Self
import json
from abc import ABC, abstractmethod
from pydantic import BaseModel



class Rect(BaseModel):
    low: tuple[float, float]
    high: tuple[float, float]

class Query(ABC):
    def __init__(self, location: str, language="pl", country="PL"):
        self.location = location       
        self.language = language
        self.country = country

    @abstractmethod
    def search(self) -> dict:
        pass

    @abstractmethod
    def set_query(self, query: str) -> Self:
        pass


class LocationQuery(Query):
    def __init__(self, location: str = "Polska", language: str = "pl", country: str = "PL"):
        super().__init__(location=location, language=language, country=country)
        self.location = location

    def set_query(self, query: str) -> Self:
        self.query = query
        return self    


    def geometry(self):
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": self.location,
            "key": config.google_location_api_key
        }

        response = httpx.get(url, params=params)
        data = response.json()
        
        if data["results"]:
            bounds = data["results"][0]["geometry"]["bounds"]
            return {
                "northeast": bounds["northeast"],
                "southwest": bounds["southwest"]
            }
        return None

    def generate_rectangles(self, step_minutes=10.0) -> list[Rect]:

        bounds = self.geometry()
        if not bounds:
            return []
        
        step_deg = step_minutes / 60.0
        
        sw_lat = bounds["southwest"]["lat"]
        sw_lng = bounds["southwest"]["lng"] 
        ne_lat = bounds["northeast"]["lat"]
        ne_lng = bounds["northeast"]["lng"]
        
        rectangles = []
        
        lat = sw_lat
        while lat < ne_lat:
            lng = sw_lng
            while lng < ne_lng:
                high_lat = min(lat + step_deg, ne_lat)
                high_lng = min(lng + step_deg, ne_lng)
                
                rect = Rect(
                    low=(lat, lng),           # southwest corner
                    high=(high_lat, high_lng) # northeast corner
                )
                rectangles.append(rect)
                
                lng += step_deg
            lat += step_deg
        logger.info(f"Generated {len(rectangles)} rectangles with {step_minutes}' spacing")

        return rectangles

    def search(self, rectangles: list[Rect]) -> dict:
        unique_places = {}  
        for rect in rectangles:
            url = 'https://places.googleapis.com/v1/places:searchText'

            headers = {
                'Content-Type': 'application/json',
                'X-Goog-Api-Key': config.google_location_api_key,
                'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.websiteUri,places.nationalPhoneNumber,places.businessStatus,nextPageToken'
            }
        
            next_page_token = None
            max_pages = 20 

            for _ in range(max_pages):

                data = {    
                    "textQuery": f"{self.query} in {self.location}",
                    "languageCode": self.language,
                    "regionCode": self.country,
                    "maxResultCount": 20,
                    "locationBias": {
                        "rectangle": {
                            "low": {
                                "latitude": rect.low[0],
                                "longitude": rect.low[1]
                            },
                            "high": {
                                "latitude": rect.high[0],
                                "longitude": rect.high[1]
                            }
                        }
                    }
                }
                
                if next_page_token:
                    data["pageToken"] = next_page_token

                response = httpx.post(url, json=data, headers=headers)
                result = response.json()
                
                if "places" in result:
                    for place in result["places"]:
                        place_key = place.get("displayName", {}).get("text", "")
                        if place_key and place_key not in unique_places:
                            unique_places[place_key] = place
                
                next_page_token = result.get("nextPageToken")
                if not next_page_token:
                    break

        if len(unique_places) == 0:
            raise ValueError("No places found for the given query and location.")
        
        return {f'{self.location}-{self.query}' : unique_places}


    def save(self, results: dict) -> None:
        with open(f"results/{self.location}-{self.query}.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    location_search = LocationQuery(location="Lublin", language="pl", country="PL")
    
    bounds = location_search.geometry()
    logger.info("Bounds: %s", bounds)
    
    rectangles = location_search.generate_rectangles(step_minutes=6.0)
    
    location_search.set_query("sklep")
    results = location_search.search(rectangles)
    places_dict = results.get(location_search.location, {})

    location_search.save(results)

