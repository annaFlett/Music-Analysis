import pandas as pd
import numpy as np

w1 = pd.read_csv("songs23July.csv")
w2 = pd.read_csv("songs30July.csv")
# songs.drop(columns=['preview_url'],inplace=True)
# print(songs.head())
# print(songs.columns)
# print(songs.info())

# print(songs[['name','popularity']].sort_values(by='popularity',ascending=False).head(20))
week1songs = w1[['name','popularity']].sort_values(by='popularity',ascending=False)
week2songs = w2[['name','popularity']].sort_values(by='popularity',ascending=False)

## TODO MAKE A WIDGIT WHICH GIVEN A SONG WILL PLOT ITS POPULARITY OVER TIME
week1songs.rename(mapper={'name':'name_1','popularity':'popularity_1'},axis=1,inplace=True)
week2songs.rename(mapper={'name':'name_2','popularity':'popularity_2'},axis=1,inplace=True)
song_popularity = pd.concat([week1songs,week2songs],axis=1)
print(song_popularity.columns)
print(song_popularity[song_popularity['popularity_1'] != song_popularity['popularity_2']])



# wk1 = (week1songs['name'].reset_index())
# wk2 = (week2songs['name'].reset_index())
# differences = week1songs[week1songs['name'] != week2songs['name']]
# print(differences.dropna())