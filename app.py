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
import os

flask_key = os.environ["flask_key"]
mongodb_username = os.environ["mongodb_username"]
mongodb_password = os.environ["mongodb_password"]



#don't forget to "pip3 install spotipy" and "sudo pip3 install dnspython" if you haven't already
# -- Initialization section --
app = Flask(__name__)

app.secret_key = flask_key
# name of database
app.config['MONGO_DBNAME'] = 'users'

# URI of database
app.config['MONGO_URI'] = f'mongodb+srv://{mongodb_username}:{mongodb_password}@cluster0.vlksj.mongodb.net/users?retryWrites=true&w=majority'


mongo = PyMongo(app)

email = "" #this variable is initialized here to avoid bugs

# -- Routes section --
# INDEX
@app.route('/')
@app.route('/index', methods = ["GET", "POST"])
def index():
    if session.get("email") == None or session["email"] != email:
        session.clear()
        return render_template("index.html")
    else:
        collection = mongo.db.profile
        user = list(collection.find({"email": session["email"]}))[0]
        session["song_ids"] = user["song_ids"]
        pfp_url = user["profile_pic_url"]
        list_of_songs = model.id_to_song(session["song_ids"])
        return render_template("overview.html", list_of_songs = list_of_songs, pfp_url = pfp_url)

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
        collection = mongo.db.profile
        user = list(collection.find({"email": session["email"]}))[0]
        session["song_ids"] = user["song_ids"]
        pfp_url = user["profile_pic_url"]
        list_of_songs = model.id_to_song(session["song_ids"]) #gives a list of dictionaries
        return render_template("overview.html", list_of_songs = list_of_songs, is_searching_songs = False, pfp_url = pfp_url)

@app.route('/soulmates')
def soulmates():
    if session.get("email") == None or session["email"] != email:
        session.clear()
        return render_template("login.html")
    else:
        collection = mongo.db.profile
        users = collection.find({})
        logined_user = list(collection.find({"email": session["email"]}))[0]
        session["song_ids"] = logined_user["song_ids"]
        p1 = model.id_to_song(session["song_ids"])
        error_message = ""
        if len(p1) < 5:
            error_message = "You must have at least 5 songs in your playlist to match with a soulmate."
            return render_template("soulmates.html", error_message = error_message)
        song_matching_users = []
        artist_matching_users = []
        genre_matching_users = []
        for user in users:
            song_percentages = {}
            artist_percentages = {}
            genre_percentages = {}
            if user["email"] != session["email"]:
                p2 = model.id_to_song(user["song_ids"])
                if len(p2) >= 5:
                    if match_score.is_matching(p1, p2, "song"):
                        song_matching_users.append(user)
                        song_percentages["match_percentage"] = match_score.match_percentage()
                        song_percentages["song_percentage"] = match_score.song_percentage()
                        song_percentages["artist_percentage"] = match_score.artist_percentage()
                        song_percentages["genre_percentage"] = match_score.genre_percentage()
                        user["song_percentages"] = song_percentages
                    if match_score.is_matching(p1, p2, "artist"):
                        artist_matching_users.append(user)
                        artist_percentages["match_percentage"] = match_score.match_percentage()
                        artist_percentages["song_percentage"] = match_score.song_percentage()
                        artist_percentages["artist_percentage"] = match_score.artist_percentage()
                        artist_percentages["genre_percentage"] = match_score.genre_percentage()
                        user["artist_percentages"] = artist_percentages
                    if match_score.is_matching(p1, p2, "genre"):
                        genre_matching_users.append(user)
                        genre_percentages["match_percentage"] = match_score.match_percentage()
                        genre_percentages["song_percentage"] = match_score.song_percentage()
                        genre_percentages["artist_percentage"] = match_score.artist_percentage()
                        genre_percentages["genre_percentage"] = match_score.genre_percentage()
                        user["genre_percentages"] = genre_percentages
            collection.update({"email": user["email"]}, {"$set": {"song_percentages": song_percentages}})
            collection.update({"email": user["email"]}, {"$set": {"artist_percentages": artist_percentages}})
            collection.update({"email": user["email"]}, {"$set": {"genre_percentages": genre_percentages}})
        return render_template("soulmates.html", song_matching_users = song_matching_users, artist_matching_users = artist_matching_users, genre_matching_users = genre_matching_users, error_message = error_message)

