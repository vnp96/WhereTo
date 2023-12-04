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
    code_from = "ec4r9ha" #request.form.get("postcode_start")
    code_to = "sw72bx" #from database
    response = requests.get("https://api.tfl.gov.uk/journey/journeyresults/"+code_from+"/to/"
                                + code_to)
    if response.status_code == 200:
        route = response.json()["journeys"][0]
        print(route)
    # return render_template("response.html", code_from=code_from, code_to=code_to, route=route)
