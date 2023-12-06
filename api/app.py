from flask import Flask, render_template, request, redirect
import requests
from api.helpers.BorgClass import BorgDB
from sample_data.fakeData import fakedata

from api.helpers.helpers import parse_postcode

# usage: flask --app=api/app.py run
app = Flask(__name__)

dbConnection = BorgDB()


@app.route("/")
def index():
    # adding comments here for merge conflict
    return render_template("index.html")
    # adding for sample merge


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
    if request.method == 'GET':
        return redirect("/", code=302)
    postcode = request.form.get("inputPostCode")
    test_db_connection()

    attractions_list = get_attractions(postcode)
    print(attractions_list) #[] if invalid postcode

    return render_template(
        "attractions.html", post_code=postcode, attractions=attractions_list
    )


@app.route("/results", methods=["POST"])
def show_res():
    id_attr = request.form.get("id")
    post_code = parse_postcode(request.form.get("post_code"))
    print(id_attr, post_code)
    attr_details = dbConnection.get_data_from_db('dbQueries',
                                                 'get_attr_details',
                                                 (id_attr,))[0]

    info = {'name': attr_details[1],
            'type': attr_details[2],
            'subtype': attr_details[3],
            'description': attr_details[4],
            'post_code': attr_details[5],
            'rating': attr_details[6]}

    route_details = get_route_details(post_code, info['post_code'])
    #print(route_details)
    legs = route_details['legs']

    return render_template("results.html", info=info, legs=legs)


def get_attractions(postcode):  # should take in the start postcode
    attraction_results = []

    query_results = dbConnection.get_data_from_db('dbQueries',
                                                  'get_attractions')

    for attraction in query_results:
        postcode_attraction = parse_postcode(attraction[1])
        response = requests.get(
            "https://api.tfl.gov.uk/journey/journeyresults/"
            + postcode
            + "/to/"
            + postcode_attraction
        )
        if response.status_code == 200:
            data = response.json()["journeys"][0]
            cur_route = {"id": attraction[2],
                         "name": attraction[0],
                         "duration": data["duration"]}
            attraction_results.append(cur_route)
            # route[attraction[0]]["legs"] = response["legs"]
            print(attraction_results)

    attraction_results.sort(key=lambda x: x["duration"])
    return attraction_results


def get_route_details(postcode_source,
                      postcode_dest):  # should take in the start postcode
    postcode_source = parse_postcode(postcode_source)
    postcode_dest = parse_postcode(postcode_dest)
    response = requests.get(
        "https://api.tfl.gov.uk/journey/journeyresults/"
        + postcode_source
        + "/to/"
        + postcode_dest
    )
    data = {}
    if response.status_code == 200:
        data = response.json()["journeys"][0]
        return data
    return data
