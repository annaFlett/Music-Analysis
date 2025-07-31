import pandas as pd
import requests
import http
import os
from dotenv import load_dotenv
import time
import datetime

load_dotenv()


endpoint = "https://api.spotify.com/v1/me/player/recently-played"
headers={f"Authorization":f"Bearer  {os.getenv("ACCESS_TOKEN")}"}
CSV_PATH = "songhistory.csv"

dfs_albums = []
dfs_artists = []
dfs_everything = []
dfs_played_at = []
dfs_context = []
ALBUM_COLS = ['a_album_type','a_artists','a_available_markets','a_external_urls','a_href','a_id','a_images','a_name','a_release_date','a_release_date_precision','a_total_tracks','a_type','a_uri']
ARTIST_COLS = ['art_external_urls','art_href','art_id','art_name','art_type','art_uri']




stamp = 1735678800 ## 22:00, 31st December 2024
stamp = time.time() ## 6:00 29th July 2025

params = {
        'after' : int(stamp),
        'limit' : 50
    }

i = 0
while i < 5:
    print(stamp)
    print(i)

    response = requests.get(url=endpoint,headers=headers,params=params)
    print(response.status_code)
    test = response.json()
    if test['items'] == []:
        break
        
    print(stamp)
    print(test['cursors'])
    print(test['next'])
    stamp = test['cursors']['before']
    params = {
        'before' : int(stamp),
        'limit' : 50
    }
    print(stamp)

    for x in response.json()['items']:
        dfs_albums.append(x['track']['album'])
        dfs_artists.append(x['track']['artists'])
        dfs_everything.append(x['track'])
        dfs_played_at.append(x['played_at'])
        dfs_context.append(x['context'])
    print (datetime.datetime.fromtimestamp(int(int(stamp)/1000)))
    i += 1

try:
    dfs_artists = list(map(lambda x : x[0],dfs_artists))
    dfs = [pd.DataFrame(df) for df in [dfs_albums,dfs_artists,dfs_everything,dfs_context,dfs_played_at]]
    dfs_for_concat =[pd.DataFrame(df) for df in dfs]
    df_concatted = pd.concat(dfs_for_concat,axis=1)
    df_concatted.columns = ALBUM_COLS  + ARTIST_COLS + list(df_concatted.columns[len(ALBUM_COLS)+len(ARTIST_COLS):-2]) + ['context','played_at']
    df_concatted.to_csv(path_or_buf=CSV_PATH)

    songs = pd.read_csv(CSV_PATH,index_col=0)
    songs.drop(labels=['album'],inplace=True,axis=1)
    songs.to_csv(path_or_buf=CSV_PATH)
except ValueError:
    print("No songs found")


print(f"CURRENT TIME : {time.time()}")