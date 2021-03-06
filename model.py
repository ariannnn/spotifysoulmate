import match_score

from flask import Flask
from flask import render_template
from flask import request
from flask_pymongo import PyMongo
import requests
import os

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials



mongodb_username = os.environ["mongodb_username"]
mongodb_password = os.environ["mongodb_password"]

cid = os.environ["spotify_cid"]
secret = os.environ["spotify_secret"]

client_credentials_manager = SpotifyClientCredentials(
    client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# -- Initialization section --
app = Flask(__name__)

# name of database
app.config['MONGO_DBNAME'] = 'users'

# URI of database
app.config['MONGO_URI'] = f'mongodb+srv://{mongodb_username}:{mongodb_password}@cluster0.vlksj.mongodb.net/users?retryWrites=true&w=majority'

mongo = PyMongo(app)

#Returns the top 10 tracks from an artist based on artist name parameter
def get_top_tracks(artist): 
    data = sp.search(q="artist:" + artist, type="artist")
    uri = data["artists"]["items"][0]["uri"]
    results = sp.artist_top_tracks(uri)
    top_tracks = []
    for track in results["tracks"][:10]:
        top_tracks.append(track["id"],)
    return top_tracks

#Returns 10 tracks from an artist based on artist name parameter
def search_for_artist(artist):
    top_10_ids = []
    data = sp.search(q="artist:" + artist, limit = 10, type="artist")
    for track in data["artists"]["items"]:
        top_10_ids.append(track["id"])
    return top_10_ids

#Returns all the songs in an album based on album name parameter
def search_for_album(album):
    album_track_ids = []
    data = sp.search(q="album:" + album, limit = 1, type="album")
    album_id = data["albums"]["items"][0]["id"]
    result = sp.album_tracks(album_id, limit=50, offset=0, market=None)
    for track in result["items"]:
        album_track_ids.append(track["id"])
    return album_track_ids

#Returns a list of songs that match the track name and artist name paramters. (updated)
def search_for_track_and_artist(track, artist):
    data_tracks = sp.search(q="track:" + track, limit = 35, type="track")
    result = []
    for track in data_tracks["tracks"]["items"]:
        for artist_dict in track["artists"]:
            if artist_dict["id"] in search_for_artist(artist):
                result.append(track["id"])
    return result

#Returns 10 similarly-named tracks based on track name parameter
def search_for_track(track):
    top_10_ids = []
    data = sp.search(q="track:" + track, limit = 10, type="track")
    for track in data["tracks"]["items"]:
        top_10_ids.append(track["id"])
    return top_10_ids


#Converts a list of track IDs to a dictionary
def id_to_song(id_list):
    song_list = []
    for id_ in id_list:
        data = sp.track(id_)
        track_album_name = data["album"]["name"]
        track_artists = []
        track_name = data["name"]
        album_art_url = data["album"]["images"][0]["url"]
        for artist in data["album"]["artists"]:
            track_artists.append([artist["name"], artist["id"]])
        artist_genres = []
        for artist_id in track_artists:
            for genre in sp.artist(artist_id[1])["genres"]:
                artist_genres.append(genre)
        song_list.append({"track_name": track_name, "track_artists": track_artists, "artist_genres": artist_genres, "track_album_name": track_album_name, "album_art_url": album_art_url, "song_id": id_})
    return song_list

def get_user_info(email):
    collection = mongo.db.profile
    profiles = collection.find({})
    user_info = {"password":"", "email":"", "name":"", "bio":"", "song_ids":[]}
    for profile in profiles:
        if(profile["email"] == email):
            user_info = profile
    return user_info