from flask import Flask, render_template, request
import requests
from api.helpers.BorgDB import BorgDB
#import helpers.py

# usage: flask --app=api/app.py run
app = Flask(__name__)

dbConnection = BorgDB()


@app.route("/")
def index():
    return render_template("index.html")


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

    return render_template("attractions_list.html",
                           dbConnected=got_dbconnection, post_code=postcode)


@app.route("/apis", methods=["GET", "POST"])
def apis():
    route ={}
    postcode_start = "ec4r9ha" 
    ##postcode_start = request.form.get("postcode_start")
    for attraction in query:
        postcode_end = attraction[0]
        postcode_end = "sw72bx" #from database
        response = requests.get("https://api.tfl.gov.uk/journey/journeyresults/+"postcode_start+"/to/"+ postcode_end)
        if response.status_code == 200:
            route[attraction[1]] = response.json()["journeys"]
            print(route)
    #return render_template("response.html", attraction, route=route)
