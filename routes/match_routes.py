from flask import Blueprint, jsonify, render_template
from utils.extensions import cache
from statsbombpy import sb
import logging

logger = logging.getLogger(__name__)

match_bp = Blueprint('match', __name__)



@match_bp.route('/match-analysis')
def match_analysis():
    return render_template('match_analysis.html')


@match_bp.route('/api/matches/<int:competition_id>/<int:season_id>')
@cache.cached(timeout=3600)
def get_matches(competition_id, season_id):
    logger.debug(f"Competition_id: {competition_id}, Season_id: {season_id}")

    matches = sb.matches(competition_id=competition_id, season_id=season_id)

    simplified = [
        {
            'match_id': row['match_id'],
            'home_team': row['home_team'],  # just use the string
            'away_team': row['away_team']
        }
        for idx, row in matches.iterrows()
    ]
    return jsonify(simplified)


@match_bp.route('/api/events/<int:match_id>')
@cache.cached(timeout=3600)
def get_match_events(match_id):
    events = sb.events(match_id)
    return jsonify(events.to_dict(orient='records'))
