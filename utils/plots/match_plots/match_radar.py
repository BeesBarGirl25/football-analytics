import plotly.graph_objects as go
import pandas as pd
import json

def extract_and_filter_stats(stats_list, desired_stats):
    """Extract and filter stats from team stats list"""
    raw = {}
    for stat in stats_list:
        name = stat["stat_name"]
        value = stat["value"]
        if name not in desired_stats:
            continue
        if isinstance(value, str):
            if value.endswith('%'):
                value = float(value.strip('%'))
            else:
                try:
                    value = float(value)
                except ValueError:
                    continue
        raw[name] = value
    return raw

def normalize_stats(stats_a, stats_b, radar_stats):
    """Normalize stats between two teams for radar chart with improved scaling"""
    df = pd.DataFrame([stats_a, stats_b])
    df = df[radar_stats]
    
    # Get min and max for normalization
    min_val = df.min()
    max_val = df.max()
    
    # Add a small buffer to max to avoid extreme scaling when values are close
    range_val = max_val - min_val
    max_val = max_val + range_val * 0.1
    
    # Normalize with a more balanced approach
    norm_df = (df - min_val) / (max_val - min_val)
    norm_df = norm_df.fillna(0)
    
    # Apply a smaller floor boost and slight scaling to avoid extreme min/max
    min_floor = 0.05
    norm_df = norm_df * 0.9 + min_floor
    
    return norm_df.iloc[0].to_dict(), norm_df.iloc[1].to_dict()

def generate_team_radar_plot(home_team_stats, away_team_stats, home_team_name, away_team_name):
    """Generate radar plot for team comparison using team stats data"""
    radar_stats = [
        "Goals",
        "xG",
        "Total Shots",
        "Shots on Target",
        "Key Passes",
        "Progressive Passes",
        "Carries into Final Third",
        "Final Third Entries",
        "Tackles Won",
        "Interceptions"
    ]
    
    # Extract stats from the team stats structure
    home_stats_list = home_team_stats["team_stats"]["stats"]
    away_stats_list = away_team_stats["team_stats"]["stats"]
    
    stats_home = extract_and_filter_stats(home_stats_list, radar_stats)
    stats_away = extract_and_filter_stats(away_stats_list, radar_stats)

    norm_home, norm_away = normalize_stats(stats_home, stats_away, radar_stats)

    # Create traces
    trace_home = go.Scatterpolar(
        r=[norm_home.get(stat, 0) for stat in radar_stats],
        theta=radar_stats,
        fill='toself',
        name=home_team_name,
        line=dict(color='#1f77b4'),
        fillcolor='rgba(31, 119, 180, 0.3)'
    )
    
    trace_away = go.Scatterpolar(
        r=[norm_away.get(stat, 0) for stat in radar_stats],
        theta=radar_stats,
        fill='toself',
        name=away_team_name,
        line=dict(color='#ff7f0e'),
        fillcolor='rgba(255, 127, 14, 0.3)'
    )

    import plotly.io as pio
    
    fig = go.Figure(
        data=[trace_home, trace_away],
        layout=go.Layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1],
                    showticklabels=False,
                    gridcolor='rgba(255, 255, 255, 0.2)'
                ),
                angularaxis=dict(
                    tickfont=dict(size=10),
                    gridcolor='rgba(255, 255, 255, 0.2)'
                ),
                bgcolor='rgba(0, 0, 0, 0)'
            ),
            paper_bg='rgba(0, 0, 0, 0)',
            plot_bg='rgba(0, 0, 0, 0)',
            showlegend=True,
            title={
                'text': "Team Performance Comparison",
                'x': 0.5,
                'xanchor': 'center',
                'font': dict(color='white')
            },
            font=dict(size=12, color='white'),
            margin=dict(l=80, r=80, t=80, b=80),
            height=400
        )
    )
    
    # Convert the figure to a JSON-serializable format using plotly.io
    return json.loads(pio.to_json(fig, validate=False, engine="json"))

# Legacy functions for backward compatibility
def plot_team_comparison_radar_from_raw(stats_a_list, stats_b_list, team_a_name="Team A", team_b_name="Team B"):
    """Legacy function - use generate_team_radar_plot instead"""
    radar_stats = [
        "Goals",
        "xG",
        "Total Shots",
        "Shots on Target",
        "Key Passes",
        "Progressive Passes",
        "Carries into Final Third",
        "Final Third Entries",
        "Tackles Won",
        "Interceptions"
    ]
    
    stats_a = extract_and_filter_stats(stats_a_list, radar_stats)
    stats_b = extract_and_filter_stats(stats_b_list, radar_stats)

    norm_a, norm_b = normalize_stats(stats_a, stats_b, radar_stats)

    return get_team_comparison_radar_data_layout(norm_a, norm_b, radar_stats, team_a_name, team_b_name)

def get_team_comparison_radar_data_layout(norm_a, norm_b, radar_stats, team_a_name, team_b_name):
    """Legacy function - use generate_team_radar_plot instead"""
    trace_a = go.Scatterpolar(
        r=[norm_a[stat] for stat in radar_stats],
        theta=radar_stats,
        fill='toself',
        name=team_a_name
    )
    
    trace_b = go.Scatterpolar(
        r=[norm_b[stat] for stat in radar_stats],
        theta=radar_stats,
        fill='toself',
        name=team_b_name
    )

    layout = go.Layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=True,
        title="Team Performance Comparison Radar"
    )

    return [trace_a, trace_b], layout
