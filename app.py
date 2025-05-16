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

db_uri = os.environ.get("DATABASE_URL", "sqlite:///local.db")

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

