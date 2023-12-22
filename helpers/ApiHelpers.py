"""
Helper functions for the website
"""
import os
import random
from threading import Thread
from timeit import default_timer as timer

import requests
from flask import Flask
from flask_caching import Cache

from dto.DataClasses import AttractionDetails, TflJourneyResponse
from helpers.PostCodeHelpers import parse_postcode

config = {
    "DEBUG": False,
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300
}
# usage: flask --app=api/app.py run
app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)

BASE_URL = "https://api.tfl.gov.uk/Journey/JourneyResults/"
API = BASE_URL + "{postcode_start}/to/{postcode_end}?api_key={api_key}"


@cache.memoize(300)
def tfl_journey(start: str, end: str) -> TflJourneyResponse:
    api_key = os.environ.get("WHERE2TFL_KEY")
    if start == end:
        return TflJourneyResponse.same_location(end)
    url = API.format(postcode_start=start, postcode_end=end,
                     api_key=api_key)
    resp = requests.get(url, timeout=8)
    ret = TflJourneyResponse.from_api_response(resp)
    ret.rand_value = int(random.randrange(0, 1000))
    return ret


def get_journey_source_to_dest(postcode_source: str,
                               postcode_dest: str) -> dict:
    postcode_source = parse_postcode(postcode_source)
    postcode_dest = parse_postcode(postcode_dest)
    tfl_journey_dict = tfl_journey(postcode_source,
                                   postcode_dest).get_dict()
    print("Route details request from {} to {} has returned: HTTP {}".
          format(postcode_source, postcode_dest,
                 str(tfl_journey_dict["response_code"])
                 ))

    return tfl_journey_dict


def get_attr_with_duration(start: str, attraction: AttractionDetails,
                           attraction_results: list) -> None:
    tfl_journey_dict = get_journey_source_to_dest(start,
                                                  attraction.post_code)

    attraction.add_api_response(tfl_journey_dict)
    attraction_results.append(attraction.get_dict())


def parallel_tfl_requests(start: str,
                          attractions: list[AttractionDetails]) \
        -> list[dict]:
    start_time = timer()
    attraction_results = []
    jobs = []
    for attraction in attractions:
        thread = Thread(target=get_attr_with_duration,
                        args=(start, attraction, attraction_results))
        jobs.append(thread)
        thread.start()
    for job in jobs:
        job.join()
    end = timer()
    print("Parallel execution for postcode: " + start
          + " took: " + str(end - start_time))
    return attraction_results
