import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.ndimage import gaussian_filter


def _generate_pitch_shapes_vertical():
    return [
        dict(type="rect", x0=0, y0=0, x1=80, y1=120, line=dict(color="black")),
        dict(type="line", x0=0, y0=60, x1=80, y1=60, line=dict(color="black")),
        dict(type="circle", x0=40 - 9.15, y0=60 - 9.15, x1=40 + 9.15, y1=60 + 9.15, line=dict(color="black")),
        dict(type="rect", x0=30, y0=0, x1=50, y1=18, line=dict(color="black")),
        dict(type="rect", x0=30, y0=102, x1=50, y1=120, line=dict(color="black")),
        dict(type="rect", x0=36, y0=0, x1=44, y1=6, line=dict(color="black")),
        dict(type="rect", x0=36, y0=114, x1=44, y1=120, line=dict(color="black")),
        dict(type="circle", x0=39.7, y0=11.7, x1=40.3, y1=12.3, fillcolor="black", line=dict(color="black")),
        dict(type="circle", x0=39.7, y0=108.7, x1=40.3, y1=109.3, fillcolor="black", line=dict(color="black"))
    ]


def generate_dominance_heatmap_json(match_df, home_team, away_team):
    # Extract and bin locations
    location_data = match_df[['location', 'team']].copy()
    location_data = location_data[location_data['location'].apply(lambda loc: isinstance(loc, list))]

    location_data[['x', 'y']] = pd.DataFrame(location_data['location'].tolist(), index=location_data.index)
    home_data = location_data[location_data['team'] == home_team]
    away_data = location_data[location_data['team'] == away_team]

    # Create 2D histograms
    bins = (24, 16)
    pitch_length = 120
    pitch_width = 80

    def make_grid(data):
        heatmap, xedges, yedges = np.histogram2d(
            data['y'], data['x'], bins=bins, range=[[0, pitch_length], [0, pitch_width]]
        )
        return gaussian_filter(heatmap, sigma=1)

    home_grid = make_grid(home_data)
    away_grid = make_grid(away_data)

    # Normalize and subtract
    max_val = max(home_grid.max(), away_grid.max(), 1)
    combined_grid = (home_grid - away_grid) / max_val

    # Build heatmap
    x = np.linspace(2.5, pitch_width - 2.5, bins[1])
    y = np.linspace(2.5, pitch_length - 2.5, bins[0])

    fig = go.Figure(data=go.Heatmap(
        z=combined_grid,
        x=x,
        y=y,
        colorscale=[[0, 'rgb(5,48,97)'], [0.5, 'rgb(247,247,247)'], [1, 'rgb(103,0,31)']],
        zmin=-1,
        zmax=1,
        zmid=0,
        showscale=True,
        colorbar=dict(
            title='Activity Edge',
            tickformat=".0f"
        )
    ))

    # Add pitch lines or shapes here if needed
    fig.update_layout(
        autosize=True,
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        title=dict(text="Full Half Activity Map", x=0.5, font=dict(size=16)),
        margin=dict(t=30, l=0, r=0, b=0),
        xaxis=dict(
            visible=False,
            type='linear',
            range=[0, pitch_width],
            autorange=False  # Force it to respect the range
        ),
        yaxis=dict(
            visible=False,
            type='linear',
            range=[0, pitch_length],
            autorange=False
        ),
        shapes=_generate_pitch_shapes_vertical()
    )

    return fig

