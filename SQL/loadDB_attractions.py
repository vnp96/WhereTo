import configparser
import os
import requests
from helpers.DBClass import BorgDB

dbConnection = BorgDB()


def get_places_for_type(typ, subType=None):
    places_url = "https://api.geoapify.com/v2/places"
    london_longitude1 = -0.5
    london_latitude1 = 50
    london_longitude2 = 0.5
    london_latitude2 = 52
    limit = 10
    apiKey = os.environ.get("PLACES_API_KEY")

    apiCall = places_url + "?" + "categories=" + typ
    if subType:
        apiCall += "." + subType
    apiCall += (
        "&filter=rect:"
        + str(london_longitude1)
        + ","
        + str(london_latitude1)
        + ","
        + str(london_longitude2)
        + ","
        + str(london_latitude2)
    )
    apiCall += "&limit=" + str(limit)
    apiCall += "&apiKey=" + str(apiKey)

    response = requests.get(apiCall)

    attractions = []
    if response.status_code == 200:
        for feature in response.json()["features"]:
            attraction = {
                "name": feature["properties"]["name"],
                "type": typ,
                "subtype": subType if subType else None,
                "post_code": feature["properties"]["postcode"],
                "latitude": feature["properties"]["lat"],
                "longitude": feature["properties"]["lon"],
            }
            attractions.append(attraction)
            print(attraction)

    return attractions


def load_db_with_data():
    config = configparser.ConfigParser()
    config.read("db_details.ini")
    places = [
        get_places_for_type("tourism", "attraction"),
        get_places_for_type("tourism", "sights"),
        get_places_for_type("catering", "restaurant"),
    ]
    conn = dbConnection.get_connection()
    curs = conn.cursor()
    for place_type in places:
        for place in place_type:
            if place["type"] == "tourism":
                params = (
                    place["name"],
                    place["type"],
                    place["subtype"],
                    place["post_code"],
                    place["latitude"],
                    place["longitude"],
                )
            else:
                params = (
                    place["name"],
                    place["subtype"],
                    None,
                    place["post_code"],
                    place["latitude"],
                    place["longitude"],
                )
            try:
                curs.execute(config["dbLoader"]["load_attractions"], params)
                print("added a row for " + place["name"])
            except Exception as e:
                print(
                    "If unique constraint, it doesnt matter, its by design.->"
                    + place["name"]
                )
                print(e)
            conn.commit()


load_db_with_data()
