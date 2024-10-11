from tabs import Manager
from helper import tracks_to_df

if __name__ == "__main__":
    username = input("Type your username:")

    manager = Manager(username=username, cores=10, cached_following=False, date_diff=100)
    df = tracks_to_df(manager.collected_tracks)
    df.to_csv('cached/collected.txt')
