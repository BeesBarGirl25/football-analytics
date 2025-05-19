import json
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter
import plotly.graph_objects as go

def generate_dominance_heatmap_json(match_data: pd.DataFrame) -> str:
    bins = (24, 16)
    sigma = 2.5

    location_data = match_data[['location', 'team']].dropna()
    location_data = location_data[location_data['location'].apply(lambda loc: isinstance(loc, list))]
    location_data[['x', 'y']] = pd.DataFrame(location_data['location'].tolist(), index=location_data.index)

    teams = location_data['team'].unique()
    if len(teams) != 2:
        raise ValueError(f"Expected 2 teams, found {teams}")

    team_a, team_b = teams
    team_a_data = location_data[location_data['team'] == team_a]
    team_b_data = location_data[location_data['team'] == team_b]

    x_bins = np.linspace(0, 120, bins[0] + 1)
    y_bins = np.linspace(0, 80, bins[1] + 1)

    a_hist, _, _ = np.histogram2d(team_a_data['x'], team_a_data['y'], bins=[x_bins, y_bins])
    b_hist, _, _ = np.histogram2d(team_b_data['x'], team_b_data['y'], bins=[x_bins, y_bins])
    total = a_hist + b_hist

    with np.errstate(divide='ignore', invalid='ignore'):
        dominance = np.divide(a_hist, total, out=np.full_like(total, 0.5), where=total != 0)
    dominance = gaussian_filter(dominance, sigma=sigma)

    x_centers = 0.5 * (x_bins[:-1] + x_bins[1:])
    y_centers = 0.5 * (y_bins[:-1] + y_bins[1:])

    fig = go.Figure(data=go.Heatmap(
        z=dominance.T,
        x=x_centers,
        y=y_centers,
        zmin=0,
        zmax=1,
        colorscale='RdBu',
        reversescale=True,
        showscale=False
    ))

    fig.update_layout(
        xaxis=dict(range=[0, 120], visible=False),
        yaxis=dict(range=[0, 80], visible=False, scaleanchor="x", scaleratio=2/3),
        margin=dict(t=30, l=0, r=0, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        autosize=True,
        title=dict(text=f"Full Match Dominance: {team_a} vs {team_b}", x=0.5, font=dict(color='white', size=14)),
        shapes=_generate_pitch_shapes()
    )

    # ✅ This is key
    return json.dumps(fig.to_plotly_json(), indent=2)
