import json
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter
import plotly.graph_objects as go

def _generate_pitch_shapes_vertical():
    return [
        dict(type="rect", x0=0, y0=0, x1=80, y1=120, line=dict(color="black")),  # Full pitch
        dict(type="line", x0=0, y0=60, x1=80, y1=60, line=dict(color="black")),  # Halfway line
        dict(type="circle", x0=40 - 9.15, y0=60 - 9.15, x1=40 + 9.15, y1=60 + 9.15, line=dict(color="black")),
        dict(type="rect", x0=30, y0=0, x1=50, y1=18, line=dict(color="black")),
        dict(type="rect", x0=30, y0=102, x1=50, y1=120, line=dict(color="black")),
        dict(type="rect", x0=36, y0=0, x1=44, y1=6, line=dict(color="black")),
        dict(type="rect", x0=36, y0=114, x1=44, y1=120, line=dict(color="black")),
        dict(type="circle", x0=39.7, y0=11.7, x1=40.3, y1=12.3, fillcolor="black", line=dict(color="black")),
        dict(type="circle", x0=39.7, y0=108.7, x1=40.3, y1=109.3, fillcolor="black", line=dict(color="black"))
    ]

def generate_dominance_heatmap_json(match_data: pd.DataFrame, home_team: str, away_team: str, half: str = "full") -> dict:
    bins = (24, 16)
    sigma = 2.5

    activity_events = match_data[match_data['type'].isin(['Pass', 'Carry', 'Dribble', 'Shot'])]

    location_data = activity_events[['location', 'team', 'period']].dropna()
    location_data = location_data[location_data['location'].apply(lambda loc: isinstance(loc, list))]
    location_data[['y', 'x']] = pd.DataFrame(location_data['location'].tolist(), index=location_data.index)

    # Flip second half only for full match to normalize direction
    if half == "full":
        first_half = location_data[location_data['period'] == 1].copy()
        second_half = location_data[location_data['period'] == 2].copy()
        second_half['y'] = 120 - second_half['y']
        location_data = pd.concat([first_half, second_half])
    elif half == "first":
        location_data = location_data[location_data['period'] == 1].copy()
    elif half == "second":
        location_data = location_data[location_data['period'] == 2].copy()

    # Separate team data
    team_a, team_b = home_team, away_team
    team_a_data = location_data[location_data['team'] == team_a]
    team_b_data = location_data[location_data['team'] == team_b]

    x_bins = np.linspace(0, 80, bins[1] + 1)
    y_bins = np.linspace(0, 120, bins[0] + 1)

    a_hist, _, _ = np.histogram2d(team_a_data['y'], team_a_data['x'], bins=[y_bins, x_bins])
    b_hist, _, _ = np.histogram2d(team_b_data['y'], team_b_data['x'], bins=[y_bins, x_bins])
    total = a_hist + b_hist

    with np.errstate(divide='ignore', invalid='ignore'):
        dominance = np.divide(a_hist, total, out=np.full_like(total, 0.5), where=total != 0)
    dominance = gaussian_filter(dominance, sigma=sigma)

    y_centers = 0.5 * (y_bins[:-1] + y_bins[1:])
    x_centers = 0.5 * (x_bins[:-1] + x_bins[1:])

    fig = go.Figure(data=go.Heatmap(
        z=dominance.tolist(),
        x=x_centers.tolist(),
        y=y_centers.tolist(),
        zmin=0,
        zmax=1,
        colorscale=[
            [0.0, "rgb(5,48,97)"],        # Team A = blue
            [0.35, "rgb(67,147,195)"],
            [0.49, "rgb(247,247,247)"],
            [0.51, "rgb(253,219,199)"],
            [0.65, "rgb(214,96,77)"],
            [1.0, "rgb(103,0,31)"]         # Team B = red
        ],
        reversescale=False,
        showscale=False
    ))

    fig.update_layout(
        xaxis=dict(range=[0, 80], visible=False),
        yaxis=dict(range=[0, 120], visible=False, scaleanchor="x", scaleratio=1.5),
        margin=dict(t=30, l=0, r=0, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        autosize=True,
        title=dict(text=f"{half.capitalize()} Half Dominance", x=0.5, font=dict(color='white', size=14)),
        shapes=_generate_pitch_shapes_vertical()
    )

    return fig.to_plotly_json()
