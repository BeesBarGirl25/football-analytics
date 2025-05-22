import json
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter
import plotly.graph_objects as go

def _generate_pitch_shapes():
    return [
        dict(type="rect", x0=0, y0=0, x1=80, y1=120, line=dict(color="white")),
        dict(type="line", x0=0, y0=60, x1=80, y1=60, line=dict(color="white")),
        dict(type="circle", x0=40-9.15, y0=60-9.15, x1=40+9.15, y1=60+9.15, line=dict(color="white")),
        dict(type="rect", x0=21.1, y0=0, x1=58.9, y1=16.5, line=dict(color="white")),
        dict(type="rect", x0=21.1, y0=103.5, x1=58.9, y1=120, line=dict(color="white")),
        dict(type="rect", x0=30.2, y0=0, x1=49.8, y1=5.5, line=dict(color="white")),
        dict(type="rect", x0=30.2, y0=114.5, x1=49.8, y1=120, line=dict(color="white")),
        dict(type="circle", x0=40-0.3, y0=11-0.3, x1=40+0.3, y1=11+0.3, fillcolor="white", line=dict(color="white")),
        dict(type="circle", x0=40-0.3, y0=109-0.3, x1=40+0.3, y1=109+0.3, fillcolor="white", line=dict(color="white")),
        dict(type="path", path="M31,20 Q40,11 49,20", line=dict(color="white")),
        dict(type="path", path="M31,100 Q40,109 49,100", line=dict(color="white")),
    ]


def generate_dominance_heatmap_json(match_data: pd.DataFrame) -> str:
    bins = (24, 16)
    sigma = 2.5

    # Extract and clean location data
    location_data = match_data[['location', 'team']].dropna()
    location_data = location_data[location_data['location'].apply(lambda loc: isinstance(loc, list))]
    location_data[['x', 'y']] = pd.DataFrame(location_data['location'].tolist(), index=location_data.index)

    teams = location_data['team'].unique()
    if len(teams) != 2:
        raise ValueError(f"Expected 2 teams, found: {teams}")

    team_a, team_b = teams
    team_a_data = location_data[location_data['team'] == team_a]
    team_b_data = location_data[location_data['team'] == team_b]

    # Bin setup
    x_bins = np.linspace(0, 80, bins[1] + 1)
    y_bins = np.linspace(0, 120, bins[0] + 1)

    # Heatmap histograms
    a_hist, _, _ = np.histogram2d(team_a_data['x'], team_a_data['y'], bins=[x_bins, y_bins])
    b_hist, _, _ = np.histogram2d(team_b_data['x'], team_b_data['y'], bins=[x_bins, y_bins])
    total = a_hist + b_hist

    with np.errstate(divide='ignore', invalid='ignore'):
        dominance = np.divide(a_hist, total, out=np.full_like(total, 0.5), where=total != 0)

    dominance = gaussian_filter(dominance, sigma=sigma)

    # Compute bin centers
    x_centers = 0.5 * (x_bins[:-1] + x_bins[1:])
    y_centers = 0.5 * (y_bins[:-1] + y_bins[1:])

    # Convert to lists to prevent Plotly 'bdata' issue
    z = dominance.tolist()
    x = x_centers.tolist()
    y = y_centers.tolist()

    # Debug logs
    print("[DEBUG] Types — x:", type(x), " y:", type(y), " z:", type(z))
    print("[DEBUG] Sample x[0:3]:", x[:3])
    print("[DEBUG] Sample z[0]:", z[0][:3])

    # Build Plotly figure
    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=x,
        y=y,
        zmin=0,
        zmax=1,
        colorscale="RdBu",
        reversescale=True,
        showscale=False
    ))

    fig.update_layout(
        title=dict(text=f"Full Match Dominance: {team_a} vs {team_b}", x=0.5, font=dict(color='white', size=14)),
        xaxis=dict(range=[0, 80], visible=False),
        yaxis=dict(range=[0, 120], visible=False, scaleanchor="x", scaleratio=1.5),
        margin=dict(t=30, l=0, r=0, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        shapes=_generate_pitch_shapes(),
        autosize=True,
    )

    return json.dumps(fig.to_plotly_json(), indent=2)
