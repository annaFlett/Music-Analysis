import os
from dotenv import load_dotenv
import numpy as np
import pandas as pd
import sklearn.neighbors
import datetime
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from dash import Dash, dcc, html, Output, Input,ctx
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import plotly.tools as tls


load_dotenv()

def account_for_germany(x):
    if x.replace(tzinfo=None) < datetime.datetime(year=2025,month=8,day=9,hour=18):
        return x + datetime.timedelta(hours=1)
    return x


df = pd.read_csv(os.getenv("SONG_DATABASE_CSV"))
song_stats = pd.read_csv(os.getenv("SONG_STATS_CSV"),index_col=0)
songs = pd.read_csv(os.getenv("SONGS_CSV"),index_col=0)

music_features = ['acousticness','danceability','energy','instrumentalness','liveness','speechiness','valence']
mean = df[music_features].mean()
std = df[music_features].std()


def songs_ids_names():
    songs = pd.read_csv(os.getenv("SONGS_CSV"),index_col=0)
    song_ids = songs['id'].to_list()
    song_names = list(map(lambda x : x.replace(",","##"),songs['name'].to_list()))
    return (song_ids,song_names)

def get_quick_stats():
    history = pd.read_csv(os.getenv("SONGHISTORY_CSV"),index_col=0)
    history['played_at'] = pd.to_datetime(history['played_at'])
    history['played_at'] = history['played_at'].apply(lambda x : account_for_germany(x))
    time_s = (songs['duration_ms'].mean()/1000)
    avg_liked_song_length = f"{int(time_s // 60)}m {round(time_s % 60)}s"

    history_stats = history.copy(deep=True)

    history_stats['days'] = history_stats['played_at'].apply(lambda x : datetime.datetime(year=x.year,month=x.month,day=x.day))
    daily_avg = float(round(history_stats.groupby('days').size().mean(),2))

    seven_days_back = (datetime.datetime.today() - datetime.timedelta(days=7)).replace(tzinfo=datetime.timezone.utc)
    history_seven = history_stats[history_stats['played_at'] > seven_days_back]
    past_week_no = history_seven.shape[0]

    thirty_days_back = (datetime.datetime.today() - datetime.timedelta(days=30)).replace(tzinfo=datetime.timezone.utc)
    history_thirty = history_stats[history_stats['played_at'] > thirty_days_back]
    past_30_no = history_thirty.shape[0]

    return [avg_liked_song_length,past_week_no,past_30_no,daily_avg]


def get_tables():
    art_song = pd.read_csv(os.getenv("ARTISTS_SONGS_CSV"),index_col=0)
    grouped_by_artists = art_song.groupby(by=["ArtistId"])
    most_popular = grouped_by_artists['SongId'].count().nlargest(n=20).reset_index()
    artists_names = artists[['name','id']].drop_duplicates()
    artist_list = pd.merge(left=artists_names,right=most_popular, left_on='id',right_on='ArtistId',how='right').drop(columns=['ArtistId','id'])
    top_5_artists = artist_list.rename(columns={'name':'Artists Name', 'SongId' : 'No. of songs'}).head(5)

    history = pd.read_csv(os.getenv("SONGHISTORY_CSV"),index_col=0)
    history['played_at'] = pd.to_datetime(history['played_at'])
    history['played_at'] = history['played_at'].apply(lambda x : account_for_germany(x))
    all_time_listens = history.groupby(by=['id','name']).size().reset_index().rename(columns={0:'No. of listens','name' : 'Song Name'}).drop(columns=['id'])
    all_time_listens = all_time_listens.sort_values(by='No. of listens',ascending=False).head(5)

    history_30_days = history[history['played_at'] > (datetime.datetime.today() - datetime.timedelta(days=31)).replace(tzinfo=datetime.timezone.utc)]
    
    thirty_day_listens = history_30_days.groupby(by=['id','name']).size().reset_index().rename(columns={0:'No. of listens','name' : 'Song Name'}).drop(columns=['id'])
    thirty_day_listens = thirty_day_listens.sort_values(by='No. of listens',ascending=False).head(5)

    return f"{top_5_artists.to_html(justify='center',index=False)}###{thirty_day_listens.to_html(justify='center',index=False)}###{all_time_listens.to_html(justify='center',index=False)}"

