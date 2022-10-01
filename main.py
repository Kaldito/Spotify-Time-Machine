from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from decouple import config

BASE_URL = "https://www.billboard.com/charts/hot-100/"
CLIENT_ID = config("CLIENT_ID")
CLIENT_SECRET = config("CLIENT_SECRET")


def best_songs():
    date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")
    year = date.split("-")[0]
    complete_url = f"{BASE_URL}{date}"

    response = requests.get(complete_url)
    website = response.text

    soup = BeautifulSoup(website, "html.parser")

    songs = [tag.get_text() for tag in soup.find_all(name="h3", id="title-of-a-story", class_="a-no-trucate")]
    songs_complete = []

    # Formatting the song
    for song in songs:
        name = ""
        finish = len(song) - 5

        # Starts in the character 14 and finishes 6 characters before the end.
        for i in range(14, finish):
            letter = song[i]
            name += letter

        songs_complete.append(name)

    results = {
        "songs": songs_complete,
        "year": year,
        "date": date,
    }

    return results


# Spotify API
scope = "playlist-modify-private"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               scope=scope,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri="http://example.com"))

user_id = sp.current_user()["id"]

song_func = best_songs()

songs = song_func["songs"]
year = song_func["year"]
date = song_func["date"]
url_list = []

for song in songs:
    url = sp.search(q=f"track:{song} year:{year}", limit=1, type="track", market="MX")
    try:
        url_list.append(url["tracks"]["items"][0]["external_urls"]["spotify"])
    except IndexError:
        print(f"{song} not founded in spotify.")

playlist = sp.user_playlist_create(user=user_id, name=f"{date} Billboard 100")
playlist_id = playlist["id"]

sp.playlist_add_items(playlist_id=playlist_id, items=url_list)


