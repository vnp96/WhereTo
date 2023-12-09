import json
from http import HTTPStatus

import pytest

from helpers.ApiHelpers import *
from dto.DataClasses import AttractionDetails


# Will need to have downloaded pytest-mock


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


def test_tfl_journey(patch_tfl_api):
    journey_info = tfl_journey("EC4R9HA", "SW72BX")
    assert journey_info.response_code == 200
    assert journey_info.duration == 34
    assert len(journey_info.legs) == 3
    assert journey_info.legs[1]["duration"] == 16
    assert journey_info.legs[2]["summary"] == "Walk to SW7 2BX"


def test_tfl_journey_negative(patch_tfl_api_negative):
    journey_info = tfl_journey("EC4R9HA", "SW72BX")
    assert journey_info.response_code != 200
    assert journey_info.duration is None
    assert journey_info.legs is None


def test_get_journey_source_to_dest(patch_tfl_api):
    journey_dict = get_journey_source_to_dest("EC4R 9HA", "Sw7 2b x")
    assert journey_dict["response_code"] == 200
    assert journey_dict["duration"] == 34
    assert len(journey_dict["legs"]) == 3
    assert journey_dict["legs"][1]["duration"] == 16
    assert journey_dict["legs"][2]["summary"] == "Walk to SW7 2BX"


def test_get_journey_source_to_dest_negative(patch_tfl_api_negative):
    journey_dict = get_journey_source_to_dest("EC4R 9HA", "Sw7 2b x")
    assert journey_dict["response_code"] != 200
    assert journey_dict["duration"] is None
    assert journey_dict["legs"] is None
