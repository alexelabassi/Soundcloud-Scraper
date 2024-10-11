# %%
from profile import User, Track
import math
from helper import *
from multiprocessing import Pool


class Tab:
    def __init__(self, driver, username, scroll_pause_time=1, open_tab=1, handle=-1, url=None):
        self.driver = driver
        self.username = username
        self.scroll_pause_time = scroll_pause_time
        if not url:
            self.url = "https://soundcloud.com/" + username
        else:
            self.url = url
        if open_tab:
            self.open_tab(handle)

    def open_tab(self, handle=-1):
        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[handle])
        self.driver.get(self.url)

    def scroll(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Scroll down
        time.sleep(self.scroll_pause_time)
        new_height = self.driver.execute_script("return document.body.scrollHeight")

        return not new_height == last_height


class FollowingTab(Tab):
    """
    Tabs opened with a username to scrape their recently posted songs
    """

    def __init__(self, driver, username, scroll_depth):
        super().__init__(driver, username, open_tab=False)
        self.username = username
        self.url = "https://soundcloud.com/" + username + "/tracks"
        self.driver.get(self.url)
        self.scroll_depth = scroll_depth
        time.sleep(3)  # Wait until it's done loading the profile
        self.tracks = self.get_tracks()

    def scrape_tracks(self):
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        sound_contents = soup.find_all('div', class_="sound__content")
        tracks = []
        for content in sound_contents:
            basic_inf = content.find('a', class_="soundTitle__title sc-link-dark sc-link-primary")
            title, url = basic_inf.get_text(), basic_inf.get('href')
            date = content.find('time', class_="relativeTime").get('datetime').split('T')[0]
            tracks.append(Track(url, date, title, self.username))
        return tracks

    def get_tracks(self):
        counter = 0
        while self.scroll() and counter < self.scroll_depth:
            counter += 1
        tracks = self.scrape_tracks()
        return tracks

    def get_tracks_before_date(self, delta_diff=30):
        tracks = [track for track in self.tracks if delta_time(track.date) < delta_diff]
        return tracks

    def __str__(self):
        string = "*" * 20 + "\n" + f"username:{self.username}"
        for track in self.tracks:
            string += "\n" + str(track)
        return string


class InitTab(Tab):
    def __init__(self, driver, username, load=True):
        super().__init__(driver, username, open_tab=0)
        self.url = "https://soundcloud.com/" + self.username + "/following"
        self.open_tab()
        self.followers = self.get_followers() if load else []

    def get_followers(self, scroll_depth=100):
        followers = []
        counter = 0

        while self.scroll() and counter < scroll_depth:
            counter += 1
        followers.extend(self.driver.find_elements_by_class_name("userBadgeListItem__image"))
        followers = [elem.get_attribute('href') for elem in followers]

        return followers

    def __str__(self):
        string = "" * 20 + "\n" + f"USERNAME:{self.username}"
        for follower in self.followers:
            string += "\n" + str(follower)
        return string


class TabManager:
    time_diff = 30

    def __init__(self, urls, scroll_depth=5, date_diff=100):
        self.driver = Chrome()
        self.date_diff = date_diff
        self.urls = urls
        self.scroll_depth = scroll_depth
        self.tracks = self.open_tabs()
        self.driver.quit()

    def open_tabs(self):
        all_tracks = []
        for idx, url in enumerate(self.urls):
            username = get_user_from_url(url)
            following_tab = FollowingTab(self.driver, username, self.scroll_depth)
            tracks = following_tab.get_tracks_before_date(self.date_diff)
            if tracks:
                all_tracks.extend(tracks)
            if idx > self.scroll_depth:
                break

        print(f'Finished opening tabs, found {len(all_tracks)}')
        return all_tracks


class Manager:
    def __init__(self, username, cores, scroll_depth=2, cached_following=False, date_diff=100):
        if cached_following:
            self.followers = pd.read_csv('followers.txt')['url']
        else:
            self.followers = InitTab(Chrome(), username).followers
            pd.DataFrame(self.followers).to_csv('cached/followers.txt')
        self.scroll_depth = scroll_depth
        self.chunk_size = math.ceil(len(self.followers) / cores)
        self.date_diff = date_diff

        self.collected_tracks = []
        splits = self.split_followers()
        with Pool(cores) as p:
            tracks = list(p.map(self.tab_job, splits))
        self.collected_tracks = [track for sublist in tracks for track in sublist]

    def tab_job(self, followers):
        tab_manager = TabManager(followers, self.scroll_depth, self.date_diff)
        return tab_manager.tracks

    def split_followers(self):
        return [self.followers[idx:idx + self.chunk_size] for idx in range(0, len(self.followers), self.chunk_size)]

    def load_urls(self):
        driver = Chrome()
        for track in self.collected_tracks:
            tab = Tab(driver, track.url)
