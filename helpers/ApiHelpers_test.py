import copy
import json
from http import HTTPStatus

import pytest

from helpers.ApiHelpers import *
from helpers.PostCodeHelpers import parse_postcode

POSTCODE_SOURCE = "EC4R 9HA"
POSTCODE_DEST = "SW7 2BX"


@pytest.fixture()
def fixed_api_response():
    with open("sample_data/mockTFLJourney.json") as f:
        return json.load(f)


@pytest.fixture()
def patch_tfl_api(mocker, fixed_api_response):
    fake_resp = mocker.Mock()
    fake_resp.json = mocker.Mock(return_value=fixed_api_response)
    fake_resp.status_code = HTTPStatus.OK

    mocker.patch("requests.get", return_value=fake_resp)


@pytest.fixture()
def patch_tfl_api_negative(mocker, fixed_api_response):
    fake_resp = mocker.Mock()
    fake_resp.json = mocker.Mock(return_value=fixed_api_response)
    fake_resp.status_code = HTTPStatus.NOT_FOUND

    mocker.patch("requests.get", return_value=fake_resp)


@pytest.fixture()
def fixed_query_details_object():
    query_data = (25, "test_name", "test_type", "test_subtype",
                  "test_description", POSTCODE_DEST, 2.5,
                  "test_link_1", "test_link_2")
    return AttractionDetails.from_details_query(query_data)


def test_tfl_journey(patch_tfl_api):
    journey_info = tfl_journey(parse_postcode(POSTCODE_SOURCE),
                               parse_postcode(POSTCODE_DEST))
    assert journey_info.response_code == 200
    assert journey_info.duration == 34
    assert len(journey_info.legs) == 3
    assert journey_info.legs[1]["duration"] == 16
    assert journey_info.legs[2]["summary"] == "Walk to SW7 2BX"


def test_tfl_journey_negative(patch_tfl_api_negative):
    journey_info = tfl_journey(parse_postcode(POSTCODE_SOURCE),
                               parse_postcode(POSTCODE_DEST))
    assert isinstance(journey_info, TflJourneyResponse)
    assert journey_info.response_code != 200
    assert journey_info.duration is None
    assert journey_info.legs is None


def test_get_journey_source_to_dest(patch_tfl_api):
    journey_dict = get_journey_source_to_dest(POSTCODE_SOURCE,
                                              POSTCODE_DEST)
    assert journey_dict["response_code"] == 200
    assert journey_dict["duration"] == 34
    assert len(journey_dict["legs"]) == 3
    assert journey_dict["legs"][1]["duration"] == 16
    assert journey_dict["legs"][2]["summary"] == "Walk to SW7 2BX"


def test_get_journey_source_to_dest_negative(patch_tfl_api_negative):
    journey_dict = get_journey_source_to_dest(POSTCODE_SOURCE,
                                              POSTCODE_DEST)
    assert journey_dict["response_code"] != 200
    assert journey_dict["duration"] is None
    assert journey_dict["legs"] is None


def test_get_attr_with_duration(patch_tfl_api, fixed_query_details_object):
    attr_with_duration = get_attr_with_duration(POSTCODE_SOURCE,
                                                fixed_query_details_object)
    assert isinstance(attr_with_duration, dict)
    assert attr_with_duration["response_code"] == 200
    assert attr_with_duration["duration"] == 34


def test_parallel_tfl_requests(patch_tfl_api, fixed_query_details_object):
    query_object_list = [copy.deepcopy(fixed_query_details_object)
                         for i in range(3)]
    tfl_response_list = parallel_tfl_requests(POSTCODE_SOURCE,
                                              query_object_list)
    assert len(tfl_response_list) == 3
    for response in tfl_response_list:
        assert isinstance(response, dict)
        assert response["response_code"] == 200
        assert response["duration"] == 34
