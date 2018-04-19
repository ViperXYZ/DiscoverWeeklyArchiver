from pprint import pprint

from pymongo import MongoClient
import os
from spotipy import Spotify
from spotipy import util

PLAYLIST_NAME = "Discover Weekly"
SCOPE = 'playlist-read-private'
USERNAME = '22kdwq5kpcai6vnmcv45nnzbi'
CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("SPOTIFY_REDIRECT_URI")
DB_CLIENT = MongoClient()
DB = DB_CLIENT["spotyapps"]
songs_db = DB["discoverweekly"]

token = util.prompt_for_user_token(username=USERNAME,
                                   scope=SCOPE,
                                   client_id=CLIENT_ID,
                                   client_secret=CLIENT_SECRET,
                                   redirect_uri=REDIRECT_URI)

if token:
    sp = Spotify(auth=token)
    playlist_dict = {i["name"]: i["id"] for i in sp.current_user_playlists()["items"]}
    playlist_dict["_id"] = "playlist-names"
    if songs_db.find({"_id": "playlist-names"}).count() == 0:
        songs_db.insert_one(playlist_dict)
    elif songs_db.find({"_id": "playlist-names"}).count() == 1:
        songs_db.replace_one({"_id": "playlist-names"}, playlist_dict)
    else:
        raise Exception("duplicate playlist document")

    if PLAYLIST_NAME in playlist_dict:
        results = sp.user_playlist_tracks(user="spotify", playlist_id=playlist_dict[PLAYLIST_NAME])
        song_list = [song["track"]["id"] for song in results["items"]]

        song_dict = {
            "_id": results["items"][0]["added_at"],
            "songs": song_list
        }
        if songs_db.find({'_id': song_dict['_id']}).count() == 0:
            songs_db.insert_one(song_dict)
        else:
            print("SONG DICT ALREADY EXISTS")

else:
    print("Can't get token for", USERNAME)
