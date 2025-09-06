import os

from . import db
from flask import Flask, render_template, request, jsonify, url_for, redirect
from . import recommender_backend

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

    db.init_app(app)

    return app




