"""
Helper functions for the website
"""
import os
from concurrent.futures import ThreadPoolExecutor
import requests
from dto.Attractions import *
from helpers.PostCodeHelpers import parse_postcode

BASE_URL = "https://api.tfl.gov.uk/Journey/JourneyResults/"
API = BASE_URL + "{postcode_start}/to/{postcode_end}?api_key={api_key}"


def tfl_journey(start, end):
    key = os.environ.get("WHERE2TFL_KEY")
    parsed_start = parse_postcode(start)
    parsed_end = parse_postcode(end)
    url = API.format(postcode_start=parsed_start, postcode_end=parsed_end,
                     api_key=key)
    resp = requests.get(url)
    return resp.json()


def retrieve_tfl_journey(start: str, end: str) -> JourneyInfo:
    """
    Does the API call for the TFL Journey and
    returns a JourneyInfo Class Object
    """
    data = tfl_journey(start, end)
    return JourneyInfo.from_dict(data)


def get_tfl_journey(start, attraction):
    response = requests.get(
        "https://api.tfl.gov.uk/journey/journeyresults/"
        + start
        + "/to/"
        + parse_postcode(attraction[1])
    )

    if response.status_code == 200:
        data = response.json()["journeys"][0]
        cur_route = {"id": attraction[2],
                     "name": attraction[0],
                     "duration": data["duration"],
                     'response_code': response.status_code}
    else:
        cur_route = {'response_code': response.status_code}
    return cur_route


def parallel_tfl_requests(start, attractions):
    with ThreadPoolExecutor() as executor:
        # Parallelize the API requests
        attraction_results = list(
            executor.map(lambda x: get_tfl_journey(start, x), attractions))

    return attraction_results



# print(retrieve_tfl_journey("EC4R9HA","SW72BX"))
