from flask import Blueprint, jsonify, render_template

from utils.analytics.match_analytics.match_analysis_utils import goal_assist_data, discipline_analysis
from utils.extensions import cache
from statsbombpy import sb
import numpy as np
import logging
from flask import request
from utils.plots.match_plots.xG_per_game import generate_match_graph_plot
import pandas as pd
import plotly.io as pio  # Import this for converting Plotly figures to JSON


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
    match_cleaned = events.fillna(-999)
    return jsonify(match_cleaned.to_dict(orient='records'))

@match_bp.route('/api/generate_match_graph', methods=['POST'])
def generate_match_graph():
    try:
        # Get the match data from the POST request
        match_data = request.json.get("matchData")
        # Validate that match data is provided
        if not match_data:
            return jsonify({"error": "No match data provided"}), 400

        # Convert match_data (JSON) into a pandas DataFrame
        try:
            match_df = pd.DataFrame(match_data)
        except Exception as df_error:
            return jsonify({"error": "Failed to convert match data to DataFrame"}), 500

        # Pass the DataFrame to the graph generation function
        graph_figure = generate_match_graph_plot(match_df)

        graph_json = pio.to_json(graph_figure, pretty=True)
        return jsonify(graph_json)
    except Exception as e:
        logger.error(f"Unexpected error in generate_match_graph: {e}")
        return jsonify({"error": str(e)}), 500

@match_bp.route('/api/generate_match_summary', methods=['POST'])
def generate_match_overview():
    try:
        match_data = request.json.get("matchData")
        if not match_data:
            return jsonify({"error": "No match data provided"}), 400

        try:
            match_df = pd.DataFrame(match_data)
            logger.debug(f"Converted match_data to DataFrame")
        except Exception as df_error:
            logger.error(f"Error converting JSON to DataFrame: {df_error}")
            return jsonify({"error": "Failed to convert match data to DataFrame"}), 500

        home_goals, home_assists, away_goals, away_assists, home_score, away_score, home_team, away_team, home_team_extra_time, away_team_extra_time, home_team_penalties, away_team_penalties = goal_assist_data(match_df)
        logger.debug(f"goal_assist_data results: "
                     f"home_goals={home_goals}, away_goals={away_goals}, "
                     f"home_assists={type(home_assists)}, away_assists={type(away_assists)}, "
                     f"home_score={home_score}, away_score={away_score}")

        home_yellow, home_red, away_yellow, away_red = discipline_analysis(match_df)
        logger.debug(f"discipline_analysis results: "
                     f"home_yellow={type(home_yellow)}, home_red={type(home_red)}, "
                     f"away_yellow={type(away_yellow)}, away_red={type(away_red)}")



        return jsonify({
            "home_goals": home_goals.tolist() if isinstance(home_goals, pd.Series) else home_goals,
            "away_goals": away_goals.tolist() if isinstance(away_goals, pd.Series) else away_goals,
            "home_assists": home_assists.tolist() if isinstance(home_assists, pd.Series) else home_assists,
            "away_assists": away_assists.tolist() if isinstance(away_assists, pd.Series) else away_assists,
            "home_yellow": home_yellow.tolist() if isinstance(home_yellow, pd.Series) else home_yellow,
            "home_red": home_red.tolist() if isinstance(home_red, pd.Series) else home_red,
            "away_yellow": away_yellow.tolist() if isinstance(away_yellow, pd.Series) else away_yellow,
            "away_red": away_red.tolist() if isinstance(away_red, pd.Series) else away_red,
            "home_score": home_score,
            "away_score": away_score,
            "home_team": home_team,
            "away_team": away_team,
            "home_team_extra_time": home_team_extra_time,
            "away_team_extra_time": away_team_extra_time,
            "home_team_penalties": home_team_penalties,
            "away_team_penalties": away_team_penalties
        })

    except Exception as e:
        logger.error(f"Unexpected error in generate_match_summary: {e}")
        return jsonify({"error": str(e)}), 500



