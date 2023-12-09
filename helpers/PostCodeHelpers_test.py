from PostCodeHelpers import is_london_postcode, parse_postcode
from PostCodeHelpers import postcode_to_coordinates


def test_parse_postcode():
    # Test valid postcode
    assert parse_postcode("SW1A 1AA") == "SW1A1AA"
    # Test non valid input
    assert parse_postcode(256) is None
    assert parse_postcode("!@#$%") is None


def test_is_london_postcode():
    # London postcodes
    assert is_london_postcode("SW")
    assert is_london_postcode("N1")
    assert is_london_postcode("W1A")
    # Non-London postcodes
    assert not is_london_postcode("B11")
    assert not is_london_postcode("CM12")
    assert not is_london_postcode("AB12")


def test_postcode_to_coordinates():
    # London postcode coordinates
    assert postcode_to_coordinates("SW81XR") == (51.4754099, -0.12267)
    #  Non-London postcode coordinates
    assert postcode_to_coordinates("AB12CD") == (None, None)
    # Test invalid postcode length
    assert postcode_to_coordinates("EC1") == (None, None)
    assert postcode_to_coordinates("SW810XRR") == (None, None)


""" if __name__ == "__main__":
    test_parse_postcode()
    test_is_london_postcode()
    test_postcode_to_coordinates() """
