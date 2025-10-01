import os
from dotenv import load_dotenv
import numpy as np
import pandas as pd
import sklearn.neighbors
import datetime
import plotly.express as px
import plotly.io as pio
import calendar

# --------------------------------------
# Constants
# --------------------------------------

LGREY = "#f0efed"
LIMEGREEN = "#32cd32"
DGREY = "#696865"

MUSIC_FEATURES = ['acousticness','danceability','energy','instrumentalness','liveness','speechiness','valence']

# --------------------------------------
# Utilities
# --------------------------------------
def account_for_germany(x):
    if x.replace(tzinfo=None) < datetime.datetime(year=2025,month=8,day=9,hour=18):
        return x + datetime.timedelta(hours=1)
    return x


def compute_day_labels(date):
    cal_obj = calendar.Calendar()
    return cal_obj.monthdayscalendar(date.year,date.month)
 

def fix(x):
    if x in ['Boston','Seattle','New York']:
        return "United States"
    elif x in ['England','London']:
        return "United Kingdom"
    return x

def week_calc(x):
    date = (x.replace(tzinfo=None) - datetime.timedelta(days=1)).replace(hour=23,minute=59,second=59)
    today = datetime.datetime.today()
    if date < (today - datetime.timedelta(days=28)):
        return np.nan
    elif  date < today - datetime.timedelta(days=21):
        return 4
    elif date < today - datetime.timedelta(days=14):
        return 3
    elif date < today - datetime.timedelta(days=7):
        return 2
    elif date <= today:
        return 1

def colour_picker(df,text):
    if text == "":
        return "rgba(80, 89, 91, 0.89)"
    else:
        try: 
            watches = int(df.loc[text])
            if watches == 1:
                return "rgba(49, 235, 65, 0.78)"
            return "rgba(0, 144, 13, 1)"
        except KeyError:
            return "rgba(240,240,240,1)"
        
def initialise_graph_extras(fig,song_id,date,songs_df,art_song_df,artists_df):
    week_days = ['Mo','Tu','We','Th','Fr','Sa','Su']
    song_name = songs_df.loc[songs_df['id'] == song_id, 'name']
    date = datetime.datetime.fromisoformat(date)
    
    if not song_name.empty:
        artist_ids = art_song_df.loc[art_song_df['SongId'] == song_id, 'ArtistId']
        artists_names = artists_df.loc[artists_df['id'].isin(artist_ids),'name'].drop_duplicates().to_list()
        
        
        # artists_str = ", ".join(artists_names)
        # total_str = f"History for : {song_name.item()} by " + artists_str
        # if len(total_str) > 20:
        #     total_str  = total_str[0:18] + "..."
            
        # fig.add_shape(
        #     type="rect",
        #     x0=0, y0=18, x1=5, y1=19.5,
        #     line=dict(width=0),
        #     fillcolor="rgba(255, 255, 255, 0.59)",
        #     label=dict(text=total_str, 
        #             textposition="middle left", font=dict(family="Souvenir Lt BT, bold", size=28))
        # )

        
    for k in range(0,7):
        fig.add_shape(
                type="rect",
                x0=2*k, y0=12, x1=2*k+1.5, y1=13.5, 
                line=dict(color="black", width=3),
                fillcolor="#FF4141",
                label=dict(text=week_days[k],font={'weight' : 'bold'})
            )
        
    return fig

# --------------------------------------
# Start-up functions
# --------------------------------------

