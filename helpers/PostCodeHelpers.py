from geopy import Nominatim


def parse_postcode(postcode):
    assert isinstance(postcode, str)
    parsed_postcode = postcode.replace(" ", "").lower()
    if parsed_postcode.isalnum():
        return parsed_postcode
    else:
        return None


def is_london_postcode(postcode):
    london_postcodes = [
        "E", "EC", "N", "NW", "SE", "SW", "W",  # Inner London
        "BR", "CR", "DA", "EN", "HA", "IG", "KT", "RM", "SM", "TN" # Outer London
    ]

    return any(postcode.upper().startswith(area) for area in london_postcodes)


def postcode_to_coordinates(postcode):
    if not is_london_postcode(postcode):
        return None, None
    
    if len(postcode) < 5 or len(postcode) > 8:
        return None, None

    geolocator = Nominatim(user_agent="WhereTo")
    location = geolocator.geocode(postcode)

    if location:
        # latitude, longitude = location.latitude, location.longitude
        return location.latitude, location.longitude
    else:
        return None, None


if __name__ == "__main__":
    print(postcode_to_coordinates("SW81XR"))