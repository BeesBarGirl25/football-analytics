import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.ndimage import gaussian_filter


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


def generate_dominance_heatmap_json(match_data: pd.DataFrame, half: str = "full") -> dict:
    bins = (24, 16)  # (y, x)

    location_data = match_data[['location', 'team', 'period']].dropna()
    location_data = location_data[location_data['location'].apply(lambda loc: isinstance(loc, list))]
    location_data[['y', 'x']] = pd.DataFrame(location_data['location'].tolist(), index=location_data.index)

    if half == "first":
        location_data = location_data[location_data['period'] == 1]
    elif half == "second":
        location_data = location_data[location_data['period'] == 2]

    teams = location_data['team'].unique()
    if len(teams) != 2:
        raise ValueError(f"Expected 2 teams, found {teams}")

    team_a, team_b = teams
    team_a_data = location_data[location_data['team'] == team_a]
    team_b_data = location_data[location_data['team'] == team_b]

    x_bins = np.linspace(0, 80, bins[1] + 1)
    y_bins = np.linspace(0, 120, bins[0] + 1)

    a_hist, _, _ = np.histogram2d(team_a_data['y'], team_a_data['x'], bins=[y_bins, x_bins])
    b_hist, _, _ = np.histogram2d(team_b_data['y'], team_b_data['x'], bins=[y_bins, x_bins])

    total_actions = a_hist + b_hist
    with np.errstate(divide='ignore', invalid='ignore'):
        dominance_ratio = np.divide(a_hist, total_actions, where=total_actions != 0)
        dominance_ratio = np.nan_to_num(dominance_ratio, nan=0.5)  # Default to neutral if zero actions

    smoothed_map = gaussian_filter(dominance_ratio, sigma=1.5)
    smoothed_map = np.clip(smoothed_map, 0.0, 1.0)

    y_centers = 0.5 * (y_bins[:-1] + y_bins[1:])
    x_centers = 0.5 * (x_bins[:-1] + x_bins[1:])

    fig = go.Figure(data=go.Heatmap(
        z=smoothed_map.tolist(),
        x=x_centers.tolist(),
        y=y_centers.tolist(),
        zmin=0,
        zmax=1,
        colorscale = [
                        [0.0, "rgb(103,0,31)"],      # Deep red
                        [0.1, "rgb(165,15,21)"],
                        [0.2, "rgb(203,24,29)"],
                        [0.3, "rgb(239,59,44)"],
                        [0.4, "rgb(251,106,74)"],
                        [0.5, "rgb(255,255,255)"],   # Neutral
                        [0.6, "rgb(158,202,225)"],
                        [0.7, "rgb(107,174,214)"],
                        [0.8, "rgb(66,146,198)"],
                        [0.9, "rgb(33,113,181)"],
                        [1.0, "rgb(5,48,97)"]        # Deep blue
                    ],
        showscale=True
    ))

    fig.update_layout(
        xaxis=dict(range=[0, 80], visible=False),
        yaxis=dict(range=[0, 120], visible=False, scaleanchor="x", scaleratio=1.5),
        margin=dict(t=30, l=0, r=0, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        autosize=True,
        title=dict(text=f"{half.capitalize()} Half Dominant Team Map", x=0.5, font=dict(color='white', size=14)),
        shapes=_generate_pitch_shapes_vertical()
    )

    return fig.to_plotly_json()

