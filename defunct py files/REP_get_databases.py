import os
from dotenv import load_dotenv
import requests
import pandas as pd

load_dotenv()

def extract_ids(rows,arr):
    artists,id = rows
    for artist in artists:
        arr.append((artist['id'],id))

#################################################################################################################
## GETTING INTIAL DATA
## IF MORE SONGS ARE ADDED / YOU WANT UPDATED INFO, RUN THIS SCRIPT [but ensure limit/offset are such
## that every song in the playlist is captured]

ENDPOINT = "https://api.spotify.com/v1/me/tracks"
HEADERS={f"Authorization":f"Bearer  {os.getenv("ACCESS_TOKEN")}"}
ALBUMS_PATH = os.getenv("ALBUMS_CSV")
ARTISTS_PATH = os.getenv("ARTISTS_CSV")
SONGS_PATH = os.getenv("SONGS_CSV")
ARTISTS_ALBUMS_PATH = os.getenv("ARTIST_ALBUMS_CSV")
ARTISTS_SONGS_PATH = os.getenv("ARTISTS_SONGS_CSV")

collection , art_song_pairs , alb_art_pairs = [] , [] , []

for offset in range(0,5):
    params = {'limit' : 49, 'offset' : offset*50}
    response = requests.get(ENDPOINT,headers=HEADERS,params=params)
    print(response.status_code)
    for x in response.json()['items']:
        collection.append(x['track'])


## Get Albums database
# dfs_albums = [x['album'] for x in collection]
# albums = pd.DataFrame(df for df in dfs_albums)
# albums[['artists','id']].apply(lambda x : extract_ids(x,alb_art_pairs),axis=1) # for albums-artists
# albums['external_urls'] = albums['external_urls'].apply(lambda x : x['spotify'])
# albums.drop(columns=['artists'],inplace=True,axis=1)
# albums.to_csv(path_or_buf = ALBUMS_PATH)

## Get albums-artists database
# art_albs = pd.DataFrame(alb_art_pairs,columns=["ArtistId","AlbumId"])
# art_albs.to_csv(path_or_buf = ARTISTS_ALBUMS_PATH)

## Get artists database
# artists =  []
# dfs_artists = [x['artists'] for x in collection]
# for x in dfs_artists:
#     for artist in x:
#         artists.append(pd.DataFrame(artist))
# artists_expanded = pd.concat(artists)
# artists_expanded.to_csv(path_or_buf = ARTISTS_PATH)

## Get songs database

# songs = pd.DataFrame(df for df in collection)
# songs['album_id']= songs['album'].apply(lambda x : x['id'])
# songs[['artists','id']].apply(lambda x : extract_ids(x,art_song_pairs),axis=1)
# songs['external_urls'] = songs['external_urls'].apply(lambda x : x['spotify'])
# songs['isrc'] = songs['external_ids'].apply(lambda x : x['isrc'])
# songs.drop(columns=['album','artists','external_ids'],inplace=True,axis=1)
# songs.to_csv(path_or_buf = SONGS_PATH)

# artists_songs = pd.DataFrame(art_song_pairs,columns=["ArtistId","SongId"])
# artists_songs.to_csv(path_or_buf = ARTISTS_SONGS_PATH)

################################################################################################################

