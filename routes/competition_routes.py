from flask import Blueprint, jsonify, render_template
from utils.extensions import cache
from utils.db import db
from models import Competition, Season

competition_bp = Blueprint('competition_bp', __name__)

@competition_bp.route('/competition-analysis')
def competition_analysis():
    return render_template('competition_analysis.html')

@competition_bp.route('/api/competitions')
@cache.cached(timeout=86400)
def api_competitions():
    results = (
        db.session.query(
            Competition.id.label('competition_id'),
            Competition.name.label('competition_name'),
            Season.id.label('season_id'),
            Season.year.label('season_name')
        )
        .join(Season, Competition.id == Season.competition_id)
        .all()
    )

    comps = [
        {
            'competition_id': r.competition_id,
            'competition_name': r.competition_name,
            'season_id': r.season_id,
            'season_name': r.season_name
        }
        for r in results
    ]

    return jsonify(comps)


@competition_bp.route('/api/seasons/<int:competition_id>')
def api_seasons(competition_id):
    seasons = (
        Season.query
        .filter_by(competition_id=competition_id)
        .with_entities(Season.id.label('season_id'), Season.year.label('season_name'))
        .all()
    )

    data = [
        {'season_id': s.season_id, 'season_name': s.season_name}
        for s in seasons
    ]

    return jsonify(data)


