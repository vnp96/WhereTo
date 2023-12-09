"""
Helper functions for the website
"""
import os
from concurrent.futures import ThreadPoolExecutor
import requests
from dto.Attractions import *
from helpers.PostCodeHelpers import parse_postcode
from dto.Attractions import AttractionDetails, RouteDetails

BASE_URL = "https://api.tfl.gov.uk/Journey/JourneyResults/"
API = BASE_URL + "{postcode_start}/to/{postcode_end}?api_key={api_key}"


def tfl_journey(start, end):
    api_key = os.environ.get("WHERE2TFL_KEY")
    url = API.format(postcode_start=start, postcode_end=end, api_key=api_key)
    resp = requests.get(url)
    return resp


def retrieve_tfl_journey(start: str, end: str) -> JourneyInfo:
    """
    Does the API call for the TFL Journey and
    returns a JourneyInfo Class Object
    """
    data = tfl_journey(start, end)
    return JourneyInfo.from_dict(data)


def get_tfl_journey(start, attraction):
    postcode_source = parse_postcode(start)
    postcode_dest = parse_postcode(attraction[1])
    response = tfl_journey(postcode_source, postcode_dest)
    print("TFL response from {} to {} : {}".format(
        postcode_source, postcode_dest, str(response.status_code)
    ))

    cur_route = {}
    if response.status_code == 200:
        try:
            cur_route = (AttractionDetails.from_api_data(attraction, response).
                         get_dict())
        except KeyError or IndexError:
            cur_route = {}
    cur_route['response_code'] = response.status_code
    return cur_route


def parallel_tfl_requests(start, attractions):
    with ThreadPoolExecutor() as executor:
        # Parallelize the API requests
        attraction_results = list(
            executor.map(lambda x: get_tfl_journey(start, x), attractions)
        )

    return attraction_results


def get_route_details(postcode_source, postcode_dest):
    postcode_source = parse_postcode(postcode_source)
    postcode_dest = parse_postcode(postcode_dest)
    response = tfl_journey(postcode_source, postcode_dest)
    print("Route details request from {} to {} has returned: HTTP {}".
          format(postcode_source, postcode_dest,
                 str(response.status_code)))

    data = {}
    if response.status_code == 200:
        data = response.json()["journeys"][0]
    data["response_code"] = response.status_code
    return data
