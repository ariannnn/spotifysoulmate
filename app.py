# ---- YOUR APP STARTS HERE ----
# -- Import section --
from flask import Flask
from flask import render_template
from flask import request
from flask_pymongo import PyMongo
import model
import requests
import match_score
from flask import session
import bcrypt
from flask import redirect, url_for

#don't forget to "pip3 install spotipy" and "sudo pip3 install dnspython" if you haven't already
# -- Initialization section --
app = Flask(__name__)

app.secret_key = "kj3klmr13asd"
# name of database
app.config['MONGO_DBNAME'] = 'users'

# URI of database
app.config['MONGO_URI'] = 'mongodb+srv://admin:xOCwocN6xNvzPPSB@cluster0.vlksj.mongodb.net/users?retryWrites=true&w=majority'


mongo = PyMongo(app)

email = "" #this variable is initialized here to avoid bugs

# -- Routes section --
# INDEX
@app.route('/')
@app.route('/index', methods = ["GET", "POST"])
def index():
    is_session_empty = False
    if session.get("email") == None or session["email"] != email:
        session.clear()
        is_session_empty = True
    return render_template("index.html", is_session_empty = is_session_empty)

#might be old code
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

@app.route('/login', methods = ["GET","POST"])
def login():
    return render_template("login.html")

@app.route('/signup')
def signup():
    return render_template("signup.html")

@app.route("/overview")
def overview():
    if session.get("email") == None or session["email"] != email:
        session.clear()
        return render_template("login.html")
    else:
        list_of_songs = model.id_to_song(session["song_ids"]) #gives a list of dictionaries
        return render_template("appsites/overview.html", list_of_songs = list_of_songs)

@app.route('/soulmates')
def soulmates():
    if session.get("email") == None or session["email"] != email:
        session.clear()
        return render_template("login.html")
    else:
        return render_template("appsites/soulmates.html")

@app.route('/help')
def help():
    if session.get("email") == None or session["email"] != email:
        session.clear()
        return render_template("login.html")
    else:
        return render_template("appsites/help.html")

@app.route('/sign_in', methods = ["GET", "POST"])
def user_signin():
    global email
    session.clear()
    if request.method == "POST":
        email = request.form["inputEmail"]
        password = request.form["inputPassword"]
        collection = mongo.db.profile
        user = list(collection.find({"email": email}))
        if (len(user) == 0):
            print("hello")
            return render_template("login.html")
        elif bcrypt.hashpw(password.encode('utf-8'), user[0]['password'].encode('utf-8')) == user[0]["password"].encode('utf-8'):
            session["email"] = user[0]["email"]
            session["name"] = user[0]["name"]
            session["bio"] = user[0]["bio"]
            session["song_ids"] = user[0]["song_ids"]
            list_of_songs = model.id_to_song(session["song_ids"]) #gives a list of dictionaries
            return render_template("appsites/overview.html", list_of_songs = list_of_songs)
        else:
            return render_template("login.html")
    else:
        return render_template("login.html")

@app.route('/store_users', methods=["GET", "POST"])
def store_users(): #this is the route for how the user creates an account
    global email
    if request.method == "POST":
        name = request.form["inputName"]
        email = request.form["inputEmail"]
        password = request.form["inputPassword"]
        collection = mongo.db.profile
        user = list(collection.find({"email": email}))
        if (len(user) == 0):
            collection.insert({"password": str(bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()), 'utf-8'), "email": email, "name": name,"bio": "I am feeling good", "song_ids": []})
            user = list(collection.find({"email": email}))
            session["email"] = user[0]["email"]
            session["name"] = user[0]["name"]
            session["bio"] = user[0]["bio"]
            session["song_ids"] = user[0]["song_ids"]
            list_of_songs = model.id_to_song(session["song_ids"])
            return render_template("appsites/overview.html", list_of_songs = list_of_songs)
        else:
            return render_template("signup.html")
    else:
        return render_template("signup.html")

@app.route("/search", methods = ["GET", "POST"])
def search():
    if request.method == "POST":
        song_query = request.form["song_query"]
        artist_query = request.form["artist_query"]
        song_ids = model.search_for_track_and_artist(song_query, artist_query) #gives a list of 10 song_ids that have similar names to the search query
        songs_found = model.id_to_song(song_ids) #gives a list of dictionaries
        list_of_songs = model.id_to_song(session["song_ids"])
        return render_template("appsites/overview.html", songs_found = songs_found, list_of_songs = list_of_songs)
    else:
        return "Error. Search for a song using the button, not by manually typing in the URL."

@app.route("/addsong/<song_id>")
def addsong(song_id):
    collection = mongo.db.profile
    collection.update({"email": session["email"]}, {"$push": {"song_ids": song_id} })
    session["song_ids"].append(song_id)
    list_of_songs = model.id_to_song(session["song_ids"])
    return render_template("appsites/overview.html", list_of_songs = list_of_songs)

@app.route("/find_soulmates/<soulmate_query>")
def find_soulmates(soulmate_query):
    collection = mongo.db.users
    users = collection.find({})
    p1 = model.id_to_song(session["song_ids"])
    for user in users:
        p2 = model.id_to_song(user["song_ids"])
        match_score = match_score.match_score_by_song(p1, p2)
        print(match_score)
        # if soulmate_query == "song":
        #     match_score.match_score_by_song(p1, p2)
    return "test"

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

# FYI on passwords - a student at another bank site just discovered documentation for bcrypt.checkpw() function that takes 2 arguments - the pw from the form and the pw from the database and returns True if they work!