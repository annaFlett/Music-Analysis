
import os
from dotenv import load_dotenv
import requests
import pandas as pd
import time

load_dotenv()

artists_df = pd.read_csv(os.getenv("ARTISTS_CSV"))
artists_list = artists_df['name'].to_list()[-25:]
artists_ids = artists_df['id'].to_list()[-25:]

ENDPOINT = "https://musicbrainz.org/ws/2/artist"
HEADERS = {'User-Agent': "spotify_data_analysis/1.0.0 annabelflett@gmail.com"}

id_artists_place = []
for (id,name) in zip(artists_ids,artists_list):
    params = {'query' : name,"limit" : 1,'fmt':'json'}
    response = requests.get(ENDPOINT,headers=HEADERS,params=params)
    try: 
        country = response.json()['artists'][0]['area']['name']
        id_artists_place.append([id,name,country])
    except KeyError:
        print(id,name)
    time.sleep(1)

df = pd.DataFrame(id_artists_place,columns=["id",'name','country'])
df.to_csv("csv/artists_country2.csv")