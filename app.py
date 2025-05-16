from flask import Flask, render_template, redirect, url_for
from routes.competition_routes import competition_bp
from routes.match_routes import match_bp
from utils.extensions import cache
import logging
from flask_sqlalchemy import SQLAlchemy
import os


logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)

app = Flask(__name__)
cache.init_app(app)

db_uri = os.environ.get("postgres://ua39ec8677dalk:pe26c006f0fcbdf4939a1096e59daacdafae16f1ec47bc084b67b4d2fb1837ead@c7lolh640htr57.cluster-czz5s0kz4scl.eu-west-1.rds.amazonaws.com:5432/dakpff00g7ion6", "sqlite:///local.db")

if db_uri.startswith("postgres://"):
    db_uri = db_uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
from models import Competition, Season, Match


@app.route('/')
def index():
    return redirect(url_for('match.match_analysis'))  # 👈 'match' is the blueprint name

@app.route('/team-analysis')
def team_analysis():
    return render_template('team_analysis.html')

@app.route('/player-analysis')
def player_analysis():
    return render_template('player_analysis.html')

app.register_blueprint(competition_bp)
app.register_blueprint(match_bp)

if __name__ == '__main__':
    app.run(debug=True)

