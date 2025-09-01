

import os
from dotenv import load_dotenv
import requests
import pandas as pd

load_dotenv()

ENDPOINT = "https://api.reccobeats.com/v1/audio-features"
HEADERS = {'Accept': 'application/json'}
params = {'ids' : ['1bx7OUl2UmAnA5oZkm9If7']}
response = requests.get(ENDPOINT,headers=HEADERS,params=params)
print(response.status_code)
print(response.json())

# songs_df = pd.read_csv(os.getenv("SONGS_CSV"),index_col=0)
# ids = songs_df['id'].to_list()
# ids_chunked = [ids[i:i+40] for i in range(0,len(ids)+1,40)]
# df = []

# counter = 0
# counter2 = 0
# for songs in ids_chunked:
#     counter2 += len(songs)
#     params = {'ids' : songs}
#     response = requests.get(ENDPOINT,headers=HEADERS,params=params)
#     print(response.status_code)
#     stats = response.json()['content']
#     for x in stats:
#         counter +=1
#         df.append(x)

# song_stats = pd.DataFrame(df)
# song_stats['spotify_id'] = song_stats['href'].apply(lambda x : x[31:])
# # song_stats.to_csv("csv/song_stats.csv")

# # stats = pd.read_csv("csv/song_stats.csv",index_col=0)
# # songs = pd.read_csv("csv/songs.csv",index_col=0)
# x = pd.merge(left=songs_df,right=song_stats,left_on='id',right_on='spotify_id',how='left')
# print(x.columns)
# print(x[['id_x','spotify_id']])
# na_ids = (x[x['spotify_id'].isna()]['id_x']).rename('spotify_id')
# print(na_ids)
# y = pd.concat([song_stats,na_ids],axis=0)
# print(y.columns)
# y.to_csv("csv/song_stats.csv")

