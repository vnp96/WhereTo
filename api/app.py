import json
from threading import Thread

from flask import Flask, render_template, request, redirect

from dto.DataClasses import AttractionDetails
from helpers.ApiHelpers import (parallel_tfl_requests,
                                get_journey_source_to_dest, is_valid_hex_color)
from helpers.DBClass import BorgDB
from helpers.PostCodeHelpers import parse_postcode, postcode_to_coordinates

config = {
    "DEBUG": False,
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300
}
# usage: flask --app=api/app.py run
app = Flask(__name__)

dbConnection = BorgDB()
attractionsFound = False
loading_try = 0
bgColor = '#fffeec'
fontColor = '#000000'


def test_db_connection():
    try:
        dbConnection.get_connection()
        print("DB connected")
    except Exception as e:
        print(e)
        print("DB connection failed.")


test_db_connection()

@app.context_processor
def inject_globals():
    parameters = {
        'bgColor': bgColor,
        'fontColor': fontColor
    }
    return parameters


@app.route("/")
def index():
    global attractionsFound
    global loading_try
    global bgColor
    print("BGColor is now:" + bgColor)
    print("FontColor is now:" + fontColor)
    attractionsFound = False
    loading_try = 0
    return render_template("index.html")


@app.errorhandler(404)
@app.errorhandler(500)
@app.errorhandler(504)
def error_page(e=None):
    return render_template("error.html", error=e)


@app.route("/loading", methods=["GET", "POST"])
def loading_page():
    if request.method == "GET":
        return redirect("/", code=302)
    post_code = parse_postcode(request.form.get("inputPostCode"))

    thread = Thread(target=get_attractions, args=(post_code,))
    thread.start()

    return render_template("loading.html",
                           inputPostCode=post_code)


@app.route("/change", methods=["GET"])
def change_color():
    global bgColor
    global fontColor
    if request.args.get("default"):
        bgColor = '#fffeec'
        fontColor = '#000000'
    else:
        bgColorParam = request.args.get("bgcolor")
        print("BG color received:" + str(bgColorParam))
        if bgColorParam:
            if is_valid_hex_color('#' + bgColorParam):
                bgColor = '#' + bgColorParam
            else:
                bgColor = bgColorParam
        fontColorParam = request.args.get("fontcolor")
        print("Font color received:" + str(fontColorParam))
        if fontColorParam:
            if is_valid_hex_color('#' + fontColorParam):
                fontColor = '#' + fontColorParam
            else:
                fontColor = fontColorParam

    return redirect("/", code=302)


@app.route("/check_loading")
def check_loading():
    global attractionsFound
    global loading_try
    loading_try += 1
    return {'loaded': attractionsFound, 'max_try_passed': loading_try > 6}


@app.route("/attractions", methods=["GET", "POST"])
def attractions_page():
    if request.method == "GET":
        return redirect("/", code=302)
    postcode = request.form.get("inputPostCode")

    attractions_list = get_attractions(postcode)
    if attractions_list is None:
        error_message = "That's not a London postcode! Please try another."
        return render_template("index.html", error=error_message)
    if attractions_list[0]["response_code"] != 200:
        print("TFL response: " + str(attractions_list[0]["response_code"]))
        return error_page()

    return render_template(
        "attractions.html", post_code=postcode,
        attractions=attractions_list
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

    route_resp_dict = get_journey_source_to_dest(post_code, info.post_code)
    if route_resp_dict['response_code'] != 200:
        return error_page()

    try:
        duration = route_resp_dict["duration"]
        legs = route_resp_dict["legs"]
        return render_template("results.html",
                               info=info.get_dict(),
                               duration=duration,
                               legs=legs)
    except KeyError:
        print("WARNING: Legs were not returned as part of request.")
        print(json.dumps(route_resp_dict, indent=4))
        return error_page()


def get_attractions(postcode):
    latitude, longitude = postcode_to_coordinates(postcode)
    if latitude is None or longitude is None:
        return None
    query_results = dbConnection.get_data_from_db(
        "dbQueries", "get_attractions", params=(longitude, latitude, latitude)
    )
    attr_query_details = [AttractionDetails.from_details_query(query_result)
                          for query_result in query_results]

    attraction_results = parallel_tfl_requests(postcode, attr_query_details)
    filtered_200 = list(filter(lambda attr: attr["response_code"] == 200,
                               attraction_results))

    global attractionsFound
    attractionsFound = True
    if len(filtered_200) == 0:
        return [{"response_code": attraction_results[0]["response_code"]}]

    return sorted(filtered_200, key=lambda x: x["duration"])
