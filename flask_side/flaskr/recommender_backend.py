import os
from dotenv import load_dotenv
import pandas as pd
import sklearn.neighbors

load_dotenv()

df = pd.read_csv(os.getenv("SONG_DATABASE_CSV"))
song_stats = pd.read_csv(os.getenv("SONG_STATS_CSV"),index_col=0)


music_features = ['acousticness','danceability','energy','instrumentalness','liveness','speechiness','valence']
mean = df[music_features].mean()
std = df[music_features].std()


def get_recs(ids : list[str]):
    relevant_stats_NORM = (song_stats[song_stats['spotify_id'].isin(ids)] - mean) / std
    averaged_song = relevant_stats_NORM[music_features].mean(axis=0)

    m = sklearn.neighbors.NearestNeighbors(metric='cosine')
    training_data = (df[music_features]-mean)/std
    m.fit(training_data)

    idxs = m.kneighbors(averaged_song.to_frame().T, n_neighbors=20, return_distance=True)[1][0]
    return df.loc[idxs]['track_id'].to_list()
