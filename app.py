# ---- YOUR APP STARTS HERE ----
# -- Import section --
from flask import Flask
from flask import render_template
from flask import request
from flask_pymongo import PyMongo


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




# CONNECT TO DB, ADD DATA

@app.route('/add')

def add():
    # connect to the database

    # insert new data

    # return a message to the user
    return ""
