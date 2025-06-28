import plotly.graph_objects as go
from utils.analytics.match_analytics.match_analysis_utils import cumulative_stats
import pandas as pd


def generate_match_graph_plot(match_data: pd.DataFrame, home_team: str, away_team: str):
    # Filter match data for only the required columns
    match_data = match_data[['team', 'minute', 'shot_outcome', 'shot_statsbomb_xg', 'period']]

    # Separate stats for Team 1 and Team 2
    team_1 = match_data[match_data['team'] == home_team]
    team_2 = match_data[match_data['team'] == away_team]

    team_1_stats = cumulative_stats(team_1)
    team_2_stats = cumulative_stats(team_2)

    # Dynamically determine the max values for x and y axes
    y_max = max(team_1_stats['cum_xg'].max(), team_1_stats['cum_goals'].max(),
                team_2_stats['cum_xg'].max(), team_2_stats['cum_goals'].max())
    x_max = max(team_1_stats['minute'].max(), team_2_stats['minute'].max())

    # Convert data to lists here to avoid serialization issues
    x_team1_stats = team_1_stats['minute'].tolist()
    y_cum_xg_team1 = team_1_stats['cum_xg'].tolist()
    y_cum_goals_team1 = team_1_stats['cum_goals'].tolist()

    x_team2_stats = team_2_stats['minute'].tolist()
    y_cum_xg_team2 = team_2_stats['cum_xg'].tolist()
    y_cum_goals_team2 = team_2_stats['cum_goals'].tolist()

    # Initialize Plotly traces (data) - convert to dicts for JSON serialization
    data = [
        # Real data traces (hidden from legend)
        {
            'x': x_team1_stats,
            'y': y_cum_xg_team1,
            'mode': 'lines',
            'name': '',
            'line': {'color': 'blue', 'dash': 'dash'},
            'showlegend': False,
            'type': 'scatter'
        },
        {
            'x': x_team1_stats,
            'y': y_cum_goals_team1,
            'mode': 'lines',
            'name': '',
            'line': {'color': 'blue'},
            'showlegend': False,
            'type': 'scatter'
        },
        {
            'x': x_team2_stats,
            'y': y_cum_xg_team2,
            'mode': 'lines',
            'name': '',
            'line': {'color': 'red', 'dash': 'dash'},
            'showlegend': False,
            'type': 'scatter'
        },
        {
            'x': x_team2_stats,
            'y': y_cum_goals_team2,
            'mode': 'lines',
            'name': '',
            'line': {'color': 'red'},
            'showlegend': False,
            'type': 'scatter'
        },
        # Legend dummy for xG
        {
            'x': [None],
            'y': [None],
            'mode': 'lines',
            'line': {'color': 'white', 'dash': 'dash'},
            'name': 'xG',
            'type': 'scatter'
        },
        # Legend dummy for Goals
        {
            'x': [None],
            'y': [None],
            'mode': 'lines',
            'line': {'color': 'white'},
            'name': 'Goals',
            'type': 'scatter'
        }
    ]

    # Add annotations and shading for extra time and penalties if applicable
    unique_periods = match_data['period'].unique()
    shapes = []
    annotations = []

    # Extra time shading (90–120 mins)
    if not set(unique_periods).issubset({1, 2}):
        shapes.append(dict(
            type="rect",
            x0=90, x1=x_max, y0=0, y1=y_max + 0.5,
            fillcolor="rgba(0, 255, 0, 0.2)",  # Semi-transparent green fill
            line=dict(color="rgba(0, 255, 0, 0)")
        ))
        annotations.append(dict(
            x=(90 + x_max) / 2, y=y_max + 0.5,
            text="Extra Time",
            showarrow=False,
            font=dict(color="green", size=12)
        ))

    # Penalty shootout shading (120+ mins)
    if match_data['period'].max() == 5:
        shapes.append(dict(
            type="rect",
            x0=120, x1=match_data['minute'].max(), y0=0, y1=y_max + 0.5,
            fillcolor="rgba(255, 0, 0, 0.2)",  # Semi-transparent red fill
            line=dict(color="rgba(255, 0, 0, 0)")
        ))
        annotations.append(dict(
            x=(120 + match_data['minute'].max()) / 2, y=y_max + 0.5,
            text="Penalties",
            showarrow=False,
            font=dict(color="red", size=12)
        ))

    # Define the layout of the graph - convert to dict for JSON serialization
    layout = {
        'title': {
            'text': 'xG and Goals per Game',
            'font': {'color': 'white', 'size': 14},
            'x': 0.5
        },
        'xaxis': {
            'color': 'white',
            'gridcolor': 'rgba(255, 255, 255, 0.1)',
            'showline': True,
            'linecolor': 'rgba(255, 255, 255, 0.2)'
        },
        'yaxis': {
            'color': 'white',
            'gridcolor': 'rgba(255, 255, 255, 0.1)',
            'showline': True,
            'linecolor': 'rgba(255, 255, 255, 0.2)',
            'range': [0, y_max + 1]
        },
        'legend': {
            'orientation': 'h',
            'x': 0,
            'y': 1,
            'xanchor': 'left',
            'yanchor': 'top',
            'font': {'color': 'white', 'size': 11},
            'bgcolor': 'rgba(0,0,0,0)'  # transparent background
        },
        'autosize': True,
        'plot_bgcolor': "rgba(0, 0, 0, 0)",
        'paper_bgcolor': "rgba(0, 0, 0, 0)",
        'margin': {'l': 10, 'r': 10, 't': 30, 'b': 30},
        'shapes': shapes,
        'annotations': annotations
    }

    return {"data": data, "layout": layout}