def load_csv_files(app):
    load_dotenv()

    history = pd.read_csv(os.getenv("SONGHISTORY_CSV"),index_col=0)
    history['played_at'] = pd.to_datetime(history['played_at'])
    history['played_at'] = history['played_at'].apply(lambda x : account_for_germany(x))
    history['hour_played'] = history['played_at'].apply(lambda x: x.hour)
    history['id_lagged'] = history['id'].shift(-1)
    history = history.loc[history['id'] != history['id_lagged']]
    history.drop(columns=['id_lagged'],inplace=True)

    artists = pd.read_csv(os.getenv("ARTISTS_CSV"),index_col=0)
    artists['country'] = artists['country'].apply(lambda x : fix(x))

    app.config['SONGHISTORY'] = history
    app.config['ARTISTS'] = artists
    app.config['ART_SONG'] = pd.read_csv(os.getenv("ARTISTS_SONGS_CSV"),index_col=0)
    app.config['ALBUMS'] = pd.read_csv(os.getenv("ALBUMS_CSV"),index_col=0)
    app.config['SONGS'] = pd.read_csv(os.getenv("SONGS_CSV"),index_col=0)
    app.config['SONGDB'] = pd.read_csv(os.getenv("SONG_DATABASE_CSV"))
    app.config['SONGSTATS'] = pd.read_csv(os.getenv("SONG_STATS_CSV"),index_col=0)
    app.config['CODES'] = pd.read_csv(os.getenv("CODES_CSV"),index_col=0)

def get_homepage_charts(app):
    hour_fig = get_hour_chart(app.config['SONGHISTORY'])
    week_fig = get_weekly_chart(app.config['SONGHISTORY'])
    world_map = get_world_map(app.config['ARTISTS'], app.config['CODES'])
    return {
        "hourly_fig": hour_fig,
        "weekly_fig": week_fig,
        "world_map": world_map,
    }

# --------------------------------------
# Functions
# --------------------------------------

def songs_ids_names(songs_df):
    song_ids = songs_df['id'].to_list()
    song_names = list(map(lambda x : x.replace(",","##"),songs_df['name'].to_list()))
    return [song_ids,song_names]


def get_quick_stats(history_df,songs_df):
    time_s = (songs_df['duration_ms'].mean()/1000)
    avg_liked_song_length = f"{int(time_s // 60)}m {round(time_s % 60)}s"

    history_stats = history_df.copy(deep=True)

    history_stats['days'] = history_stats['played_at'].apply(lambda x : datetime.datetime(year=x.year,month=x.month,day=x.day))
    daily_avg = float(round(history_stats.groupby('days').size().mean(),2))

    seven_days_back = (datetime.datetime.today() - datetime.timedelta(days=7)).replace(tzinfo=datetime.timezone.utc)
    history_seven = history_stats[history_stats['played_at'] > seven_days_back]
    past_week_no = history_seven.shape[0]

    thirty_days_back = (datetime.datetime.today() - datetime.timedelta(days=30)).replace(tzinfo=datetime.timezone.utc)
    history_thirty = history_stats[history_stats['played_at'] > thirty_days_back]
    past_30_no = history_thirty.shape[0]

    return [avg_liked_song_length,past_week_no,past_30_no,daily_avg]


def get_tables(art_song_df,artists_df,history_df,albums_df,songs_df):
    grouped_by_artists = art_song_df.groupby(by=["ArtistId"])
    most_popular = grouped_by_artists['SongId'].count().nlargest(n=20).reset_index()
    artists_names = artists_df[['name','id']].drop_duplicates()
    artist_list = pd.merge(left=artists_names,right=most_popular, left_on='id',right_on='ArtistId',how='right').drop(columns=['ArtistId','id'])
    top_5_artists = artist_list.rename(columns={'name':'Artists Name', 'SongId' : 'No. of songs'}).head(5)

    all_time_listens = history_df.groupby(by=['id','name']).size().reset_index().rename(columns={0:'No. of listens','name' : 'Song Name'}).drop(columns=['id'])
    all_time_listens = all_time_listens.sort_values(by='No. of listens',ascending=False).head(5)

    history_30_days = history_df[history_df['played_at'] > (datetime.datetime.today() - datetime.timedelta(days=31)).replace(tzinfo=datetime.timezone.utc)]
    
    thirty_day_listens = history_30_days.groupby(by=['id','name']).size().reset_index().rename(columns={0:'No. of listens','name' : 'Song Name'}).drop(columns=['id'])
    thirty_day_listens = thirty_day_listens.sort_values(by='No. of listens',ascending=False).head(5)

    top_5_albums_ids = songs_df.groupby('album_id').size().nlargest(5).to_frame('No. of songs from album')
    top_5_albums= pd.merge(left=albums_df,right=top_5_albums_ids,left_on='id', right_on='album_id', how='right')[['name','No. of songs from album']].drop_duplicates().rename(columns={'name' : 'Album Name'})

    return [all_time_listens.to_html(justify='center',index=False),
            thirty_day_listens.to_html(justify='center',index=False),
            top_5_artists.to_html(justify='center',index=False),
            top_5_albums.to_html(justify='center',index=False)]


