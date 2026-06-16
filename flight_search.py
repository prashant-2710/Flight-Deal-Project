import os
import requests
from dotenv import load_dotenv

load_dotenv()

serpapi_endpoint = os.environ["SERPAPI_ENDPOINT"]


class FlightSearch:
    
    def __init__(self):
        self._api_key = os.environ["SERPAPI_API_KEY"]

    def check_flights(self, origin_city_code, destination_city_code, outbound_date, return_date, is_direct = True):
        stops_params = "0" if is_direct else "1"

        query_params = {
            "engine": "google_flights",
            "departure_id": origin_city_code,
            "arrival_id": destination_city_code,
            "outbound_date": outbound_date,
            "return_date": return_date,
            "type": "1",
            "adults": "1",
            "currency": "GBP",
            "stops": stops_params,
            "api_key": self._api_key,
        }

        response = requests.get(url=serpapi_endpoint, params=query_params)
        
        if response.status_code != 200:
            print(f"check_flights() response code: {response.status_code}")
            return None

        data = response.json()
        if "error" in data:
            print(f"API error: {data['error']}")
            return None
        return data
        