from flask import Flask, render_template, request
import requests
from api.helpers.BorgDB import BorgDB
from api.helpers.fakeData import fakedata
#import helpers.py

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
    route_dictionary = fakedata
    print(route_dictionary)
    ##route_dictionary = dictionary_routes()
    return render_template("attractions_list.html",
                           dbConnected=got_dbconnection, post_code=postcode, dictionary=route_dictionary)


def dictionary_routes():
    route ={}
    postcode_start = "ec4r9ha" ##fake value
    ##postcode_start = request.form.get("inputPostCode")
    ##for attraction in query:
        ##postcode_end = attraction[0]
    postcode_end = "sw72bx" #from database
    response = requests.get("https://api.tfl.gov.uk/journey/journeyresults/"+postcode_start+"/to/"+ postcode_end).json()["journeys"][0]
    if response.status_code == 200:
        route[attraction[1]] = {}
        route[attraction[1]]['duration'] = response['duration']
        route[attraction[1]]['legs'] = response['legs']
        print(route)
    return route
