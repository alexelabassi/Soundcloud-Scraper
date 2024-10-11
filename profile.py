class User:
    def __init__(self, username, user_type, follow_list=None, tracks=None):
        # user_type="follow_list" or "init"
        self.username = username
        self.user_type = user_type

        if user_type == "init":
            self.url = "https://soundcloud.com/" + username + "/follow_list"
        elif user_type == "follow_list":
            self.url = "https://soundcloud.com/" + username + "/tracks"
        else:
            raise Exception("Invalid user type!")
        self.follow_list = follow_list
        self.tracks = tracks


class Track:
    def __init__(self, url, date, track_name="", artist=""):
        self.url = url
        self.artist = artist
        self.date = date
        self.track_name = track_name.strip('\n')

    def __str__(self) -> str:
        return self.artist + "-" + self.track_name + " Date=" + self.date

    def __repr__(self):
        return self.artist + "-" + self.track_name + " Date=" + self.date