@app.route('/profile/song_match/<name>')
def profile_song_match(name):
    if session.get("email") == None or session["email"] != email:
        session.clear()
        return render_template("login.html")
    else:
        collection = mongo.db.profile

        #these are the variables for the person whose profile is being viewed
        user_being_searched = collection.find({"name": name})[0]
        user_being_searched_email = user_being_searched["email"]
        bio = user_being_searched["bio"]
        user_song_ids = user_being_searched["song_ids"]
        match_percentage = user_being_searched["song_percentages"]["match_percentage"]
        song_percentage = user_being_searched["song_percentages"]["song_percentage"]
        artist_percentage = user_being_searched["song_percentages"]["artist_percentage"]
        genre_percentage = user_being_searched["song_percentages"]["genre_percentage"]
        user_pfp = user_being_searched["profile_pic_url"]

        #these are the variables for the user that is logged in
        my_user = collection.find({"email": session["email"]})[0]
        my_song_ids = my_user["song_ids"]
        common_song_ids = []
        for song in user_song_ids:
            if song in my_song_ids:
                common_song_ids.append(song)
        list_of_common_songs = model.id_to_song(common_song_ids)
        return render_template("profile.html", user_pfp = user_pfp, name = name, email = user_being_searched_email, bio = bio, list_of_common_songs = list_of_common_songs, match_percentage = match_percentage, song_percentage = song_percentage, artist_percentage = artist_percentage, genre_percentage = genre_percentage)

@app.route('/profile/artist_match/<name>')
def profile_artist_match(name):
    if session.get("email") == None or session["email"] != email:
        session.clear()
        return render_template("login.html")
    else:
        collection = mongo.db.profile

        #these are the variables for the person whose profile is being viewed
        user_being_searched = collection.find({"name": name})[0]
        user_being_searched_email = user_being_searched["email"]
        bio = user_being_searched["bio"]
        user_song_ids = user_being_searched["song_ids"]
        match_percentage = user_being_searched["artist_percentages"]["match_percentage"]
        artist_percentage = user_being_searched["artist_percentages"]["artist_percentage"]
        genre_percentage = user_being_searched["artist_percentages"]["genre_percentage"]
        user_pfp = user_being_searched["profile_pic_url"]
        
        #these are the variables for the user that is logged in
        my_user = collection.find({"email": session["email"]})[0]
        my_song_ids = my_user["song_ids"]
        common_song_ids = []
        for song in user_song_ids:
            if song in my_song_ids:
                common_song_ids.append(song)
        list_of_common_songs = model.id_to_song(common_song_ids)
        return render_template("profile.html", user_pfp = user_pfp, name = name, email = user_being_searched_email, bio = bio, list_of_common_songs = list_of_common_songs, match_percentage = match_percentage, song_percentage = "", artist_percentage = artist_percentage, genre_percentage = genre_percentage)

@app.route('/profile/genre_match/<name>')
def profile_genre_match(name):
    if session.get("email") == None or session["email"] != email:
        session.clear()
        return render_template("login.html")
    else:
        collection = mongo.db.profile

        #these are the variables for the person whose profile is being viewed
        user_being_searched = collection.find({"name": name})[0]
        user_being_searched_email = user_being_searched["email"]
        bio = user_being_searched["bio"]
        user_song_ids = user_being_searched["song_ids"]
        match_percentage = user_being_searched["genre_percentages"]["match_percentage"]
        genre_percentage = user_being_searched["genre_percentages"]["genre_percentage"]
        user_pfp = user_being_searched["profile_pic_url"]
        
        #these are the variables for the user that is logged in
        my_user = collection.find({"email": session["email"]})[0]
        my_song_ids = my_user["song_ids"]
        common_song_ids = []
        for song in user_song_ids:
            if song in my_song_ids:
                common_song_ids.append(song)
        list_of_common_songs = model.id_to_song(common_song_ids)
        return render_template("profile.html", user_pfp = user_pfp, name = name, email = user_being_searched_email, bio = bio, list_of_common_songs = list_of_common_songs, match_percentage = match_percentage, song_percentage = "", artist_percentage = "", genre_percentage = genre_percentage)

