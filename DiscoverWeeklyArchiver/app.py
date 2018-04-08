import io
import os
import pickle
from pathlib import Path
from urllib.request import urlopen

import xlsxwriter
from spotipy import Spotify
from spotipy import util

PLAYLIST_NAME = "Discover Weekly"
SCOPE = 'playlist-read-private'
USERNAME = os.environ.get("SPOTIFY_USERNAME")
CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("SPOTIFY_REDIRECT_URI")
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
SONGS_DB = Path(os.path.join(BASE_DIR, "songs_db.pickle"))
EXCEL_FILE = Path(os.path.join(BASE_DIR, "DiscoverWeekly.xlsx"))
EXCEL_HEADERS = ["Cover", "Song Name", "Artists", "Date Added", "Song ID"]


class SongNode:
    def __init__(self, song_id, name, artists, added_at, cover):
        self.id = song_id
        self.name = name
        self.artists = artists
        self.added_at = added_at
        self.cover = cover

    def get_artists(self):
        return ", ".join(self.artists)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "{0} - {1}".format(self.name, self.artists)


if __name__ == "__main__":
    token = util.prompt_for_user_token(username=USERNAME,
                                       scope=SCOPE,
                                       client_id=CLIENT_ID,
                                       client_secret=CLIENT_SECRET,
                                       redirect_uri=REDIRECT_URI)
    if token:
        sp = Spotify(auth=token)
        discover_id = ""
        for i in sp.current_user_playlists()["items"]:
            if i["name"] == "Discover Weekly":
                discover_id = i["id"]

        if discover_id:
            results = sp.user_playlist_tracks(user="spotify", playlist_id=discover_id)
            song_nodes = []
            song_dict = {}
            for song in results["items"]:
                song_nodes.append(SongNode(
                    song_id=song["track"]["id"],
                    name=song["track"]["name"],
                    artists=tuple(artist["name"] for artist in song["track"]["artists"]),
                    added_at=song["added_at"],
                    cover=song["track"]["album"]["images"][0]["url"]
                ))

            if SONGS_DB.is_file():
                with open(SONGS_DB, 'rb') as f:
                    song_dict = pickle.load(f)
            song_dict[song_nodes[0].added_at] = song_nodes
            with open(SONGS_DB, 'wb') as handle:
                pickle.dump(song_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

            workbook = xlsxwriter.Workbook(EXCEL_FILE)
            format_book = workbook.add_format()
            format_book.set_align('center')
            format_book.set_align('vcenter')
            worksheet = workbook.add_worksheet(name="Songs")
            worksheet.write_row("A1", EXCEL_HEADERS, format_book)
            i = 2
            for date in sorted(song_dict, reverse=True):
                for node in song_dict[date]:
                    url = node.cover
                    cover_img = io.BytesIO(urlopen(url).read())
                    worksheet.set_row(i - 1, 130)
                    worksheet.write_row("B" + str(i), (node.name, node.get_artists(), date[:10], node.id), format_book)
                    worksheet.insert_image('A' + str(i), url, {'image_data': cover_img,
                                                               'x_scale': 0.2,
                                                               'y_scale': 0.2,
                                                               'positioning': 1})
                    i += 1
            worksheet.set_column(0, 0, 25)
            worksheet.set_column(1, 2, 60)
            worksheet.set_column(3, 3, 15)
            worksheet.set_column(4, 4, 30)
            workbook.close()

    else:
        print("Can't get token for", USERNAME)
