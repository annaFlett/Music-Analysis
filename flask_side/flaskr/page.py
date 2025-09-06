from flask import Flask, render_template, request, jsonify, url_for, redirect

app = Flask(__name__)


@app.route('/song', methods = ['GET','POST'])
def get_id():
        if request.method == 'POST':
            song_id = request.form.get('date')
            return redirect(url_for('recommedations', song_id=song_id))
        return render_template('home.html',title="Hello")

@app.route('/recommendation')
def id_selected():
    song_id = request.args.get('id', None)
    return render_template('selected.html',title=f"Recs for {song_id}", song_id=song_id)
