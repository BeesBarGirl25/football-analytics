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
    plot = MatchPlot.query.get(match_id)
    if not plot:
        return jsonify({"error": "No plot data found for this match."}), 404

    try:
        return jsonify({
            "xg_graph": json.loads(plot.xg_graph_json) if plot.xg_graph_json else {},
            "momentum_graph": json.loads(plot.momentum_graph_json) if plot.momentum_graph_json else {},
            "match_summary": json.loads(plot.match_summary_json) if plot.match_summary_json else {}
        })
    except Exception as e:
        logger.error(f"Error parsing plot data for match {match_id}: {e}")
        return jsonify({"error": "Failed to parse plot data"}), 500
