from flask import Blueprint, jsonify, render_template

from utils.analytics.match_analytics.match_analysis_utils import goal_assist_stats, extract_player_names
from utils.extensions import cache
from statsbombpy import sb
import numpy as np
import logging
from flask import request
from utils.plots.match_plots.xG_per_game import generate_match_graph_plot
import pandas as pd
import plotly.io as pio  # Import this for converting Plotly figures to JSON
from utils.plots.match_plots.momentum_per_game import generate_momentum_graph_plot
from utils.plots.match_plots.match_heatmap import generate_match_heatmap_plot
from flask import Response


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

@match_bp.route('/api/generate_match_heatmap', methods=['POST'])
def generate_match_heatmap():
    try:
        match_data = request.json.get("matchData")
        if not match_data:
            return jsonify({"error": "No match data provided"}), 400

        match_df = pd.DataFrame(match_data)
        graph_dict = generate_match_heatmap_plot(match_df)
        logger.debug(f"Converted match_data to DataFrame")
        logger.debug(f"Generated heatmap")
        logger.debug(f"Returning graph_dict")
        logger.debug(f"graph_dict: {graph_dict}")
        return jsonify(graph_dict)
    except Exception as e:
        logger.error(f"Unexpected error in generate_match_heatmap: {e}")
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

        home_team_df, away_team_df, home_team, away_team, home_team_normal_time, away_team_normal_time, home_team_extra_time, away_team_extra_time, home_team_penalties, away_team_penalties = goal_assist_stats(match_df)
        home_team_data = []
        for _, row in home_team_df.iterrows():
            home_team_data.append({
                'player': row['player'],
                'contributions': list(row['contributions'])
            })

        away_team_data = []
        for _, row in away_team_df.iterrows():
            away_team_data.append({
                'player': row['player'],
                'contributions': list(row['contributions'])
            })

        # Create the combined scoreline
        scoreline = f"{home_team} {home_team_normal_time} - {away_team_normal_time} {away_team}"
        extra_time_details = None

        # Add extra time and penalties if they exist
        if home_team_extra_time > 0 or away_team_extra_time > 0:
            extra_time_details = f"(ET: {home_team_extra_time} - {away_team_extra_time})"
        if home_team_penalties > 0 or away_team_penalties > 0:
            if extra_time_details:
                extra_time_details += f", (Pen: {home_team_penalties} - {away_team_penalties})"
            else:
                extra_time_details = f"(Pen: {home_team_penalties} - {away_team_penalties})"

        return jsonify({
            'home': home_team_data,
            'away': away_team_data,
            'homeTeam': home_team,
            'awayTeam': away_team,
            'homeTeamNormalTime': home_team_normal_time,
            'awayTeamNormalTime': away_team_normal_time,
            'homeTeamExtraTime': home_team_extra_time,
            'awayTeamExtraTime': away_team_extra_time,
            'homeTeamPenalties': home_team_penalties,
            'awayTeamPenalties': away_team_penalties,
            'scoreline': scoreline,
            'extraTimeDetails': extra_time_details
        })

    except Exception as e:
        logger.error(f"Unexpected error in generate_match_summary: {e}")
        return jsonify({"error": str(e)}), 500


@match_bp.route('/api/generate_momentum_graph', methods=['POST'])
def generate_momentum_graph():
    try:
        match_data = request.json.get("matchData")
        if not match_data:
            return jsonify({"error": "No match data provided"}), 400
        try:
            match_df = pd.DataFrame(match_data)

            graph_figure = generate_momentum_graph_plot(match_df)
            graph_json = pio.to_json(graph_figure, pretty=True)
            logger.debug(f"Converted match_data to DataFrame")
            return jsonify(graph_json)
        except Exception as df_error:
            logger.error(f"Error converting JSON to DataFrame: {df_error}")
            return jsonify({"error": "Failed to convert match data to DataFrame"}), 500
    except Exception as e:
        logger.error(f"Unexpected error in generate_momentum_graph: {e}")
        return jsonify({"error": str(e)}), 500


