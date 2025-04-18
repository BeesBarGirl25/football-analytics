from flask import Blueprint, jsonify, render_template
from utils.statsbomb_utils import get_all_competitions
from utils.extensions import cache

competition_bp = Blueprint('competition_bp', __name__)

@competition_bp.route('/competition-analysis')
def competition_analysis():
    return render_template('competition_analysis.html')


@cache.cached(timeout=86400)
@competition_bp.route('/api/competitions')
def api_competitions():
    df = get_all_competitions()
    unique_comps = df[['competition_name', 'competition_id', 'season_name', 'season_id']].drop_duplicates()
    return jsonify(unique_comps.to_dict(orient='records'))

@competition_bp.route('/api/seasons/<int:competition_id>')
def api_seasons(competition_id):
    df = get_all_competitions()
    filtered = df[df['competition_id'] == competition_id]
    seasons = filtered[['season_id', 'season_name']].drop_duplicates()
    return jsonify(seasons.to_dict(orient='records'))