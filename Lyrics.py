import requests
import lyricsgenius
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()
GENIUS_API_KEY = os.getenv('GENIUS_API_KEY')


# With requests library (Returns Link)
def Search_Song_Link(song):
    base_url = 'https://api.genius.com'
    headers = {'Authorization': f'Bearer {GENIUS_API_KEY}'}
    params = {'q': song}
    response = requests.get(f'{base_url}/search', params=params, headers=headers)

    results = response.json()['response']['hits']
    for r in results[:3]:
        print(f'{r["result"]["full_title"]}')
        print(f'Artist = {r["result"]["artist_names"]}')
        print(f'{r["result"]["url"]}')


def Song_Artist(song):
    base_url = 'https://api.genius.com'
    headers = {'Authorization': f'Bearer {GENIUS_API_KEY}'}
    params = {'q': song}
    response = requests.get(f'{base_url}/search', params=params, headers=headers)

    results = response.json()['response']['hits']
    for r in results[:1]:
        return r["result"]["artist_names"]


# With lyricsgenius library (Returns Lyrics)
genius = lyricsgenius.Genius(access_token=GENIUS_API_KEY)
genius.skip_non_songs = True
genius.verbose = False


def Search_Song_Lyrics(song_name):
    try:
        song = genius.search_song(song_name, get_full_info=False)
        if song:
            return song.lyrics

        else:
            print('The song was not found! :(')
    except Exception as e:
        print(f'An error Occurred :( \n{e}')


def Search_Song_Through_Link(url):
    if 'genius.com' not in url:
        print('This method only works with links from Genius.com')
        return

    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    lyrics_div = soup.find('div', class_='lyrics')

    # Sometimes the class name is data-lyrics-container
    if not lyrics_div:
        lyrics_divs = soup.find_all('div', {'data-lyrics-container': 'true'})
        lyric = '\n'.join([lyrics.get_text() for lyrics in lyrics_divs])

    else:
        lyric = lyrics_div.get_text()

    return lyric