@app.route('/help')
def help():
    if session.get("email") == None or session["email"] != email:
        session.clear()
        return render_template("login.html")
    else:
        return render_template("help.html")

@app.route("/profile_page")
def profile_page():
    if session.get("email") == None or session["email"] != email:
        session.clear()
        return render_template("login.html")
    else:
        error_message = ""
        collection = mongo.db.profile
        user = list(collection.find({"email": session["email"]}))[0]
        return render_template("profile_page.html", user = user, is_changing_name = False, is_changing_bio = False, is_changing_pw = False, is_changing_pfp = False, error_message = error_message)

@app.route("/change/name")
def change_name():
    if session.get("email") == None or session["email"] != email:
        session.clear()
        return render_template("login.html")
    else:
        error_message = ""
        collection = mongo.db.profile
        user = list(collection.find({"email": session["email"]}))[0]
        return render_template("profile_page.html", user = user, is_changing_name = True, is_changing_bio = False, is_changing_pw = False, is_changing_pfp = False, error_message = error_message)

@app.route("/change/bio")
def change_bio():
    if session.get("email") == None or session["email"] != email:
        session.clear()
        return render_template("login.html")
    else:
        error_message = ""
        collection = mongo.db.profile
        user = list(collection.find({"email": session["email"]}))[0]
        return render_template("profile_page.html", user = user, is_changing_name = False, is_changing_bio = True, is_changing_pw = False, is_changing_pfp = False, error_message = error_message)

@app.route("/change/pw")
def change_pw():
    if session.get("email") == None or session["email"] != email:
        session.clear()
        return render_template("login.html")
    else:
        error_message = ""
        collection = mongo.db.profile
        user = list(collection.find({"email": session["email"]}))[0]
        return render_template("profile_page.html", user = user, is_changing_name = False, is_changing_bio = False, is_changing_pw = True, is_changing_pfp = False, error_message = error_message)

@app.route("/change/pfp")
def change_pfp():
    if session.get("email") == None or session["email"] != email:
        session.clear()
        return render_template("login.html")
    else:
        error_message = ""
        collection = mongo.db.profile
        user = list(collection.find({"email": session["email"]}))[0]
        return render_template("profile_page.html", user = user, is_changing_name = False, is_changing_bio = False, is_changing_pw = False, is_changing_pfp = True, error_message = error_message)

@app.route("/update_database/name", methods = ["GET", "POST"])
def update_database_name():
    if session.get("email") == None or session["email"] != email:
        session.clear()
        return render_template("login.html")
    else:
        error_message = ""
        collection = mongo.db.profile
        user = list(collection.find({"email": session["email"]}))[0]
        if request.method == "POST":
            new_name = request.form["name"]
            session["name"] = new_name
            collection.update({"email": session["email"]}, {"$set": {"name": new_name}})
            user = list(collection.find({"email": session["email"]}))[0] #this is actually not redundant code, I have to update user so it has the new name change
        return render_template("profile_page.html", user = user, is_changing_name = False, is_changing_bio = False, is_changing_pw = False, is_changing_pfp = False, error_message = error_message)

