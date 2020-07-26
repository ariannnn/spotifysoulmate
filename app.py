# ---- YOUR APP STARTS HERE ----
# -- Import section --
from flask import Flask
from flask import render_template
from flask import request
from flask_pymongo import PyMongo
import model
import requests

#don't forget to "pip3 install spotipy" and "sudo pip3 install dnspython" if you haven't already
# -- Initialization section --
app = Flask(__name__)

# name of database
app.config['MONGO_DBNAME'] = 'playlist'

# URI of database
app.config['MONGO_URI'] = 'mongodb+srv://admin:xOCwocN6xNvzPPSB@cluster0.vlksj.mongodb.net/playlist?retryWrites=true&w=majority'

mongo = PyMongo(app)

#i need to find a way to view dyllon's database

# -- Routes section --
# INDEX

@app.route('/')
@app.route('/index')
def index():
    collection = mongo.db.profile
    if request.method == "POST":
        #the message successfully pushed to dyllon's database
        message = request.form["message"]
        #once we have users implemented, i can also add a "users" key to the dictionary im pushing to the database
        collection.insert({"message":message})
    return render_template("index.html")

@app.route('/profile', methods=["GET", "POST"])
def profile():
    collection = mongo.db.songs
    songs = collection.find({})
    if request.method == "POST":
        user_artist = request.form["artist"]
        user_song = request.form["song"]
        print(songs)
        songs = mongo.db.songs
        songs.insert({"song": "Test Day", "arist": "2020-12-10", "album": "test","genres": ["test", "test"]})
        songs = collection.find({})
        return render_template("profile.html",
                                user_artist=user_artist,
                                user_top_tracks=user_song, songs = songs)
    else:
        return render_template("profile.html", songs = songs)

#perhaps i could just use <input type = "submit" class = "nav-link"> so that the user cannot log in by just manually typing in the URL

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/login', methods = ["GET","POST"])
def login():
    return render_template("login.html")

@app.route('/signup', methods = ["GET","POST"])
def signup():
    return render_template("signup.html")

@app.route('/appsites/soulmates', methods = ["GET","POST"])
def soulmates():
    return render_template("appsites/soulmates.html")
    # if request.method == "POST":
    #     return render_template("appsites/soulmates.html")
    # else:
    #     return "Try logging in instead of manually entering in the URL."

@app.route('/appsites/help', methods = ["GET","POST"])
def help():
    return render_template("appsites/help.html")
    # if request.method == "POST":
    #     return render_template("appsites/help.html")
    # else:
    #     return "Try logging in instead of manually entering in the URL."

@app.route('/appsites/overview', methods = ["GET","POST"])
def user_signin():
    return render_template("appsites/overview.html")
    # if request.method == "POST":
    #     return render_template("appsites/overview.html")
    # else:
    #     return "Try logging in instead of manually entering in the URL."

@app.route('/store_users', methods=["GET", "POST"])
def store_users():
    if request.method == "POST":
        user_email = request.form["inputEmail"]
        user_name = request.form["inputName"]
        user_password = request.form["inputPassword"]
        collection = mongo.db.profile
        collection.insert({"username":user_name, "password":user_password, "name":user_name})
    else:
        return "Error. Use the create an account page, not manually entering in the URL."