def get_recs(ids : list[str],percs,song_stats_df,songdb_df):
    mean = songdb_df[MUSIC_FEATURES].mean()
    std = songdb_df[MUSIC_FEATURES].std()

    percs = list(map(lambda x: int(x),percs))
    relevant_stats_NORM = (song_stats_df[song_stats_df['spotify_id'].isin(ids)] - mean) / std
    averaged_song = (relevant_stats_NORM[MUSIC_FEATURES].apply(lambda x : x * percs,axis=0)).sum() / (np.sum(percs))

    m = sklearn.neighbors.NearestNeighbors(metric='cosine')
    training_data = (songdb_df[MUSIC_FEATURES]-mean)/std
    m.fit(training_data)

    idxs = m.kneighbors(averaged_song.to_frame().T, n_neighbors=20, return_distance=True)[1][0]
    return songdb_df.loc[idxs]['track_id'].to_list()


def get_hour_chart(history_df):
    counts = history_df['hour_played'].value_counts().reset_index()
    x = pd.merge(left=pd.Series(np.arange(0,24),name="Hour"),right=counts,left_on="Hour",right_on='hour_played',how='left').fillna(0).astype(int)[['Hour','count']].rename(columns={'count' : 'No. of songs'})
    x['Hour'] = x['Hour'].apply(lambda x: f"{x:02d}:00")

    max_val = x['No. of songs'].max()

    # Build the line plot
    fig = px.line(
        data_frame = x,
        x=x["Hour"], 
        y=x["No. of songs"],
        labels={"x": "Hour", "y": "No. of songs"},
    )

    fig.update_traces(line=dict(color=LIMEGREEN, width=2.5))

    fig.update_layout(
        autosize=True,
        height = 300,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor=DGREY,  
        plot_bgcolor=DGREY,   
        font=dict(color=LGREY),    
        xaxis=dict(
            showline=True, 
            fixedrange=True,
            showgrid=False,
            zeroline=False,
            linecolor=LGREY,
            tickvals=np.arange(0, 24, 3),
            ticktext=[f"{h:02d}:00" for h in np.arange(0, 24, 3)],
            tickfont=dict(color=LGREY,weight='bold'),
            title=dict(text="Hour", font=dict(color=LGREY,weight='bold'))
        ),
        yaxis=dict(
            showline=True, 
            fixedrange=True,
            showgrid=False,
            zeroline=False,
            linecolor=LGREY,
            tickfont=dict(color=LGREY,weight='bold'),
            title=dict(text="No. of songs", font=dict(color=LGREY,weight='bold')),
            range = [-5,max_val+10]
        )
    )
    
    return pio.to_html(fig, include_plotlyjs='cdn', full_html=False,config=dict(displayModeBar=False))

    
