from flask import Flask, render_template, redirect, url_for
from routes.competition_routes import competition_bp
from routes.match_routes import match_bp
from utils.extensions import cache
import logging
from flask_sqlalchemy import SQLAlchemy
import os
from utils.db import db  # ⬅️ Instead of 'from flask_sqlalchemy import SQLAlchemy'


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

db.init_app(app)  # ✅ Attach it to the app

# Import models AFTER db is attached
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

@app.route('/debug/competitions')
def debug_competitions():
    comps = Competition.query.all()
    if not comps:
        return "No competitions found."
    return "<br>".join(f"{c.id} – {c.name}" for c in comps)


if __name__ == '__main__':
    app.run(debug=True)

