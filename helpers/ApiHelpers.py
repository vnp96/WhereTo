"""
Helper functions for the website
"""
import os
from concurrent.futures import ThreadPoolExecutor
import requests
from helpers.PostCodeHelpers import parse_postcode
from dto.DataClasses import AttractionDetails, TflJourneyResponse

BASE_URL = "https://api.tfl.gov.uk/Journey/JourneyResults/"
API = BASE_URL + "{postcode_start}/to/{postcode_end}?api_key={api_key}"


def tfl_journey(start: str, end: str) -> TflJourneyResponse:
    api_key = os.environ.get("WHERE2TFL_KEY")
    if start == end:
        return TflJourneyResponse.same_location(end)
    url = API.format(postcode_start=start, postcode_end=end, api_key=api_key)
    resp = requests.get(url)
    return TflJourneyResponse.from_api_response(resp)


def get_journey_source_to_dest(postcode_source: str,
                               postcode_dest: str) -> dict:
    postcode_source = parse_postcode(postcode_source)
    postcode_dest = parse_postcode(postcode_dest)
    tfl_journey_dict = tfl_journey(postcode_source, postcode_dest).get_dict()
    print("Route details request from {} to {} has returned: HTTP {}".
          format(postcode_source, postcode_dest,
                 str(tfl_journey_dict["response_code"])))

    return tfl_journey_dict


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
            executor.map(lambda x: get_attr_with_duration(start, x),
                         attractions)
        )

    return attraction_results
