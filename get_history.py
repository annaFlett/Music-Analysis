import pandas as pd
import requests
import os
from dotenv import load_dotenv,set_key
from pathlib import Path
from subprocess import Popen

load_dotenv()

p  = Popen(['python',os.getenv('AUTH_PATH')])
p.wait()

endpoint = "https://api.spotify.com/v1/me/player/recently-played"
headers={f"Authorization":f"Bearer  {os.getenv("ACCESS_TOKEN")}"}
CSV_PATH = os.getenv("CSV_PATH_SONG_HISTORY")
dfs_everything,dfs_context,dfs_played_at = [],[],[]

params = {
        'after' : str(os.getenv("PREV_SEARCH")),
        'limit' : 50,
    }

response = requests.get(url=endpoint,headers=headers,params=params)
print(response.status_code)
print(response.text)
test = response.json()
    
if test['cursors'] != None:
    set_key(os.getenv("ENV_PATH"), 'PREV_SEARCH', response.json()['cursors']['after'])

for x in response.json()['items']:
    dfs_everything.append(x['track'])
    dfs_played_at.append(x['played_at'])
    dfs_context.append(x['context'])

try:
    songs,context,played_at = [pd.DataFrame(df) for df in [dfs_everything,dfs_context,dfs_played_at]]
    context.rename(columns={0:'context'},inplace=True)
    played_at.rename(columns={0:'played_at'},inplace=True)
    songs['album_id']= songs['album'].apply(lambda x : x['id'])
    songs['external_urls'] = songs['external_urls'].apply(lambda x : x['spotify'])
    songs['isrc'] = songs['external_ids'].apply(lambda x : x['isrc'])

    songs.drop(columns=['album','artists','external_ids'],inplace=True,axis=1)
    new_songs = pd.concat([songs,context,played_at],axis = 1)

    history = pd.read_csv(CSV_PATH,index_col=0)
    total_history = pd.concat([new_songs,history],axis=0)
    total_history.to_csv(path_or_buf = CSV_PATH)

except (ValueError,KeyError):
    print("No songs found")