def get_weekly_chart(history_df):
# week-by-week, no. of songs listened to per hour
    week_df = history_df.copy()
    week_df['week'] = week_df['played_at'].apply(lambda x: week_calc(x))
    week_df.dropna(inplace=True,subset=['week'])
    grouped_week = week_df.groupby(by=['week','hour_played'])
    counts = grouped_week['id'].count().reset_index().rename(columns={'week': 'Week', 'hour_played': 'Hour'})
    all_hours = pd.merge(left=pd.Series([1,2,3,4],name="Week"),right=pd.Series(np.arange(0,24),name="Hour"),how='cross')
    counts_full = pd.merge(left=all_hours,right=counts,on=["Week","Hour"],how='left')
    counts_full['No. of Songs'] = counts_full['id'].fillna(0).astype(int)
    counts_full['Week'] = counts_full['Week'].astype(str)
    counts_full['Hour'] =  counts_full['Hour'].apply(lambda x: f"{x:02d}:00")

    max_val = counts_full['No. of Songs'].max()

    # Build the line plot
    fig = px.line(
        data_frame = counts_full,
        x="Hour", 
        y="No. of Songs",
        color="Week",
        labels={"x": "Hour", "y": "No. of songs"},
    )

    fig.update_traces(line=dict(width=2.5))

    fig.update_layout(
        autosize=True,
        height = 300,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor=DGREY,  
        plot_bgcolor=DGREY,  
        font=dict(color=LGREY),  
        xaxis=dict(
            showline=True, 
            fixedrange=True,
            showgrid=False,
            zeroline=False,
            linecolor=LGREY,
            tickvals=np.arange(0, 24, 3),
            ticktext=[f"{h:02d}:00" for h in np.arange(0, 24, 3)],
            tickfont=dict(color=LGREY,weight='bold'),
            title=dict(text="Hour", font=dict(color=LGREY,weight='bold'))
        ),
        yaxis=dict(
            showline=True, 
            fixedrange=True,
            showgrid=False,
            zeroline=False,
            linecolor=LGREY,
            tickfont=dict(color=LGREY,weight='bold'),
            title=dict(text="No. of songs", font=dict(color=LGREY,weight='bold')),
            range = [-5,max_val+10]
        )
    )

    newnames = {'4':'22-28 days ago', '3': '15-21 days ago', '2' : '8-14 days ago','1':'1-7 days ago'}
    fig.for_each_trace(lambda t: t.update(name = newnames[t.name],
                                        legendgroup = newnames[t.name],
                                        hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])
                                        )
                    )

    fig.update_layout(
        legend = {'y' : 0.90,
                  'x' : 0.05,
                  'xanchor' : 'left',
                  'yanchor':'top',
                  'title' : None,
                })

    return pio.to_html(fig, include_plotlyjs='cdn', full_html=False,config=dict(displayModeBar=False))


def proportional_dist(): ## CURRENTLY UNIMPLEMENTED
    pass
    ## never implemented a graph using proportional distribution
    # ax = plt.axes(projection=ccrs.Robinson())
    # ax.set_title("Distribution proportional to number of songs")
    # top_appearance = self.prop_numbers.max()
    # norm = mcolors.LogNorm(vmin=1, vmax=top_appearance)
    # for country in shpreader.Reader(self.countries_shp).records():
    #     country_name = country.attributes['NAME_LONG']
    #     if country_name in self.prop_numbers.index:
    #         appearances = self.prop_numbers.loc[country_name]
    #         ax.add_geometries(country.geometry, ccrs.PlateCarree(),
    #                         facecolor=self.cmap(norm(appearances)),
    #                         label=country_name)

    #     else:
    #         ax.add_geometries(country.geometry, ccrs.PlateCarree(),
    #                         facecolor="#FCEBEB",
    #                         label=country_name)

    
    #     return pio.to_html(tls.mpl_to_plotly(ax.get_figure()), include_plotlyjs='cdn', full_html=False)


def get_world_map(artists_df,codes_df):
    flat_numbers = artists_df[['country']].groupby(['country']).size().to_frame('count').reset_index()
    country_codes = codes_df.reset_index()[['English short name lower case','Alpha-3 code']].rename(columns={'English short name lower case':'name','Alpha-3 code' :'code'})
    coded_counts = pd.merge(left=country_codes,right=flat_numbers,left_on='name',right_on='country',how='left')[['name','code','count']].fillna(0)
    coded_counts['logged_counts'] = coded_counts['count'].apply(lambda x : np.log10(x) if x != 0 else -0.5)

    
    fig = px.choropleth(coded_counts, locations="code",
                    color="logged_counts", 
                    hover_name="name", 
                    color_continuous_scale=px.colors.sequential.Reds,
                    hover_data={
                        'count' : True,
                        'logged_counts' : False,
                        'code' : False,
                        }
                    )
    
    fig.update_layout(
        # geo=dict(bgcolor=LGREY),
        autosize=True,
        height = 300,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor=DGREY,  
        plot_bgcolor=DGREY,  
        font=dict(color=LGREY),
        coloraxis_showscale = False,
        )
    
    return pio.to_html(fig, include_plotlyjs='cdn', full_html=False,config=dict(displayModeBar=False))

