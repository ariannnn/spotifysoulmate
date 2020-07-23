#playlist1 should be the user's playlist and playlist2 should be the playlist of whoever the user is trying to match with
def match_score_by_song(p1, p2):
    #songs
    global song_score
    song_score = 0
    #loop through playlist1 and see if the song in playlist1 can be located in playlist2. If so, add a score of 3.
    for song in p1:
        if song in p2:
            song_score += 3


    #artists
    #creates a dictionary of the artists in playlist1 and playlist2 to remove duplicate artists in entries
    global artist_score
    artist_score = 0
    p1_artists = {}
    for song in p1:
        p1_artists[song["artist"]] = "any_value"

    p2_artists = {}
    for song in p2:
        p2_artists[song["artist"]] = "any_value"

    #loop through p1_artists and see if the artist in playlist1 can be located in playlist2. If so, add a score of 2.
    for artist in p1_artists:
        if artist in p2_artists:
            artist_score+= 2


    #genres
    #creates a dictionary of the genres in playlist1 and playlist2 to remove duplicate genres in entries
    global genre_score
    genre_score = 0
    p1_genres = {}
    for song in p1:
        p1_genres[song["genre"]] = "any_value"

    p2_genres = {}
    for song in p2:
        p2_genres[song["genre"]] = "any_value"

    #loop through p1_genres and see if the genre in playlist1 can be located in playlist2. If so, add a score of 1.
    for genre in p1_genres:
        if genre in p2_genres:
            genre_score+= 1

    
    #calculates maximum match score for the user, max_score should always be >= total_score
    global max_score
    max_score = 3 * len(p1) + 2 * len(p1_artists) + 1 * len(p1_genres)
    
    global total_score
    total_score = song_score + artist_score + genre_score

    if (max_score < total_score):
        return "Error: Max score is somehow lower than total score, which shouldn't happen."
    
    return total_score

#returns match_percentage in percent form
def match_percentage(total_score, max_score):
    return str(round(total_score / max_score * 100, 2)) + "%"

#returns how much the matching songs in p1 and p2 contributed to the match_percentage.
#for example, if match_percentage outputted 50%, and half of that 50% came from songs, then song_percentage would be 25%
def song_percentage(song_score, total_score, match_percentage):
    return str(round(song_score / max_score * 100, 2)) + "%"

def artist_percentage(artist_score, total_score, match_percentage):
    return str(round(artist_score / max_score * 100, 2)) + "%"

def genre_percentage(genre_score, total_score, match_percentage):
    return str(round(genre_score / max_score * 100, 2)) + "%"


#test cases
# p1 = [
#     {"name":"Red", "artist": "Taylor Swift", "genre":"idk"},
#     {"name":"Cruel Summer", "artist": "Taylor Swift", "genre": "idk"}
# ]

# p2 = [
#     {"name":"Red", "artist": "Taylor Swift", "genre":"idk"},
#     {"name":"Style", "artist": "Taylor Swift", "genre":"idk"},
#     {"name":"Wildest Dreams", "artist": "Taylor Swift", "genre":"idk"},
#     {"name":"Paradise", "artist": "Bazzi", "genre":"idk"}
# ]

# print(match_score_by_song(p2, p1)) #should output 6
# match_percentage = match_percentage(total_score, max_score) 
# print(match_percentage) 
# print(song_percentage(song_score, total_score, match_percentage)) 
# print(artist_percentage(artist_score, total_score, match_percentage)) 
# print(genre_percentage(genre_score, total_score, match_percentage)) 