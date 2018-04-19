import json
from collections import OrderedDict
from pprint import pprint

from pymongo import MongoClient
import os
from spotipy import Spotify
from spotipy import util

PLAYLIST_NAME = "Archived Discover Weekly"
SCOPE = 'playlist-modify-private'
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
    play_list_names = songs_db.find_one({"_id": "playlist-names"})
    if (songs_db.find({"_id": play_list_names}).count() == 1) and (
            PLAYLIST_NAME not in play_list_names):
        sp.user_playlist_create(user=USERNAME, name=PLAYLIST_NAME, public=False)

    songs_list = []
    for i in songs_db.find({"_id": {"$ne": "playlist-names"}}):
        songs_list.extend(i["songs"])
    songs_list = list(OrderedDict.fromkeys(songs_list))
    sp.user_playlist_replace_tracks(user=USERNAME, playlist_id=play_list_names[PLAYLIST_NAME], tracks=songs_list)
