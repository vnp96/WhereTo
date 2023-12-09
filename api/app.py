import json

from flask import Flask, render_template, request, redirect
from helpers.DBClass import BorgDB
from helpers.ApiHelpers import parallel_tfl_requests, get_route_details
from helpers.PostCodeHelpers import parse_postcode, postcode_to_coordinates
from dto.Attractions import AttractionDetails, RouteDetails

# usage: flask --app=api/app.py run
app = Flask(__name__)

dbConnection = BorgDB()


def test_db_connection():
    try:
        dbConnection.get_connection()
        print("DB connected")
    except Exception as e:
        print(e)
        print("DB connection failed.")


test_db_connection()


@app.route("/")
def index():
    return render_template("index.html")


@app.errorhandler(404)
@app.errorhandler(500)
@app.errorhandler(504)
def error_page(e=None):
    return render_template("error.html", error=e)


@app.route("/attractions", methods=["GET", "POST"])
def attractions_page():
    if request.method == "GET":
        return redirect("/", code=302)
    postcode = parse_postcode(request.form.get("inputPostCode"))

    attractions_list = get_attractions(postcode)
    if attractions_list is None:
        error_message = "That's not a London postcode! Please try another."
        return render_template("index.html", error=error_message)
    if attractions_list[0]["response_code"] != 200:
        print("TFL response: " + str(attractions_list[0]["response_code"]))
        return error_page()

    return render_template(
        "attractions.html", post_code=postcode, attractions=attractions_list
    )


@app.route("/results", methods=["GET", "POST"])
def show_results():
    if request.method == "GET":
        return redirect("/", code=302)

    id_attr = request.form.get("id")
    post_code = parse_postcode(request.form.get("post_code"))

    info = AttractionDetails.from_details_query(
        dbConnection.get_data_from_db('dbQueries',
                                      'get_attr_details',
                                      (id_attr,))[0])

    route_response = get_route_details(post_code, info.post_code)
    if route_response['response_code'] != 200:
        return error_page()

    legs = []
    duration = None
    try:
        route_details = RouteDetails.from_api_response(route_response)
        duration = route_details.duration
        legs = route_details.legs
    except KeyError:
        print("WARNING: Legs were not returned as part of request.")
        print(json.dumps(route_response, indent=4))

    return render_template(
        "results.html", info=info.get_dict(), duration=duration, legs=legs
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