@app.route("/update_database/bio", methods = ["GET", "POST"])
def update_database_bio():
    if session.get("email") == None or session["email"] != email:
        session.clear()
        return render_template("login.html")
    else:
        error_message = ""
        collection = mongo.db.profile
        user = list(collection.find({"email": session["email"]}))[0]
        if request.method == "POST":
            new_bio = request.form["bio"]
            session["bio"] = new_bio
            collection.update({"email": session["email"]}, {"$set": {"bio": new_bio}})
            user = list(collection.find({"email": session["email"]}))[0] #this is actually not redundant code, I have to update user so it has the new bio change
        return render_template("profile_page.html", user = user, is_changing_name = False, is_changing_bio = False, is_changing_pw = False, is_changing_pfp = False, error_message = error_message)

@app.route("/update_database/pfp", methods = ["GET", "POST"])
def update_database_pfp():
    if session.get("email") == None or session["email"] != email:
        session.clear()
        return render_template("login.html")
    else:
        error_message = ""
        collection = mongo.db.profile
        user = list(collection.find({"email": session["email"]}))[0]
        if request.method == "POST":
            new_pfp_url = request.form["pfp_url"]
            collection.update({"email": session["email"]}, {"$set": {"profile_pic_url": new_pfp_url}})
            user = list(collection.find({"email": session["email"]}))[0] #this is actually not redundant code, I have to update user so it has the new bio change
        return render_template("profile_page.html", user = user, is_changing_name = False, is_changing_bio = False, is_changing_pw = False, is_changing_pfp = False, error_message = error_message)

@app.route("/update_database/pw", methods = ["GET", "POST"])
def update_database_pw():
    if session.get("email") == None or session["email"] != email:
        session.clear()
        return render_template("login.html")
    else:
        error_message = ""
        collection = mongo.db.profile
        user = list(collection.find({"email": session["email"]}))[0]
        if request.method == "POST":
            old_pw = request.form["old_pw"]
            new_pw_1 = request.form["new_pw_1"]
            new_pw_2 = request.form["new_pw_2"]
            if bcrypt.hashpw(old_pw.encode('utf-8'), user['password'].encode('utf-8')) == user["password"].encode('utf-8'):
                if new_pw_1 == new_pw_2:
                    collection.update({"email": session["email"]}, {"$set": {"password": str(bcrypt.hashpw(new_pw_1.encode("utf-8"), bcrypt.gensalt()), 'utf-8')}})
                    user = list(collection.find({"email": session["email"]}))[0] #this is actually not redundant code, I have to update user so it has the new pw change
                    return render_template("profile_page.html", user = user, is_changing_name = False, is_changing_bio = False, is_changing_pw = False, is_changing_pfp = False, error_message = error_message)
                else:
                    error_message = "Passwords do not match."
                    return render_template("profile_page.html", user = user, is_changing_name = False, is_changing_bio = False, is_changing_pw = True, is_changing_pfp = False, error_message = error_message)
            else:
                error_message = "You did not input your old password correctly."
                return render_template("profile_page.html", user = user, is_changing_name = False, is_changing_bio = False, is_changing_pw = True, is_changing_pfp = False, error_message = error_message)

@app.route('/sign_in', methods = ["GET", "POST"])
def user_signin():
    error_message = ""
    global email
    session.clear()
    if request.method == "POST":
        email = request.form["inputEmail"]
        password = request.form["inputPassword"]
        collection = mongo.db.profile
        user = list(collection.find({"email": email}))
        if (len(user) == 0):
            error_message = "Invalid email or password."
            return render_template("login.html", error_message = error_message)
        elif bcrypt.hashpw(password.encode('utf-8'), user[0]['password'].encode('utf-8')) == user[0]["password"].encode('utf-8'):
            session["email"] = user[0]["email"]
            session["name"] = user[0]["name"]
            session["bio"] = user[0]["bio"]
            session["song_ids"] = user[0]["song_ids"]
            pfp_url = user[0]["profile_pic_url"]
            list_of_songs = model.id_to_song(session["song_ids"]) #gives a list of dictionaries
            return render_template("overview.html", list_of_songs = list_of_songs, is_searching_songs = False, pfp_url = pfp_url)
        else:
            error_message = "Invalid email or password."
            return render_template("login.html", error_message = error_message)
    else:
        return render_template("login.html")

