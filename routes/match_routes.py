from flask import Blueprint, jsonify, render_template
from utils.extensions import cache
from utils.db import db
from models import Match, MatchPlot
import json
import logging

match_bp = Blueprint('match', __name__)
logger = logging.getLogger(__name__)

@match_bp.route('/match-analysis')
def match_analysis():
    return render_template('match_analysis.html')

@match_bp.route('/api/matches/<season_id>')
@cache.cached(timeout=3600)
def get_matches(season_id):
    matches = Match.query.filter_by(season_id=season_id).all()
    simplified = [
        {
            'match_id': match.id,
            'home_team': match.home_team,
            'away_team': match.away_team
        }
        for match in matches
    ]
    return jsonify(simplified)

@match_bp.route('/api/plots/<int:match_id>')
@cache.cached(timeout=3600)
def get_match_plots(match_id):
    plots = MatchPlot.query.filter_by(match_id=match_id).all()

    if not plots:
        return jsonify({"error": "No plot data found for this match."}), 404

    try:
        result = {}
        for plot in plots:
            result[plot.plot_type] = json.loads(plot.plot_json)

        return jsonify(result)
    except Exception as e:
        logger.error(f"Error parsing plot data for match {match_id}: {e}", exc_info=True)
        return jsonify({"error": "Failed to parse plot data"}), 500

