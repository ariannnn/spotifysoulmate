import match_score

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

cid = '2aec1864fdb0443da8ea4f23b250f72b'
secret = '8100126adef24003b819e136fbc13afe'
client_credentials_manager = SpotifyClientCredentials(
    client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

#Returns the top 10 tracks from an artist based on artist name parameter
def get_top_tracks(artist): 
    data = sp.search(q="artist:" + artist, type="artist")
    uri = data["artists"]["items"][0]["uri"]
    results = sp.artist_top_tracks(uri)
    top_tracks = []
    for track in results["tracks"][:10]:
        top_tracks.append(track["id"],)
    return top_tracks
# print(get_top_tracks("kanye"))

#Returns 10 tracks from an artist based on artist name parameter
def search_for_artist(artist):
    top_10_ids = []
    data = sp.search(q="artist:" + artist, limit = 10, type="artist")
    for track in data["artists"]["items"]:
        top_10_ids.append(track["id"])
    return top_10_ids
# print(search_for_artist("kanye"))

#Returns all the songs in an album based on album name parameter
def search_for_album(album):
    album_track_ids = []
    data = sp.search(q="album:" + album, limit = 1, type="album")
    album_id = data["albums"]["items"][0]["id"]
    result = sp.album_tracks(album_id, limit=50, offset=0, market=None)
    for track in result["items"]:
        album_track_ids.append(track["id"])
    return album_track_ids

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
        song_list.append({"track_name": track_name, "track_artists": track_artists, "artist_genres": artist_genres, "track_album_name": track_album_name, "album_art_url": album_art_url})
    return song_list
#print(search_for_track("I am a God"))