"""
Helper functions for the website
"""
import os
from concurrent.futures import ThreadPoolExecutor
import requests
from dto.DataClasses import *
from helpers.PostCodeHelpers import parse_postcode
from dto.DataClasses import AttractionDetails, TflJourneyResponse

BASE_URL = "https://api.tfl.gov.uk/Journey/JourneyResults/"
API = BASE_URL + "{postcode_start}/to/{postcode_end}?api_key={api_key}"


def tfl_journey(start: str, end: str) -> dict:
    api_key = os.environ.get("WHERE2TFL_KEY")
    url = API.format(postcode_start=start, postcode_end=end, api_key=api_key)
    resp = requests.get(url)
    resp_obj = TflJourneyResponse.from_api_response(resp)
    return resp_obj.get_dict()


def get_journey_source_to_dest(postcode_source: str,
                               postcode_dest: str) -> dict:
    postcode_source = parse_postcode(postcode_source)
    postcode_dest = parse_postcode(postcode_dest)
    tfl_journey_dict = tfl_journey(postcode_source, postcode_dest)
    print("Route details request from {} to {} has returned: HTTP {}".
          format(postcode_source, postcode_dest,
                 str(tfl_journey_dict["response_code"])))

    return tfl_journey_dict

def retrieve_tfl_journey(start: str, end: str) -> JourneyInfo:
    """
    Does the API call for the TFL Journey and
    returns a JourneyInfo Class Object
    """
    data = tfl_journey(start, end)
    return JourneyInfo.from_dict(data)


def get_attr_with_duration(start: str, attraction: AttractionDetails)\
        -> dict:
    tfl_journey_dict = get_journey_source_to_dest(start, attraction.post_code)

    attraction.add_api_response(tfl_journey_dict)
    return attraction.get_dict()


def parallel_tfl_requests(start: str, attractions: list[AttractionDetails])\
        -> list[dict]:
    with ThreadPoolExecutor() as executor:
        # Parallelize the API requests
        attraction_results = list(
            executor.map(lambda x: get_attr_with_duration(start, x), attractions)
        )

    return attraction_results




print('Here')