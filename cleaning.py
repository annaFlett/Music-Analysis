import os
from dotenv import load_dotenv
import requests
import pandas as pd

load_dotenv()

#################################################################################################################
## GETTING INTIAL DATA
## IF MORE SONGS ARE ADDED / YOU WANT UPDATED INFO, RUN THIS SCRIPT [but ensure limit/offset are such
## that every song in the playlist is captured]

# endpoint = "https://api.spotify.com/v1/me/tracks"
# headers={f"Authorization":f"Bearer  {os.getenv("ACCESS_TOKEN")}"}

# dfs_albums = []
# dfs_artists = []
# dfs_everything = []
# ALBUM_COLS = ['a_album_type','a_artists','a_available_markets','a_external_urls','a_href','a_id','a_images','a_is_playable','a_name','a_release_date','a_release_date_precision','a_total_tracks','a_type','a_uri']


# for offset in range(0,5):
#     params = {'limit' : 49, 'offset' : offset*50}
#     response = requests.get(endpoint,headers=headers,params=params)
#     test = response.json()
#     x = test['items'][0]
#     keys = [key for key in x['track']]

#     for x in test['items']:
#         dfs_albums.append(x['track']['album'])
#         dfs_artists.append(x['track']['artists'])
#         dfs_everything.append(x['track'])


# dfs = [pd.DataFrame(df) for df in [dfs_albums,dfs_artists,dfs_everything]]
# dfs_for_concat =[pd.DataFrame(df) for df in dfs]
# df_concatted = pd.concat(dfs_for_concat,axis=1)
# df_concatted.columns = ALBUM_COLS  + list(df_concatted.columns[len(ALBUM_COLS):])
# df_concatted.to_csv(path_or_buf='songs.csv')

# songs = pd.read_csv('songs.csv',index_col=0)
# songs.drop(labels=['album','artists'],inplace=True,axis=1)
# songs.to_csv(path_or_buf='songs.csv')
#################################################################################################################

