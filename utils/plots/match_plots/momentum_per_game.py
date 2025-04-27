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
    match_data = match_data[['minute', 'possession_team', 'type', 'location', 'pass_outcome', 'pass_end_location', 'carry_end_location']]
    filtered_data = match_data.loc[(match_data['type'] == 'Pass') | (match_data['type'] == 'Carry')]

    # Handle pass_outcome for Pass type, and carry_end_location for Carry type
    filtered_data.loc[filtered_data['type'] == 'Pass', 'pass_outcome'] = filtered_data.loc[
        filtered_data['type'] == 'Pass', 'pass_outcome'].fillna('Successful')

    # Split 'location' into start_x and start_y for all rows
    filtered_data[['start_x', 'start_y']] = pd.DataFrame(filtered_data['location'].tolist(), index=filtered_data.index)

    # For Pass type: set end_x and end_y from 'pass_end_location'
    filtered_data.loc[filtered_data['type'] == 'Pass', 'end_x'] = filtered_data.loc[
        filtered_data['type'] == 'Pass', 'pass_end_location'].apply(lambda x: x[0] if isinstance(x, list) else None)
    filtered_data.loc[filtered_data['type'] == 'Pass', 'end_y'] = filtered_data.loc[
        filtered_data['type'] == 'Pass', 'pass_end_location'].apply(lambda x: x[1] if isinstance(x, list) else None)

    # For Carry type: set end_x and end_y from 'carry_end_location'
    filtered_data.loc[filtered_data['type'] == 'Carry', 'end_x'] = filtered_data.loc[
        filtered_data['type'] == 'Carry', 'carry_end_location'].apply(lambda x: x[0] if isinstance(x, list) else None)
    filtered_data.loc[filtered_data['type'] == 'Carry', 'end_y'] = filtered_data.loc[
        filtered_data['type'] == 'Carry', 'carry_end_location'].apply(lambda x: x[1] if isinstance(x, list) else None)

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
    home_team_y = [0 if x < 0 else x for x in home_team_y]
    away_team_x = away_team_data['minute'].tolist()
    away_team_y = away_team_data['xT'].tolist()
    away_team_y = [-x if x > 0 else 0 for x in away_team_y]

    # Find the maximum absolute value for symmetry
    max_value = max(max(home_team_y), abs(min(away_team_y)))

    # Add a small buffer so the bars don't touch the x-axis
    buffer = max_value * 0.1
    max_range = max_value + buffer

    # Create Bar traces
    home_trace = go.Bar(
        x=home_team_x,
        y=home_team_y,
        name=home_team,
        marker=dict(
            color='blue',
            line=dict(color='rgba(0, 0, 255, 0.3)', width=3)
        ),
        width=0.6,
    )

    away_trace = go.Bar(
        x=away_team_x,
        y=away_team_y,
        name=away_team,
        marker=dict(
            color='red',
            line=dict(color='rgba(255, 0, 0, 0.3)', width=3)
        ),
        width=0.6,
    )

    layout = go.Layout(
        xaxis=dict(
            title='Minutes',
            color='white',
            gridcolor='rgba(255, 255, 255, 0.05)',
            showline=True,
            linecolor='rgba(255, 255, 255, 0.2)',
            automargin=True,
            autorange=True,
            zeroline=True,
            zerolinecolor='rgba(255,255,255,0.6)',
            zerolinewidth=2,
        ),
        yaxis=dict(
            range=[-max_range, max_range],  # Symmetrical around 0
            showgrid=False,
            zeroline=True,
            zerolinecolor='rgba(255,255,255,0.6)',
            zerolinewidth=2,
            visible=False
        ),
        barmode='relative',  # overlay instead of relative
        bargap=0.1,
        autosize=True,
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        margin=dict(l=20, r=20, t=20, b=40),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.25,
            xanchor='center',
            x=0.5,
            font=dict(color='white', size=12),
            bgcolor='rgba(0,0,0,0)'
        )
    )

    # Return a dictionary to match the desired format
    data = [home_trace, away_trace]
    return {"data": data, "layout": layout}

