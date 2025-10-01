import os
from flask import Flask, render_template, request,jsonify
from . import utils
from dash import Dash, dcc, html, Output, Input,ctx
import plotly.graph_objects as go
from dotenv import load_dotenv
import datetime 

load_dotenv()
LGREY = "#f0efed"
LIMEGREEN = "#32cd32"
DGREY = "#696865"
START_OF_DATA = datetime.datetime(2025,8,1,0,0,0)

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

    utils.load_csv_files(app)


    @app.route('/')
    def load_analytics():
        charts = utils.get_homepage_charts(app)
        return render_template('homepage.html',**charts)
    
    @app.route("/process", methods=["POST"])
    def process():
        data = request.get_json()
        ids = data.get("ids", [])
        percs = data.get("splits",[])
        ids = list(map(lambda x: x.replace("'","").replace(" ",""),ids))
        result = utils.get_recs(ids,percs,app.config['SONGSTATS'],app.config['SONGDB']) ## needs to take list of strings of ids
        return jsonify({"result": result})

    @app.route("/table_setup", methods=['GET'])
    def table_setup():
        return utils.get_tables(app.config['ART_SONG'],app.config['ARTISTS'],app.config['SONGHISTORY'],app.config['ALBUMS'],app.config['SONGS'])

    @app.route("/song_info",methods=['GET'])
    def song_info():
        return utils.songs_ids_names(app.config['SONGS'])
    
    @app.route("/get_facts",methods=['GET'])
    def get_facts():
        return utils.get_quick_stats(app.config['SONGHISTORY'],app.config['SONGS'])



    ## Creating dash app for calendar
    dash_app = Dash(
        __name__,
        server=app,
        url_base_pathname='/dash/',
        suppress_callback_exceptions=True,
    )

    song_choices = list(zip(app.config['SONGS']['name'],app.config['SONGS']['id']))

    date = datetime.datetime.today().replace(day=1)
    dash_app.layout = html.Div([
        dcc.Dropdown(
            id='song_choice',
            options=[{'label': song_name, 'value': song_id} for song_name,song_id in song_choices],
            searchable=True,
            style={'width': '100%'}
        ),
         html.Div([
            html.H2(f"{date.strftime('%B').upper()} {date.strftime('%Y').upper()}",id="calendar-date",
                        style={'color' : LIMEGREEN, 'margin' : "0px 20px 0px 40px", 'font': 'bold 28px "Souvenir Lt BT", sans-serif'}),
                html.Div([
                    html.Button(
                        html.I(style={'transform': 'rotate(135deg)',
                                                        '-webkit-transform': 'rotate(135deg)',
                                                        'border': 'solid black',
                                                        'border-width': '0 3px 3px 0',
                                                        'display': 'inline-block',
                                                        'padding': '3px'}),
                        style={'border-radius': '100%','padding': '10px'}, 
                        id='back', n_clicks=0),
                    html.Button(
                        html.I(style={'transform': 'rotate(-45deg)',
                                                        '-webkit-transform': 'rotate(-45deg)',
                                                        'border': 'solid black',
                                                        'border-width': '0 3px 3px 0',
                                                        'display': 'inline-block',
                                                        'padding': '3px'}),
                        style={'border-radius': '100%','padding': '10px'},
                        id='forwards', n_clicks=0,disabled=True)],
                    style={
                        'position': 'absolute',     
                        'left': '50%',               
                        'transform': 'translateX(70px)',             
                        'display': 'flex',
                        'gap': '10px'
                    })],
            style={
                'position': 'relative',          
                'height': '50px',            
                'width': '100%',
                'display':'flex',
                'padding-top' : '20px'
            }),
        dcc.Graph(id='graph',config= {'displayModeBar' : False},style={"margin": "0", "padding": "0",'width': '100%','height': '370px'},responsive=True),
        dcc.Store(id="current_date", data=date)
    ],style={"margin": "0", "padding": "0",'height':'100%'})

    @dash_app.callback(
        Output('graph', 'figure'),
        Input('song_choice', 'value'),
        Input('current_date','data'),
    )
    def update_graph(song,date):
        fig = go.Figure()
        fig.update_xaxes(range = [-1,15],showticklabels=False,showgrid=False,zeroline=False,fixedrange=True)
        fig.update_yaxes(range = [2,14],showticklabels=False,showgrid=False,zeroline = False,fixedrange=True)
        fig.update_layout(template='plotly_white',
                          autosize=True,
                          margin=dict(l=0, r=0, t=0, b=0), 
                          paper_bgcolor=DGREY,  
                          plot_bgcolor=DGREY,
                          showlegend=False)

        fig.layout.shapes = []
        song_history = app.config['SONGHISTORY'][app.config['SONGHISTORY']['id'] == song][['name','played_at']]
        song_history['month'] = song_history['played_at'].apply(lambda x : x.month)

        cal_date = datetime.datetime.fromisoformat(date)

        filt_history = song_history[song_history['month'] == cal_date.month].copy()
        filt_history['day'] = filt_history['played_at'].apply(lambda x : x.day)
        counts = filt_history.groupby(by='day').size()

        day_labels = utils.compute_day_labels(cal_date)
        
        for i in range(0,5):
            for j in range(0,7):
                text = ""
                if day_labels[i][j] != 0:
                    text = day_labels[i][j]
                    
                fig.add_shape(
                    type="rect",
                    x0=2*j, y0=10 - 2*i, x1=2*j+1.5, y1=10 -2*i+1.5, 
                    line=dict(color="black", width=1),
                    fillcolor=utils.colour_picker(counts,text),
                    label=dict(text=text)
                )
                
        fig = utils.initialise_graph_extras(fig,song,date,app.config['SONGS'],app.config['ART_SONG'],app.config['ARTISTS'])
            
        return fig

    @dash_app.callback(
        Output('current_date','data'),
        Output('back','disabled'),
        Output('forwards','disabled'),
        Output('calendar-date', 'children'),
        Input('back','n_clicks'),
        Input('forwards','n_clicks'),
        Input('current_date','data'),
        prevent_initial_call=True
    )
    def update_month(back,forwards,current_date):
        current_date = datetime.datetime.fromisoformat(current_date)
        if "back" == ctx.triggered_id and current_date > START_OF_DATA:
            current_date = (current_date - datetime.timedelta(days=1)).replace(day=1,hour=0,minute=0,second=0,microsecond=0)
        elif "forwards" == ctx.triggered_id and current_date < datetime.datetime.today().replace(day=1,hour=0,minute=0,second=0,microsecond=0):
            current_date = (current_date + datetime.timedelta(days=35)).replace(day=1,hour=0,minute=0,second=0,microsecond=0)
        date_str = f"{current_date.strftime('%B').upper()} {current_date.strftime('%Y').upper()}"
        return current_date, current_date <= START_OF_DATA, current_date >= datetime.datetime.today().replace(day=1,hour=0,minute=0,second=0,microsecond=0), date_str
        

    if __name__ == "__main__":
        dash_app.run(debug=True)


    return app


