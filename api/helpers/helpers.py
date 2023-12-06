"""
Helper functions for the website
"""
import os
import psycopg as db
import requests
from dataclasses import dataclass
from geopy.geocoders import Nominatim

BASE_URL = "https://api.tfl.gov.uk/Journey/JourneyResults/"
API = BASE_URL + "{postcode_start}/to/{postcode_end}?api_key={api_key}"


def parse_postcode(postcode):
    assert isinstance(postcode, str)
    parsed_postcode = postcode.replace(" ", "")
    if parsed_postcode.isalnum():
        return parsed_postcode
    else:
        return None


def tfl_journey(start, end):
    key = os.environ.get("WHERE2TFL_KEY")
    parsed_start = parse_postcode(start)
    parsed_end = parse_postcode(end)
    url = API.format(postcode_start=parsed_start, postcode_end=parsed_end, api_key=key)
    resp = requests.get(url)
    return resp.json()


def postcode_to_coordinates(postcode):
    geolocator = Nominatim(user_agent="your_app_name")
    location = geolocator.geocode(postcode)
    
    if location:
        #latitude, longitude = location.latitude, location.longitude
        return location.latitude, location.longitude
    else:
        return None


@dataclass
class JourneyLegInfo:
    duration: float
    instruction: str


@dataclass
class JourneyInfo:
    duration: float
    legs: list

    @classmethod
    def from_dict(cls, data: dict) -> "JourneyInfo":
        return cls(
            duration=data["journeys"][0]["duration"],
            legs=[
                JourneyLegInfo(leg["duration"], leg["instruction"]["summary"])
                for leg in data["journeys"][0]["legs"]
            ],
        )


def retrieve_tfl_journey(start: str, end: str) -> JourneyInfo:
    """
    Does the API call for the TFL Journey and returns a JourneyInfo Class Object
    """
    data = tfl_journey(start, end)
    return JourneyInfo.from_dict(data)


if __name__=="__main__":
    print(postcode_to_coordinates("SW81XR"))


# print(retrieve_tfl_journey("EC4R9HA","SW72BX"))
