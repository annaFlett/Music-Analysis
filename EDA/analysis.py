import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import datetime
from dotenv import load_dotenv

load_dotenv()

def account_for_germany(x):
    if x.replace(tzinfo=None) < datetime.datetime(year=2025,month=8,day=9,hour=18):
        return x + datetime.timedelta(hours=1)
    return x

history = pd.read_csv(os.getenv("SONGHISTORY_CSV"))
art_song = pd.read_csv(os.getenv("ARTISTS_SONGS_CSV"),index_col=0)
songs = pd.read_csv(os.getenv("SONGS_CSV"))
artists = pd.read_csv(os.getenv("ARTISTS_CSV"))
history.drop(columns=['preview_url'],inplace=True)

history['played_at'] = pd.to_datetime(history['played_at'])
history = history[history['played_at'].dt.date > datetime.datetime(year=2025,month=8,day=1).date()]
history['played_at'] = history['played_at'].apply(lambda x : account_for_germany(x))

history['date'] = history['played_at'].apply(lambda x : x.replace(minute=0,second=0,hour=0,microsecond=0))
print(history.groupby('date')['played_at'].idxmin())
# print(history.loc[history.groupby('date')['played_at'].idxmin()][['name','played_at']])
# print(history)
# history['id_lagged'] = history['id'].shift(-1)
# print(history[['id','id_lagged']])
# history = history.loc[history['id'] != history['id_lagged']]
# history.drop(columns=['id_lagged'],inplace=True)
# print(history)


# history['days'] = history['played_at'].apply(lambda x : datetime.datetime(year=x.year,month=x.month,day=x.day))
# print(history.tail())
# print(round(history.groupby('days').size().mean(),2))

# seven_days_back = (datetime.datetime.today() - datetime.timedelta(days=7)).replace(tzinfo=datetime.timezone.utc)
# print(seven_days_back)
# history = history[history['played_at'] > seven_days_back]
# print(history.shape[0])
# print(history.head()
# print(history.columns)
# print(history.info())

# print(history.sort_values(by="popularity",ascending=False).head()['name'])
# song_id = (history.loc[history["name"] == "undressed",'id']).tolist()[0]
# print(song_id)

# def check_if_song_in_db(x):
#     art_id = art_song.loc[art_song['SongId'] == x, "ArtistId"]
#     print(art_id)
#     return art_id.empty

# history['needs_api'] = history['id'].apply(lambda x : check_if_song_in_db(x))
# print(art_song.loc[art_song['SongId'] == song_id, "ArtistId"])

# print(history[history['needs_api'] == True][['name','id']])

# time_s = (songs['duration_ms'].mean()/1000)
# print(f"Average liked song duration:  {int(time_s // 60)}m {round(time_s % 60)}s")

# grouped_by_artists = art_song.groupby(by=["ArtistId"])
# most_popular = pd.Series(grouped_by_artists['SongId'].count().nlargest(n=10).index)
# print(most_popular)
# artists_names = artists[['name','id']].drop_duplicates()
# x = pd.merge(left=artists_names,right=most_popular, left_on='id',right_on='ArtistId',how='right').drop(columns=['ArtistId'])
# print(x)


# midgnith to midnight no of songs listened to at each hour

# def account_for_germany(x):
#     if x.replace(tzinfo=None) < datetime.datetime(year=2025,month=8,day=9,hour=18):
#         return x + datetime.timedelta(hours=1)
#     return x



# history['played_at'] = pd.to_datetime(history['played_at']).apply(lambda x : account_for_germany(x))
# history['hour_played'] = history['played_at'].apply(lambda x : x.hour)

# # total counts
# counts = history['hour_played'].value_counts().reset_index()
# print(counts)
# sns.lineplot(data=counts,x='hour_played',y='count')

# plt.show()