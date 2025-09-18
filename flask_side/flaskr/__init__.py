import os
from . import db
from flask import Flask, render_template, request, url_for, redirect,jsonify
from sqlalchemy import create_engine, inspect
from . import recommender_backend
import pandas as pd

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
    @app.route('/song', methods = ['GET','POST'])
    def get_id():
            if request.method == 'POST':
                song_id = request.form.get('song_id')
                return redirect(url_for('id_selected', song_id=song_id))
            return render_template('home.html',title="Hello")

    @app.route('/recommendation')
    def id_selected():
        song_id = request.args.get('song_id', None)
        song_list = recommender_backend.get_recs([song_id])
        return render_template('selected.html',title=f"Recs for {song_id}", song_id=song_id,rec_song_ids=song_list)

    @app.route('/')
    def load_analytics():
        (song_ids,song_names) = recommender_backend.songs_ids_names()
        quick_facts = recommender_backend.get_quick_stats()
        hour_fig = recommender_backend.get_hour_chart()
        week_fig = recommender_backend.get_weekly_chart()
        recommender_backend.get_calender()
        world_map = recommender_backend.get_world_map()
        tables = recommender_backend.get_tables()
        return render_template('homepage.html',hourly_fig=hour_fig,weekly_fig = week_fig,world_map = world_map,
                               song_id='2iUmqdfGZcHIhS3b9E9EWq', facts=quick_facts,
                               tables=tables, song_ids=song_ids,song_names=song_names)
    
    @app.route("/process", methods=["POST"])
    def process():
        data = request.get_json()
        print(data)
        ids = data.get("ids", [])
        percs = data.get("splits",[])
        print(percs)
        ids = list(map(lambda x: x.replace("'","").replace(" ",""),ids))
        print(ids)
        result = recommender_backend.get_recs(ids,percs) ## needs to take list of strings of ids
        return jsonify({"result": result})

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


    return app




