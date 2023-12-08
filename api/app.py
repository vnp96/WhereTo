import json

import requests
from flask import Flask, render_template, request, redirect
from helpers.DBClass import BorgDB
from helpers.ApiHelpers import parallel_tfl_requests
from helpers.PostCodeHelpers import parse_postcode, postcode_to_coordinates

# usage: flask --app=api/app.py run
app = Flask(__name__)

dbConnection = BorgDB()


@app.route("/")
def index():
    return render_template("index.html")


@app.errorhandler(404)
@app.errorhandler(500)
@app.errorhandler(504)
def error_page(e=None):
    return render_template("error.html", error=e)


def test_db_connection():
    got_dbconnection = False
    try:
        dbConnection.get_connection()
        got_dbconnection = True
    except Exception as e:
        print(e)
        print("DB connection failed.")
    print("DB connected") if got_dbconnection else None


@app.route("/attractions", methods=["GET", "POST"])
def attractions_page():
    if request.method == "GET":
        return redirect("/", code=302)
    postcode = parse_postcode(request.form.get("inputPostCode"))
    test_db_connection()

    attractions_list = get_attractions(postcode)
    if attractions_list is None:
        return render_template(
            "index.html", error="That's not a London postcode! \
                                Please try another."
        )
    if attractions_list[0]["response_code"] != 200:
        print("TFL response: " + str(attractions_list[0]["response_code"]))
        return error_page()

    return render_template(
        "attractions.html", post_code=postcode, attractions=attractions_list
    )


@app.route("/results", methods=["GET", "POST"])
def show_res():
    if request.method == "GET":
        return redirect("/", code=302)
    id_attr = request.form.get("id")
    post_code = parse_postcode(request.form.get("post_code"))
    attr_details = dbConnection.get_data_from_db(
        "dbQueries", "get_attr_details", (id_attr,)
    )[0]

    info = {
        "name": attr_details[1],
        "type": attr_details[2],
        "subtype": attr_details[3],
        "description": attr_details[4],
        "post_code": attr_details[5],
        "rating": attr_details[6],
        "image_link_1": attr_details[7],
        "image_link_2": attr_details[8],
    }

    route_details = get_route_details(post_code, info["post_code"])
    if route_details["response_code"] != 200:
        return error_page()

    legs = []
    try:
        duration = route_details["duration"]
        all_data = route_details["legs"]
        for data in all_data:
            leg = {
                "duration": data["duration"],
                "summary": data["instruction"]["summary"],
                "steps": [
                    step["descriptionHeading"] + step["description"]
                    for step in data["instruction"]["steps"]
                ],
                "arrivalPoint": data["arrivalPoint"]["commonName"],
                "path": [stop["name"] for stop in data["path"]["stopPoints"]],
            }
            legs.append(leg)
    except KeyError:
        print("WARNING: Legs were not returned as part of request.")
        print(json.dumps(route_details, indent=4))

    return render_template(
        "results.html", info=info, duration=duration, legs=legs
    )


def get_attractions(postcode):  # should take in the start postcode
    latitude, longitude = postcode_to_coordinates(postcode)
    if latitude is None or longitude is None:
        return None
    query_results = dbConnection.get_data_from_db(
        "dbQueries", "get_attractions", params=(longitude, latitude, latitude)
    )

    attraction_results = parallel_tfl_requests(postcode, query_results)

    for attraction in attraction_results:
        if attraction["response_code"] != 200:
            return [{"response_code": attraction["response_code"]}]

    attraction_results.sort(key=lambda x: x["duration"])

    return attraction_results


def get_route_details(postcode_source, postcode_dest):
    postcode_source = parse_postcode(postcode_source)
    postcode_dest = parse_postcode(postcode_dest)
    response = requests.get(
        "https://api.tfl.gov.uk/journey/journeyresults/"
        + postcode_source
        + "/to/"
        + postcode_dest
    )
    print(
        "Route details request from "
        + postcode_source
        + " to "
        + postcode_dest
        + " has returned: HTTP "
        + str(response.status_code)
    )

    data = {}
    if response.status_code == 200:
        data = response.json()["journeys"][0]
        data["response_code"] = response.status_code
    else:
        data["response_code"] = response.status_code
    return data
