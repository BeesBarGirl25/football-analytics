from flask import Flask, render_template, redirect, url_for
from routes.competition_routes import competition_bp
from routes.match_routes import match_bp
from utils.extensions import cache
import logging

logging.basicConfig(
    level=logging.WARN,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)

app = Flask(__name__)
cache.init_app(app)

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

