import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter

def generate_vertical_pitch_shapes():
    return [
        # Outer boundary
        dict(type="rect", x0=0, y0=0, x1=80, y1=120, line=dict(color="white")),

        # Halfway line
        dict(type="line", x0=0, y0=60, x1=80, y1=60, line=dict(color="white")),

        # Centre circle
        dict(type="circle", x0=40-9.15, y0=60-9.15, x1=40+9.15, y1=60+9.15, line=dict(color="white")),

        # Penalty areas
        dict(type="rect", x0=21.1, y0=0, x1=58.9, y1=16.5, line=dict(color="white")),
        dict(type="rect", x0=21.1, y0=103.5, x1=58.9, y1=120, line=dict(color="white")),

        # Six-yard boxes
        dict(type="rect", x0=30.2, y0=0, x1=49.8, y1=5.5, line=dict(color="white")),
        dict(type="rect", x0=30.2, y0=114.5, x1=49.8, y1=120, line=dict(color="white")),

        # Penalty spots
        dict(type="circle", x0=40-0.3, y0=11-0.3, x1=40+0.3, y1=11+0.3, fillcolor="white", line=dict(color="white")),
        dict(type="circle", x0=40-0.3, y0=109-0.3, x1=40+0.3, y1=109+0.3, fillcolor="white", line=dict(color="white")),

        # Approx penalty arcs
        dict(type="path", path="M31,20 Q40,11 49,20", line=dict(color="white")),
        dict(type="path", path="M31,100 Q40,109 49,100", line=dict(color="white")),
    ]


def generate_match_heatmap_plot(match_data):
    bins = (24, 16)
    sigma = 2.5

    # Clean and extract coordinates
    location_data = match_data[['location', 'team']]
    location_data = location_data[location_data['location'].apply(lambda loc: isinstance(loc, list))]
    location_data[['x', 'y']] = pd.DataFrame(location_data['location'].tolist(), index=location_data.index)

    team_names = list(location_data['team'].unique())
    if len(team_names) != 2:
        raise ValueError(f"Expected exactly 2 teams, found: {team_names}")

    team_a_name, team_b_name = team_names
    team_a = location_data[location_data['team'] == team_a_name]
    team_b = location_data[location_data['team'] == team_b_name]

    x_bins = np.linspace(0, 120, bins[0] + 1)
    y_bins = np.linspace(0, 80, bins[1] + 1)

    a_hist, _, _ = np.histogram2d(team_a['x'].values, team_a['y'].values, bins=[x_bins, y_bins])
    b_hist, _, _ = np.histogram2d(team_b['x'].values, team_b['y'].values, bins=[x_bins, y_bins])
    total = a_hist + b_hist

    with np.errstate(divide='ignore', invalid='ignore'):
        dominance = np.divide(a_hist, total, out=np.full_like(total, 0.5), where=total != 0)
    dominance = np.clip(dominance, 0, 1)
    dominance = gaussian_filter(dominance, sigma=sigma)

    x_centers = 0.5 * (x_bins[:-1] + x_bins[1:])
    y_centers = 0.5 * (y_bins[:-1] + y_bins[1:])

    return {
        "data": [
            {
                "type": "heatmap",
                "x": x_centers.tolist(),  # width = 0 to 120
                "y": y_centers.tolist(),  # height = 0 to 80
                "z": dominance.tolist(),  # no transpose anymore
                "colorscale": "RdBu",
                "reversescale": True,
                "zmin": 0,
                "zmax": 1,
                "showscale": False  # remove colorbar
            }
        ],
        "layout": {
            "title": {
                "text": f"Full Match Dominance: {team_a_name} vs {team_b_name}",
                "font": {"color": "white", "size": 14},
                "x": 0.5
            },
            "xaxis": {
                "range": [0, 120],
                "visible": False,
                "type": "linear"
            },
            "yaxis": {
                "range": [0, 80],
                "visible": False,
                "type": "linear"
            },
            "shapes": generate_vertical_pitch_shapes(),
            "plot_bgcolor": "rgba(0,0,0,0)",
            "paper_bgcolor": "rgba(0,0,0,0)",
            "font": {"color": "white"},
            "autosize": True,
            "margin": {"t": 0, "l": 0, "r": 0, "b": 0},
            "height": None,  # optional; can also let Plotly auto-resize based on container
        }
    }
