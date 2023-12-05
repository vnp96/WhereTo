from flask import Flask, render_template, request
import requests
from api.helpers.BorgDB import BorgDB
from api.sample_data.fakeData import fakedata

# from api.helpers import helpers

# usage: flask --app=api/app.py run
app = Flask(__name__)

dbConnection = BorgDB()


@app.route("/")
def index():
    # adding comments here for merge conflict
    return render_template("index.html")
    # adding for sample merge


@app.route("/attractions", methods=["POST"])
def attractions_page():
    postcode = request.form.get("inputPostCode")
    print("postcode received = " + str(postcode))
    got_dbconnection = False
    try:
        dbConnection.get_connection()
        got_dbconnection = True
    except Exception as e:
        print(e)
        print("DB connection failed.")
    print("DB connected") if got_dbconnection else None

    route_dictionary = fakedata

    return render_template(
        "attractions.html", post_code=postcode, dictionary=route_dictionary
    )


def dictionary_routes():  # should take in the start postcode
    route = {}
    postcode_start = "ec4r9ha"  ##fake value
    ##postcode_start = request.form.get("inputPostCode")
    ##for attraction in query:
    ##postcode_end = attraction[0]
    postcode_end = "sw72bx"  # from database
    response = requests.get(
        "https://api.tfl.gov.uk/journey/journeyresults/"
        + postcode_start
        + "/to/"
        + postcode_end
    ).json()["journeys"][0]
    if response.status_code == 200:
        route[attraction[1]] = {}
        route[attraction[1]]["duration"] = response["duration"]
        route[attraction[1]]["legs"] = response["legs"]
        print(route)
    return route
