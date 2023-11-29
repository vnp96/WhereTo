from flask import Flask, render_template, request
import requests

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/apis", methods=["GET", "POST"])
def apis():
    repos = [{}]
    username = request.form.get("username")
    if username:
        response = requests.get("https://api.github.com/users/"
                                + username + "/repos")
        if response.status_code == 200:
            repos = response.json()
            for repo in repos:
                url_raw = requests.get(repo["commits_url"][:-6])
                url = url_raw.json()
                if url_raw.status_code == 200:
                    repo["newest_commit"] = url[0]["sha"]
                    repo["newest_commit_message"] = url[0]["commit"]["message"]
                    repo["num_commits"] = len(url)
        elif response.status_code == 403:
            repos[0]['full_name'] = ""
            repos[0]['clone_url'] = "Too many requests, try again later!"
            repos[0]['updated_at'] = ""
            repos[0]['newest_commit'] = ""
            repos[0]['newest_commit_message'] = ""
            repos[0]['num_commits'] = ""
    else:
        response = "Not found"
        repos = None
    return render_template("response.html", username=username, repos=repos)


@app.route("/query")
def handle_query():
    return process_query(request.args.get("q"))


def process_query(word):
    if "dinosaurs" in word:
        return "Dinosaurs ruled the Earth 200 million years ago"