def get_recs(ids : list[str],percs):
    percs = list(map(lambda x: int(x),percs))
    relevant_stats_NORM = (song_stats[song_stats['spotify_id'].isin(ids)] - mean) / std
    averaged_song = (relevant_stats_NORM[music_features].apply(lambda x : x * percs,axis=0)).sum() / (np.sum(percs))
    print(averaged_song)

    m = sklearn.neighbors.NearestNeighbors(metric='cosine')
    training_data = (df[music_features]-mean)/std
    m.fit(training_data)

    idxs = m.kneighbors(averaged_song.to_frame().T, n_neighbors=20, return_distance=True)[1][0]
    return df.loc[idxs]['track_id'].to_list()


def get_hour_chart():
    history = pd.read_csv(os.getenv("SONGHISTORY_CSV"),index_col=0)
    history['played_at'] = pd.to_datetime(history['played_at'])
    history = history[history['played_at'].dt.date > datetime.datetime(year=2025,month=7,day=31).date()]
    history['played_at'] = history['played_at'].apply(lambda x : account_for_germany(x))
    history['hour_played'] = history['played_at'].apply(lambda x: x.hour)
    counts = history['hour_played'].value_counts().reset_index()
    x = pd.merge(left=pd.Series(np.arange(0,24),name="Hour"),right=counts,left_on="Hour",right_on='hour_played',how='left').fillna(0).astype(int)[['Hour','count']].rename(columns={'count' : 'No. of songs'})
    x['Hour'] = x['Hour'].apply(lambda x: f"{x:02d}:00")

    LGREY = "#f0efed"
    LIMEGREEN = "#32cd32"
    DGREY = "#696865"
    max_val = x['No. of songs'].max()

    # Build the line plot
    fig = px.line(
        data_frame = x,
        x=x["Hour"], 
        y=x["No. of songs"],
        labels={"x": "Hour", "y": "No. of songs"},
    )

    # Style the trace
    fig.update_traces(line=dict(color=LIMEGREEN, width=2.5))

    # Format the layout to match your matplotlib look
    fig.update_layout(
        paper_bgcolor=DGREY,   # figure background
        plot_bgcolor=DGREY,    # axes background
        font=dict(color=LGREY),    # text color
        xaxis=dict(
            showline=True, 
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
            showgrid=False,
            zeroline=False,
            linecolor=LGREY,
            tickfont=dict(color=LGREY,weight='bold'),
            title=dict(text="No. of songs", font=dict(color=LGREY,weight='bold')),
            range = [-5,max_val+10]
        )
    )
    html_str = pio.to_html(fig, include_plotlyjs='cdn', full_html=False)
    return html_str


def week_calc(x):
    if  x.replace(tzinfo=None) < datetime.datetime(year=2025,month=8,day=8,hour=23,minute=59,second=59):
        return 1
    elif x.replace(tzinfo=None) < datetime.datetime(year=2025,month=8,day=15,hour=23,minute=59,second=59):
        return 2
    elif x.replace(tzinfo=None) < datetime.datetime(year=2025,month=8,day=22,hour=23,minute=59,second=59):
        return 3
    elif x.replace(tzinfo=None) < datetime.datetime(year=2025,month=8,day=29,hour=23,minute=59,second=59):
        return 4
    elif x.replace(tzinfo=None) < datetime.datetime(year=2025,month=8,day=31,hour=23,minute=59,second=59) : 
        return 5
    
