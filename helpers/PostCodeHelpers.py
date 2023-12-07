from geopy import Nominatim


def parse_postcode(postcode):
    assert isinstance(postcode, str)
    parsed_postcode = postcode.replace(" ", "").lower()
    if parsed_postcode.isalnum():
        return parsed_postcode
    else:
        return None


def postcode_to_coordinates(postcode):
    geolocator = Nominatim(user_agent="WhereTo")
    location = geolocator.geocode(postcode)

    if location:
        # latitude, longitude = location.latitude, location.longitude
        return location.latitude, location.longitude
    else:
        return None


if __name__ == "__main__":
    print(postcode_to_coordinates("SW81XR"))