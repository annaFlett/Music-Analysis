import os
from . import db
from flask import Flask, render_template, request, url_for, redirect,jsonify
from sqlalchemy import create_engine, inspect
from . import recommender_backend
import pandas as pd
from dash import Dash, dcc, html, Output, Input,ctx
import plotly.graph_objects as go
from dotenv import load_dotenv
import datetime 

load_dotenv()
LGREY = "#f0efed"
LIMEGREEN = "#32cd32"
DGREY = "#696865"

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db_path = "sqlite:///database.db"
    engine = create_engine(db_path)
    inspector = inspect(engine)

    csv_table_mapping = {
        os.getenv("ALBUMS_CSV") : "albums",
        os.getenv("ARTIST_ALBUMS_CSV") : "artists_albums",
        os.getenv("ARTISTS_SONGS_CSV") : 'artists_songs',
        os.getenv("ARTISTS_CSV") : 'artists',
        os.getenv("CONTEXT_CSV") : 'context',
        os.getenv("SONGHISTORY_CSV") : 'song_history',
        os.getenv("SONGS_CSV") : 'songs',
        os.getenv("PLACES_CSV") : 'places',
        os.getenv("SONG_STATS_CSV") : 'song_stats',
        os.getenv("COUNTRY_LOC_CSV") : 'country_loc',
        os.getenv("ARTISTS_COUNTRY_CSV") : 'all_songs',
    }

    recommender_backend.load_csv_files(app)
    ### Uncomment when you want to read the csv's again (will need to deal with the fact that the tables exist)
    # with app.app_context():
    #     for csv_path, table_name in csv_table_mapping.items():
    #         if table_name not in inspector.get_table_names():
    #             if os.path.exists(csv_path):
    #                 df = pd.read_csv(csv_path,index_col=0)
    #                 df.to_sql(table_name, engine, if_exists="fail", index=False)
    #                 print(f"Inserted {len(df)} rows into table '{table_name}'")
    #             else:
    #                 print(f"CSV file {csv_path} not found. Skipping.")
    #         else:
    #             print(f"Table '{table_name}' already exists. Skipping CSV load.")

        # id entry page


    @app.route('/')
    def load_analytics():
        charts = recommender_backend.get_homepage_charts(app)
        return render_template('homepage.html',**charts)
    
    @app.route("/process", methods=["POST"])
    def process():
        data = request.get_json()
        ids = data.get("ids", [])
        percs = data.get("splits",[])
        ids = list(map(lambda x: x.replace("'","").replace(" ",""),ids))
        result = recommender_backend.get_recs(ids,percs,app.config['SONGSTATS'],app.config['SONGDB']) ## needs to take list of strings of ids
        return jsonify({"result": result})

    @app.route("/table_setup", methods=['GET'])
    def table_setup():
        return recommender_backend.get_tables(app.config['ART_SONG'],app.config['ARTISTS'],app.config['SONGHISTORY'])

    @app.route("/song_info",methods=['GET'])
    def song_info():
        return recommender_backend.songs_ids_names(app.config['SONGS'])
    
    @app.route("/get_facts",methods=['GET'])
    def get_facts():
        return recommender_backend.get_quick_stats(app.config['SONGHISTORY'],app.config['SONGS'])

    @app.route("/view")
    def view_table():
        # Check if table exists
        tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", engine)
        # if table_name not in tables['name'].values:
            # return f"Table '{table_name}' does not exist.", 404

        # Read table into DataFrame
        df = pd.read_sql_table('table1', engine)
        
        # Return as JSON
        return df.to_json(orient="records")


    dash_app = Dash(
        __name__,
        server=app,
        url_base_pathname='/dash/',
        suppress_callback_exceptions=True
    )

    songs = pd.read_csv(os.getenv("SONGS_CSV"),index_col=0)
    history = pd.read_csv(os.getenv("SONGHISTORY_CSV"),index_col=0)
    history['played_at'] = pd.to_datetime(history['played_at'])
    history['played_at'] = history['played_at'].apply(lambda x : recommender_backend.account_for_germany(x))

    song_choices = list(zip(songs['name'],songs['id']))


    dash_app.layout = html.Div([
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
    ],style={"margin": "0", "padding": "0"})

    @dash_app.callback(
        Output('graph', 'figure'),
        Input('song_choice', 'value'),
        Input('current_date','data'),
    )
    def update_graph(song,date):
        fig = go.Figure()
        fig.update_xaxes(range = [-1,15],showticklabels=False,showgrid=False,zeroline=False,fixedrange=True)
        fig.update_yaxes(range = [-1,20],showticklabels=False,showgrid=False,zeroline = False,fixedrange=True)
        fig.update_layout(template='plotly_white',
                          margin=dict(l=0, r=0, t=0, b=0), 
                          paper_bgcolor=DGREY,  
                          plot_bgcolor=DGREY,)

        fig.layout.shapes = []
        song_history = history[history['id'] == song][['name','played_at']]
        song_history['month'] = song_history['played_at'].apply(lambda x : x.month)

        cal_date = datetime.datetime.strptime(date,"%Y-%m-%dT%H:%M:%S.%f")

        filt_history = song_history[song_history['month'] == cal_date.month]
        filt_history['day'] = filt_history['played_at'].apply(lambda x : x.day)
        counts = filt_history.groupby(by='day').size()

        day_labels = recommender_backend.compute_day_labels(cal_date)
        
        for i in range(0,5):
            for j in range(0,7):
                text = ""
                if day_labels[i][j] != 0:
                    text = day_labels[i][j]
                    
                fig.add_shape(
                    type="rect",
                    x0=2*j, y0=10 - 2*i, x1=2*j+1.5, y1=10 -2*i+1.5, 
                    line=dict(color="black", width=1),
                    fillcolor=recommender_backend.colour_picker(counts,text),
                    label=dict(text=text)
                )
                
        fig = recommender_backend.initialise_graph_extras(fig,song,date,app.config['SONGS'],app.config['ART_SONG'],app.config['ARTISTS'])
            
        return fig

    @dash_app.callback(
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
        dash_app.run(debug=True)

    
    
    return app