def get_weekly_chart():
# week-by-week, no. of songs listened to per hour
    history = pd.read_csv(os.getenv("SONGHISTORY_CSV"),index_col=0)
    history['played_at'] = pd.to_datetime(history['played_at'])
    history = history[history['played_at'].dt.date > datetime.datetime(year=2025,month=8,day=1).date()]
    history['played_at'] = history['played_at'].apply(lambda x : account_for_germany(x))

    history['hour_played'] = history['played_at'].apply(lambda x: x.hour)
    week_df = history.copy()
    week_df['week'] = week_df['played_at'].apply(lambda x: week_calc(x))
    grouped_week = week_df.groupby(by=['week','hour_played'])
    counts = grouped_week['id'].count().reset_index().rename(columns={'week': 'Week', 'hour_played': 'Hour'})
    all_hours = pd.merge(left=pd.Series([1,2,3,4,5],name="Week"),right=pd.Series(np.arange(0,24),name="Hour"),how='cross')
    counts_full = pd.merge(left=all_hours,right=counts,on=["Week","Hour"],how='left')
    counts_full['No. of Songs'] = counts_full['id'].fillna(0).astype(int)
    counts_full['Week'] = counts_full['Week'].astype(str)
    counts_full['Hour'] =  counts_full['Hour'].apply(lambda x: f"{x:02d}:00")

    LGREY = "#f0efed"
    LIMEGREEN = "#32cd32"
    DGREY = "#696865"
    max_val = counts_full['No. of Songs'].max()

    # Build the line plot
    fig = px.line(
        data_frame = counts_full,
        x="Hour", 
        y="No. of Songs",
        color="Week",
        labels={"x": "Hour", "y": "No. of songs"},
    )

    # # Style the trace
    fig.update_traces(line=dict(width=2.5))

    # Format the layout to match your matplotlib look
    fig.update_layout(
        paper_bgcolor=DGREY,   # figure background
        plot_bgcolor=DGREY,    # axes background
        font=dict(color=LGREY),    # text color
        xaxis=dict(
            showline=True, 
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
            showgrid=False,
            zeroline=False,
            linecolor=LGREY,
            tickfont=dict(color=LGREY,weight='bold'),
            title=dict(text="No. of songs", font=dict(color=LGREY,weight='bold')),
            range = [-5,max_val+10]
        )
    )

    html_str = pio.to_html(fig, include_plotlyjs='cdn', full_html=False)
    return html_str

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

history = pd.read_csv(os.getenv("SONGHISTORY_CSV"),index_col=0)
history['played_at'] = pd.to_datetime(history['played_at'])
art_song = pd.read_csv(os.getenv("ARTISTS_SONGS_CSV"),index_col=0)
songs = pd.read_csv(os.getenv("SONGS_CSV"),index_col=0)
artists = pd.read_csv(os.getenv("ARTISTS_CSV"),index_col=0)

def initialise_graph_extras(fig,song_id,date):
    week_days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    song_name = songs.loc[songs['id'] == song_id, 'name']
    date = datetime.datetime.strptime(date,"%Y-%m-%dT%H:%M:%S.%f")
    
    if not song_name.empty:
        artist_ids = art_song.loc[art_song['SongId'] == song_id, 'ArtistId']
        artists_names = artists.loc[artists['id'].isin(artist_ids),'name'].drop_duplicates().to_list()
        artists_str = ", ".join(artists_names)
        total_str = f"Listening History :  {song_name.item()} by " + artists_str
        if len(total_str) > 65:
            total_str  = total_str[0:62] + "..."
            
        fig.add_shape(
            type="rect",
            x0=0, y0=18, x1=5, y1=19.5,
            line=dict(width=0),
            fillcolor="rgba(255, 255, 255, 0.59)",
            label=dict(text=total_str, 
                    textposition="middle left", font=dict(family="Souvenir Lt BT, bold", size=28))
        )

    
    fig.add_shape(
        type="rect",
        x0=0, y0=15, x1=5, y1=16.5,
        line=dict(width=0),
        fillcolor="rgba(255, 255, 255, 0.59)",
        label=dict(text=f"{date.strftime('%B').upper()} {date.strftime('%Y').upper()}", textposition="middle left", font=dict(family="Souvenir Lt BT, bold", size=28,color='red'))
    )
        
    for k in range(0,7):
        fig.add_shape(
                type="rect",
                x0=2*k, y0=12, x1=2*k+1.5, y1=13.5, 
                line=dict(color="grey", width=2),
                fillcolor="rgba(49, 206, 235, 0.59)",
                label=dict(text=week_days[k])
            )


def compute_day_labels(fig,date):
    days = [[None,None,None,None,1,2,3],np.arange(4,11),np.arange(11,18),np.arange(18,25),[25,26,27,28,29,30,31]]
    day_labels = np.array(days)
    return day_labels
 
