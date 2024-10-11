from bs4 import BeautifulSoup
from datetime import datetime
from profile import Track
from selenium.webdriver import Chrome
import time
import pickle as pkl
import pandas as pd


def delta_time(then: datetime):
    then = datetime.strptime(then, "%Y-%m-%d").date()
    now = datetime.today().date()
    return (now - then).days


def sort_tracks_by_date(tracks):
    tracks.sort(key=lambda x: x.date)
    return tracks


def pkl_dump(obj, fname):
    with open(fname, 'wb') as f:
        pkl.dump(obj, fname)


def track_to_dict(track):
    d = {
        'Artist': track.artist,
        'Track': track.track_name,
        'Date': str(track.date),
        'URL': track.url
    }
    return d


def tracks_to_df(tracks):
    tracks = sort_tracks_by_date(tracks)
    tracks_dict = list(map(track_to_dict, tracks))
    df = pd.DataFrame(tracks_dict, columns=['Artist', 'Track', 'Date', 'URL'])
    return df


def get_user_from_url(url):
    return url[len("https://soundcloud.com/"):]


def store_data(data, filename):
    with open(filename, "w") as f:
        for index, info in enumerate(data):
            f.write(str(index) + "," + str(info) + "\n")
