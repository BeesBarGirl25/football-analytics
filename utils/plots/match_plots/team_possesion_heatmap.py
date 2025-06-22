from utils.plots.match_plots.heatmap_per_game import _generate_pitch_shapes_vertical
import pandas as pd
import numpy as np
from scipy.ndimage import gaussian_filter
import plotly.graph_objects as go

def generate_team_match_heatmap(match_data: pd.DataFrame, half: str = "full") -> dict:
    bins = (48, 32)
    sigma = 2.5
    epsilon = 1e-6  # Fix for edge bin exclusions

    x_bins = np.linspace(0, 80 + epsilon, bins[1] + 1)  # X: pitch width
    y_bins = np.linspace(0, 120 + epsilon, bins[0] + 1)  # Y: pitch length
    location_data = match_data[['location', 'team', 'period']].dropna()
    location_data = location_data[location_data['location'].apply(lambda loc: isinstance(loc, list))]
    location_data[['y', 'x']] = pd.DataFrame(location_data['location'].tolist(), index=location_data.index)

    if half == "first":
        location_data = location_data[location_data['period'] == 1]
    elif half == "second":
        location_data = location_data[location_data['period'] == 2]

    # 2D HISTOGRAM: y first (vertical), x second (horizontal)
    team_hist, _, _ = np.histogram2d(location_data['y'], location_data['x'], bins=[y_bins, x_bins])

    # SMOOTH THE DATA
    team_hist = gaussian_filter(team_hist, sigma=sigma)

    # BIN CENTERS
    x_centers = 0.5 * (x_bins[:-1] + x_bins[1:])  # pitch width (0 to 80)
    y_centers = 0.5 * (y_bins[:-1] + y_bins[1:])  # pitch length (0 to 120)

    fig = go.Figure(data = go.Heatmap(
        z=team_hist,
        x=x_centers,
        y=y_centers,
        colorscale='Viridis',
        reversescale=True
    ))

    fig.update_layout(
        xaxis=dict(range=[0, 80], visible=False),
        yaxis=dict(range=[0, 120], visible=False, scaleanchor="x", scaleratio=1.5),
        margin=dict(t=30, l=0, r=0, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        autosize=True,
        title=dict(text=f"{half.capitalize()} Half Possesion", x=0.5, font=dict(color='white', size=14)),
        shapes=_generate_pitch_shapes_vertical()
    )

    return fig.to_plotly_json()