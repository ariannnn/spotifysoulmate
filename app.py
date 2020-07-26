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

# -- Routes section --
# INDEX

@app.route('/')
@app.route('/index', methods = ["GET", "POST"])
def index():
    global user_email
    if request.method == "POST":
        user_email = ""
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

@app.route('/signup')
def signup():
    return render_template("signup.html")

@app.route("/overview")
def overview():
    global user_email
    user_dict = model.get_user_info(user_email)
    name = user_dict["name"]
    bio = user_dict["bio"]
    song_ids = user_dict["song_ids"] #gives a list
    list_of_songs = model.id_to_song(song_ids) #gives a list of dictionaries
    return render_template("appsites/overview.html", list_of_songs = list_of_songs)

@app.route('/soulmates')
def soulmates():
    return render_template("appsites/soulmates.html")

@app.route('/help')
def help():
    return render_template("appsites/help.html")

@app.route('/sign_in', methods = ["GET", "POST"])
def user_signin():
    global user_email #stores the unique identifier of the user so we can use it to access their playlists, songs, etc
    email = request.form["inputEmail"]
    password = request.form["inputPassword"]
    user_email = email
    user_dict = model.get_user_info(user_email)
    name = user_dict["name"]
    bio = user_dict["bio"]
    song_ids = user_dict["song_ids"] #gives a list
    list_of_songs = model.id_to_song(song_ids) #gives a list of dictionaries
    if (model.sign_in(email, password) == 0):
        user_email = email
        return render_template("appsites/overview.html", list_of_songs = list_of_songs)
    else:
        return render_template("login.html")

@app.route('/store_users', methods=["GET", "POST"])
def store_users(): #this is the route for how the user creates an account
    global user_email #stores the unique identifier of the user so we can use it to access their playlists, songs, etc
    if request.method == "POST":
        name = request.form["inputName"]
        email = request.form["inputEmail"]
        password = request.form["inputPassword"]
        if (model.sign_up(name, email, password) == 0):
            user_email = email
            return render_template("appsites/overview.html")
        else:
            return render_template("signup.html")
    else:
        return "Error: Try using the create an account link instead of manually entering the URL."

@app.route("/test", methods = ["GET","POST"])
def test():
    collection = mongo.db.profile
    if request.method == "POST":
        #the message successfully pushed to dyllon's database
        message = request.form["message"]
        #once we have users implemented, i can also add a "users" key to the dictionary im pushing to the database
        collection.insert({"message":message})
        print(collection.find({}))
    return render_template("test.html")