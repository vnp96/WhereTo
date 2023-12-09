import json
from http import HTTPStatus

import pytest

from dto.DataClasses import *

POSTCODE_SOURCE = "EC4R 9HA"
POSTCODE_DEST = "SW7 2BX"


@pytest.fixture()
def fixed_query_details_tuple():
    return (25, "test_name", "test_type", "test_subtype",
            "test_description", POSTCODE_DEST, None,
            "test_link_1", "test_link_2")


@pytest.fixture()
def fixed_api_response():
    with open("sample_data/mockTFLJourney.json") as f:
        return json.load(f)


@pytest.fixture()
def patch_tfl_api(mocker, fixed_api_response):
    fake_resp = mocker.Mock()
    fake_resp.json = mocker.Mock(return_value=fixed_api_response)
    fake_resp.status_code = HTTPStatus.OK

    return fake_resp


@pytest.fixture()
def patch_tfl_api_negative(mocker, fixed_api_response):
    fake_resp = mocker.Mock()
    fake_resp.json = mocker.Mock(return_value=[{}])
    fake_resp.status_code = HTTPStatus.NOT_FOUND

    return fake_resp


def test_from_api_response(patch_tfl_api):
    resp = patch_tfl_api
    obj = TflJourneyResponse.from_api_response(resp)

    assert obj.response_code == 200
    assert obj.duration == 34
    assert isinstance(obj.legs, list)
    assert isinstance(obj.legs[0], dict)
    assert obj.legs[0]["duration"] == 7


def test_from_api_response_neg(patch_tfl_api_negative):
    resp = patch_tfl_api_negative
    obj = TflJourneyResponse.from_api_response(resp)

    assert obj.response_code != 200
    assert obj.duration is None
    assert obj.legs is None


def test_api_same_location():
    obj = TflJourneyResponse.same_location(POSTCODE_SOURCE)

    assert obj.response_code == 200
    assert obj.duration == 0
    assert len(obj.legs) == 1
    assert obj.legs[0]["duration"] == 0
    assert obj.legs[0]["arrivalPoint"] == POSTCODE_SOURCE


def test_tjr_get_dict():
    obj = TflJourneyResponse.same_location(POSTCODE_SOURCE)
    dct = obj.get_dict()

    assert len(dct.keys()) == 3
    assert dct["response_code"] == obj.response_code
    assert dct["duration"] == obj.duration


def test_from_details_query(fixed_query_details_tuple):
    obj = AttractionDetails.from_details_query(fixed_query_details_tuple)

    assert obj.id == fixed_query_details_tuple[0]
    assert obj.name == fixed_query_details_tuple[1]
    assert obj.duration is None


def test_add_api_response_to_query(fixed_query_details_tuple,
                                   patch_tfl_api_negative):
    obj = AttractionDetails.from_details_query(fixed_query_details_tuple)
    api_resp = (TflJourneyResponse.
                from_api_response(patch_tfl_api_negative).get_dict())
    obj.add_api_response(api_resp)

    assert obj.response_code == 404
    assert obj.duration is None


def test_ad_get_dict(fixed_query_details_tuple,
                     patch_tfl_api_negative):
    obj = AttractionDetails.from_details_query(fixed_query_details_tuple)
    api_resp = (TflJourneyResponse.
                from_api_response(patch_tfl_api_negative).get_dict())
    obj.add_api_response(api_resp)
    dict_w_api = obj.get_dict()

    assert dict_w_api["id"] == fixed_query_details_tuple[0]
    assert dict_w_api["name"] == fixed_query_details_tuple[1]
    assert "response_code" in dict_w_api.keys()
    assert "duration" not in dict_w_api.keys()