@app.route('/store_users', methods=["GET", "POST"])
def store_users(): #this is the route for how the user creates an account
    global email
    error_message = ""
    if request.method == "POST":
        name = request.form["inputName"]
        email = request.form["inputEmail"]
        password = request.form["inputPassword"]
        collection = mongo.db.profile
        user = list(collection.find({"email": email}))
        if (len(user) == 0):
            collection.insert({"password": str(bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()), 'utf-8'), "email": email, "name": name,"bio": "I am feeling good", "profile_pic_url": "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png", "song_ids": []})
            user = list(collection.find({"email": email}))
            session["email"] = user[0]["email"]
            session["name"] = user[0]["name"]
            session["bio"] = user[0]["bio"]
            session["song_ids"] = user[0]["song_ids"]
            pfp_url = user[0]["profile_pic_url"]
            list_of_songs = model.id_to_song(session["song_ids"])
            return render_template("overview.html", list_of_songs = list_of_songs, is_searching_songs = False, pfp_url = pfp_url)
        else:
            error_message = "This email is already being used by an account."
            return render_template("signup.html", error_message = error_message)
    else:
        return render_template("signup.html")

@app.route("/search", methods = ["GET", "POST"])
def search():
    if session.get("email") == None or session["email"] != email:
        session.clear()
        return render_template("login.html")
    else:
        error_message = ""
        if request.method == "POST":
            song_query = request.form["song_query"]
            artist_query = request.form["artist_query"]
            song_ids = model.search_for_track_and_artist(song_query, artist_query) #gives a list of up to 10 song_ids that have similar names to the search query
            songs_found = model.id_to_song(song_ids) #gives a list of dictionaries
            
            collection = mongo.db.profile
            user = list(collection.find({"email": session["email"]}))[0]
            session["song_ids"] = user["song_ids"]

            if (len(songs_found) == 0):
                error_message = "No songs found"

            list_of_songs = model.id_to_song(session["song_ids"])
            pfp_url = user["profile_pic_url"]
            return render_template("overview.html", songs_found = songs_found, list_of_songs = list_of_songs, error_message = error_message, is_searching_songs = True, pfp_url = pfp_url)
        else:
            list_of_songs = model.id_to_song(session["song_ids"])
            user = list(collection.find({"email": session["email"]}))[0]
            pfp_url = user["profile_pic_url"]
            return render_template("overview.html", list_of_songs = list_of_songs, error_message = error_message, is_searching_songs = False, pfp_url = pfp_url)

@app.route("/addsong/<song_id>")
def addsong(song_id):
    if session.get("email") == None or session["email"] != email:
        session.clear()
        return render_template("login.html")
    else:
        collection = mongo.db.profile
        user = list(collection.find({"email": session["email"]}))[0]
        if song_id not in user["song_ids"]:
            collection.update({"email": session["email"]}, {"$push": {"song_ids": song_id} })
            session["song_ids"].append(song_id)
        list_of_songs = model.id_to_song(session["song_ids"])
        pfp_url = user["profile_pic_url"]
        return render_template("overview.html", list_of_songs = list_of_songs, is_searching_songs = False, pfp_url = pfp_url)

@app.route("/removesong/<song_id>")
def removesong(song_id):
    if session.get("email") == None or session["email"] != email:
        session.clear()
        return render_template("login.html")
    else:
        collection = mongo.db.profile
        collection.update({"email": session["email"]}, {"$pull": {"song_ids": song_id} })
        user = list(collection.find({"email": session["email"]}))[0]
        songs = user["song_ids"]
        session["song_ids"] = songs
        list_of_songs = model.id_to_song(session["song_ids"])
        pfp_url = user["profile_pic_url"]
        return render_template("overview.html", list_of_songs = list_of_songs, is_searching_songs = False, pfp_url = pfp_url)