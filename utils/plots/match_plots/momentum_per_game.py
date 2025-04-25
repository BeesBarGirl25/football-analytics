import pandas as pd
import numpy as np
import plotly.graph_objects as go
import logging
import os

def load_xT():
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Traverse up to the project root and then to the data file
    file_path = os.path.join(script_dir, "../../../data/xT_Grid.csv")

    # Attempt to load the CSV file
    try:
        xT = pd.read_csv(file_path)
        return xT
    except FileNotFoundError as e:
        raise RuntimeError(f"xT_Grid.csv file not found at: {file_path}") from e


def generate_momentum_graph_plot(match_data):
    match_data = match_data[['minute', 'possession_team', 'type', 'location', 'pass_outcome', 'pass_end_location']]
    filtered_data = match_data.loc[match_data['type'] == 'Pass']
    filtered_data.loc[:, 'pass_outcome'] = filtered_data['pass_outcome'].fillna('Successful')
    filtered_data[['start_x', 'start_y']] = pd.DataFrame(filtered_data['location'].tolist(), index=filtered_data.index)
    filtered_data[['end_x', 'end_y']] = pd.DataFrame(filtered_data['pass_end_location'].tolist(),index=filtered_data.index)

    logging.debug(f"filtered_data: {filtered_data}")
    xT = load_xT()
    logging.debug(f"xT: {xT}")
    xT = np.array(xT)
    xt_rows, xt_cols = xT.shape
    filtered_data['x1_bin'] = pd.cut(filtered_data['start_x'], bins=xt_cols, labels=False)
    filtered_data['y1_bin'] = pd.cut(filtered_data['start_y'], bins=xt_rows, labels=False)
    filtered_data['x2_bin'] = pd.cut(filtered_data['end_x'], bins=xt_cols, labels=False)
    filtered_data['y2_bin'] = pd.cut(filtered_data['end_y'], bins=xt_rows, labels=False)
    filtered_data['start_zone_value'] = filtered_data[['x1_bin', 'y1_bin']].apply(lambda x: xT[x[1]][x[0]], axis=1)
    filtered_data['end_zone_value'] = filtered_data[['x2_bin', 'y2_bin']].apply(lambda x: xT[x[1]][x[0]], axis=1)
    filtered_data['xT'] = filtered_data['end_zone_value'] - filtered_data['start_zone_value']
    summed_data = (
        filtered_data
        .groupby(['minute', 'possession_team'])['xT']
        .sum()
        .reset_index()
    )

    home_team, away_team = summed_data['possession_team'].unique()
    home_team_data = summed_data[summed_data['possession_team'] == home_team]
    away_team_data = summed_data[summed_data['possession_team'] == away_team]

    # Set a "shrink" factor to bring bars in a little bit
    shrink_factor = 0.9

    home_team_x = home_team_data['minute'].tolist()
    home_team_y = home_team_data['xT'].tolist()
    away_team_x = away_team_data['minute'].tolist()
    away_team_y = away_team_data['xT'].tolist()
    away_team_y = [-1 * x for x in away_team_y]


    # Create Plotly Bar traces
    home_trace = go.Bar(
        x=home_team_x,
        y=home_team_y,
        name=home_team,
        marker_color='red'
    )

    away_trace = go.Bar(
        x=away_team_x,
        y=away_team_y,
        name=away_team,
        marker_color='blue'
    )

    # Define layout using go.Layout
    layout = go.Layout(
        barmode='overlay',
        bargap=0.2,
        autosize=True,
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )

    # Return a dictionary to match the desired format
    data = [home_trace, away_trace]
    return {"data": data, "layout": layout}