## Setup for if you want to work with SQLite instead of CSVs
# from sqlalchemy import create_engine, inspect

# @app.route("/view")
#     def view_table():
#         # Check if table exists
#         tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", engine)
#         # if table_name not in tables['name'].values:
#             # return f"Table '{table_name}' does not exist.", 404

#         # Read table into DataFrame
#         df = pd.read_sql_table('table1', engine)
        
#         # Return as JSON
#         return df.to_json(orient="records")
    
#     db_path = "sqlite:///database.db"
#     engine = create_engine(db_path)
#     inspector = inspect(engine)

#     csv_table_mapping = {
#         os.getenv("ALBUMS_CSV") : "albums",
#         os.getenv("ARTIST_ALBUMS_CSV") : "artists_albums",
#         os.getenv("ARTISTS_SONGS_CSV") : 'artists_songs',
#         os.getenv("ARTISTS_CSV") : 'artists',
#         os.getenv("CONTEXT_CSV") : 'context',
#         os.getenv("SONGHISTORY_CSV") : 'song_history',
#         os.getenv("SONGS_CSV") : 'songs',
#         os.getenv("PLACES_CSV") : 'places',
#         os.getenv("SONG_STATS_CSV") : 'song_stats',
#         os.getenv("COUNTRY_LOC_CSV") : 'country_loc',
#         os.getenv("ARTISTS_COUNTRY_CSV") : 'all_songs',
#     }

    ### Uncomment when you want to read the csv's again (will need to deal with the fact that the tables already exist)
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



