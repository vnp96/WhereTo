from app import process_query
import pytest
import json
from helpers import helpers
#Will need to have downloaded pytest-mock

@pytest.fixture()
def fake_tfl_journey():
    """
    Fake TFL Journey from London Bridge (EC4R9HA) to Imperial College (SW72BX)
    """
    with open("sample_data/mockTFLJourney.json") as f:
        return json.load(f)

def test_retrieve_transit_time_using_mocks(mocker, fake_tfl_journey):
    """
    
    """
    fake_resp = mocker.Mock()
    fake_resp.json = mocker.Mock(return_value=fake_tfl_journey)
    fake_resp.status_code = HTTPStatus.OK

    mocker.patch("tfl_app.requests.get",return_value=fake_resp)

    journey_info = retrieve_tfl_journey("EC4R9HA","SW72BX","")
    assert journey_info == JourneyInfo.from_dict(fake_tfl_journey)