def get_calender():
    app = Dash(__name__)

    song_choices = list(zip(songs['name'],songs['id']))
    fig = go.Figure()
    fig.update_xaxes(range = [-1,15],showticklabels=False,showgrid=False,zeroline=False,fixedrange=True)
    fig.update_yaxes(range = [-1,20],showticklabels=False,showgrid=False,zeroline = False,fixedrange=True)
    fig.update_layout(template='plotly_white')


    app.layout = html.Div([
        dcc.Dropdown(
            id='song_choice',
            options=[{'label': song_name, 'value': song_id} for song_name,song_id in song_choices],
            searchable=True,
            style={'width': '100%'}
        ),
        html.Button('<',id='back',n_clicks=0),
        html.Button('>',id='forwards',n_clicks=0),
        dcc.Graph(id='graph',config= {'displayModeBar' : False},style={'width': '100%'},responsive=True),
        dcc.Store(id="current_date", data=datetime.datetime.today().replace(day=1))
    ])

    @app.callback(
        Output('graph', 'figure'),
        Input('song_choice', 'value'),
        Input('current_date','data'),
    )
    def update_graph(song,date):
        fig.layout.shapes = []
        song_history = history[history['id'] == song][['name','played_at']]
        song_history['day'] = song_history['played_at'].apply(lambda x : x.day)
        counts = song_history.groupby(by='day').size()

        day_labels = compute_day_labels(fig,date)
        
        for i in range(0,5):
            for j in range(0,7):
                text = ""
                if day_labels[i][j] is not None:
                    text = day_labels[i][j]
                    
                fig.add_shape(
                    type="rect",
                    x0=2*j, y0=10 - 2*i, x1=2*j+1.5, y1=10 -2*i+1.5, 
                    line=dict(color="black", width=1),
                    fillcolor=colour_picker(counts,text),
                    label=dict(text=text)
                )
                
        initialise_graph_extras(fig,song,date)
            
        return fig

    @app.callback(
        Output('current_date','data'),
        Input('back','n_clicks'),
        Input('forwards','n_clicks'),
        Input('current_date','data'),
        prevent_initial_call=True
    )
    def update_month(back,forwards,current_date):
        current_date = datetime.datetime.strptime(current_date,"%Y-%m-%dT%H:%M:%S.%f")
        if "back" == ctx.triggered_id:
            current_date = (current_date - datetime.timedelta(days=1)).replace(day=1)
        elif "forwards" == ctx.triggered_id:
            current_date = (current_date + datetime.timedelta(days=35)).replace(day=1)
        return current_date
        

    if __name__ == "__main__":
        app.run(debug=True)


def fix(x):
    if x in ['Boston','Seattle','New York']:
        return "United States"
    elif x in ['England','London']:
        return "United Kingdom"
    return x

def proportional_dist(self):
    ## never implemented a graph using proportional distribution
    ax = plt.axes(projection=ccrs.Robinson())
    ax.set_title("Distribution proportional to number of songs")
    top_appearance = self.prop_numbers.max()
    norm = mcolors.LogNorm(vmin=1, vmax=top_appearance)
    for country in shpreader.Reader(self.countries_shp).records():
        country_name = country.attributes['NAME_LONG']
        if country_name in self.prop_numbers.index:
            appearances = self.prop_numbers.loc[country_name]
            ax.add_geometries(country.geometry, ccrs.PlateCarree(),
                            facecolor=self.cmap(norm(appearances)),
                            label=country_name)

        else:
            ax.add_geometries(country.geometry, ccrs.PlateCarree(),
                            facecolor="#FCEBEB",
                            label=country_name)

    
        return pio.to_html(tls.mpl_to_plotly(ax.get_figure()), include_plotlyjs='cdn', full_html=False)

def get_world_map():
    places_df = pd.read_csv(os.getenv("PLACES_CSV"),index_col=0)
    places_df = places_df.drop_duplicates()
    places_df['country'] = places_df['country'].apply(lambda x : fix(x))
    flat_numbers = places_df[['country']].groupby(['country']).size().to_frame('count').reset_index()

    country_codes = pd.read_csv(r"C:\Users\annab\OneDrive\Documents\coding projects\spotify api\csv\wikipedia-iso-country-codes.csv")
    country_codes = country_codes[['English short name lower case','Alpha-3 code']].rename(columns={'English short name lower case':'name','Alpha-3 code' :'code'})
    coded_counts = pd.merge(left=country_codes,right=flat_numbers,left_on='name',right_on='country',how='left')[['name','code','count']].fillna(0)
    coded_counts['logged_counts'] = coded_counts['count'].apply(lambda x : np.log10(x) if x != 0 else x)
    fig = px.choropleth(coded_counts, locations="code",
                    color="logged_counts", 
                    hover_name="name", 
                    color_continuous_scale=px.colors.sequential.Plasma)
    return pio.to_html(fig, include_plotlyjs='cdn', full_html=False)


        
get_calender()