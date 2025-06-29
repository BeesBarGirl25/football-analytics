import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.ndimage import gaussian_filter


def _generate_pitch_shapes_vertical():
    """Generate pitch shapes for vertical orientation"""
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


def _generate_phase_filters(phase: str):
    "Generate phase filters for match data depending on the phase of play."
    # Define event types by phase
    attacking_types = ['Pass', 'Carry', 'Dribble', 'Shot', 'Foul Won']
    defensive_types = ['Interception', 'Clearance', 'Block', 'Ball Recovery', 'Duel', 'Foul Committed']
    
    if phase == "attack":
        event_types = attacking_types
    elif phase == "defense":
        event_types = defensive_types
    else:
        raise ValueError("phase must be 'attack' or 'defense'")
    return event_types

def _preprocess_location_data(match_data: pd.DataFrame, half: str = "full") -> pd.DataFrame:
    """Preprocess and normalize location data so the team always attacks bottom-to-top (120 → 0)"""
    location_data = match_data[['location', 'team', 'period']].dropna()
    location_data = location_data[location_data['location'].apply(lambda loc: isinstance(loc, list) and len(loc) == 2)]

    teams = location_data['team'].dropna().unique()
    if len(teams) != 1:
        raise ValueError(f"Expected 1 team in match_data, found: {teams}")
    team_name = teams[0]

    # Normalize coordinates to match left-to-right attacking direction
    def normalize(loc, team, period):
        x_sb, y_sb = loc  # x = length (0-120), y = width (0-80)

        # Flip direction for second half if needed
        if (team == team_name and period in [2, 4]) or (team != team_name and period in [1, 3]):
            x_sb = 120 - x_sb
            y_sb = 80 - y_sb

        return [y_sb, x_sb]  # Now: y (length) → vertical axis, x (width) → horizontal axis

    location_data['normalized_location'] = location_data.apply(
        lambda row: normalize(row['location'], row['team'], row['period']),
        axis=1
    )

    # Assign vertical (length) to y, horizontal (width) to x
    location_data[['y', 'x']] = pd.DataFrame(location_data['normalized_location'].tolist(), index=location_data.index)

    # Half filtering
    if half == "first":
        location_data = location_data[location_data['period'] == 1]
    elif half == "second":
        location_data = location_data[location_data['period'] == 2]

    return location_data




def _create_bins_and_centers(bins: tuple, epsilon: float = 1e-6):
    """Create bins and centers for histogram"""
    x_bins = np.linspace(0, 80 + epsilon, bins[1] + 1)  # X: pitch width
    y_bins = np.linspace(0, 120 + epsilon, bins[0] + 1)  # Y: pitch length
    
    x_centers = 0.5 * (x_bins[:-1] + x_bins[1:])
    y_centers = 0.5 * (y_bins[:-1] + y_bins[1:])
    
    return x_bins, y_bins, x_centers, y_centers


def _get_dominance_colorscale():
    """Get the custom colorscale for dominance heatmaps"""
    return [
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
    ]


def generate_heatmap(
    match_data: pd.DataFrame,
    heatmap_type: str,
    half: str = "full",
    bins: tuple = None,
    sigma: float = None,
    colorscale = None,
    title_prefix: str = None
) -> dict:
    """
    Unified heatmap generation function
    
    Args:
        match_data: DataFrame containing match event data
        heatmap_type: 'dominance', 'possession', 'attack', or 'defense'
        half: 'full', 'first', or 'second'
        bins: Custom bin size (y, x). Defaults: dominance=(24,16), possession=(48,32)
        sigma: Gaussian filter sigma. Defaults: dominance=1.5, possession=2.5
        colorscale: Custom colorscale. Defaults: dominance=custom, possession='Viridis'
        title_prefix: Custom title prefix
    
    Returns:
        Plotly figure as JSON dict
    """
    
    # Set defaults based on heatmap type
    if heatmap_type == "dominance":
        bins = bins or (24, 16)
        sigma = sigma or 1.5
        colorscale = colorscale or _get_dominance_colorscale()
        title_prefix = title_prefix or "Dominant Team Map"
        zmin, zmax = 0, 1
    elif heatmap_type == "possession":
        bins = bins or (48, 32)
        sigma = sigma or 2.5
        colorscale = colorscale or 'Viridis'
        title_prefix = title_prefix or "Possesion"
        zmin, zmax = None, None
    elif heatmap_type == "attack":
        bins = bins or (48, 32)
        sigma = sigma or 2.5
        colorscale = colorscale or 'Viridis'
        title_prefix = title_prefix or "Attack Map"
        zmin, zmax = None, None
        phase_filter = _generate_phase_filters("attack")
    elif heatmap_type == "defense":
        bins = bins or (48, 32)
        sigma = sigma or 2.5
        colorscale = colorscale or 'Viridis'
        title_prefix = title_prefix or "Defense Map"
        zmin, zmax = None, None
        phase_filter = _generate_phase_filters("defense")
    else:
        raise ValueError(f"Unknown heatmap_type: {heatmap_type}. Must be 'dominance' or 'possession'")
    
    # Create bins and centers
    x_bins, y_bins, x_centers, y_centers = _create_bins_and_centers(bins)
    
    # Generate heatmap data based on type
    if heatmap_type == "dominance":
        # For dominance heatmaps, we need to process both teams' data separately with normalization
        location_data = match_data[['location', 'team', 'period']].dropna()
        location_data = location_data[location_data['location'].apply(lambda loc: isinstance(loc, list) and len(loc) == 2)]
        
        # Extract coordinates
        location_data[['x', 'y']] = pd.DataFrame(location_data['location'].tolist(), index=location_data.index)
        
        # Apply half filter
        if half == "first":
            location_data = location_data[location_data['period'] == 1]
        elif half == "second":
            location_data = location_data[location_data['period'] == 2]
        
        teams = location_data['team'].unique()
        if len(teams) != 2:
            raise ValueError(f"Expected 2 teams for dominance heatmap, found {teams}")
        
        team_a, team_b = teams
        
        # Normalize coordinates so teams attack in consistent direction
        def normalize_dominance(loc, team, period):
            x, y = loc
            # For team_a: normalize so they always attack towards y=120
            # For team_b: normalize so they always attack towards y=0
            if team == team_a:
                # Team A attacks towards y=120 in periods 1,3 and towards y=0 in periods 2,4
                if period in [2, 4]:
                    return [120 - y, 80 - x]  # Fixed: y should be transformed by 120, x by 80
                return [y, x]  # Fixed: return [y, x] not [x, y]
            else:  # team_b
                # Team B attacks towards y=0 in periods 1,3 and towards y=120 in periods 2,4
                if period in [1, 3]:
                    return [120 - y, 80 - x]  # Fixed: y should be transformed by 120, x by 80
                return [y, x]  # Fixed: return [y, x] not [x, y]
        
        location_data['normalized_location'] = location_data.apply(
            lambda row: normalize_dominance([row['x'], row['y']], row['team'], row['period']),
            axis=1
        )
        
        location_data[['norm_x', 'norm_y']] = pd.DataFrame(location_data['normalized_location'].tolist(), index=location_data.index)
        
        team_a_data = location_data[location_data['team'] == team_a]
        team_b_data = location_data[location_data['team'] == team_b]
        
        # Use normalized coordinates for histogram
        a_hist, _, _ = np.histogram2d(team_a_data['norm_y'], team_a_data['norm_x'], bins=[y_bins, x_bins])
        b_hist, _, _ = np.histogram2d(team_b_data['norm_y'], team_b_data['norm_x'], bins=[y_bins, x_bins])
        
        total_actions = a_hist + b_hist
        with np.errstate(divide='ignore', invalid='ignore'):
            dominance_ratio = np.divide(a_hist, total_actions, where=total_actions != 0)
            dominance_ratio = np.nan_to_num(dominance_ratio, nan=0.5)  # Default to neutral if zero actions
        
        heatmap_data = gaussian_filter(dominance_ratio, sigma=sigma)
        heatmap_data = np.clip(heatmap_data, 0.0, 1.0)
        
    else:
        # For single-team heatmaps (possession, attack, defense), use the preprocessing function
        location_data = _preprocess_location_data(match_data, half)
        
        if heatmap_type == "possession":
            team_hist, _, _ = np.histogram2d(location_data['y'], location_data['x'], bins=[y_bins, x_bins])
            heatmap_data = gaussian_filter(team_hist, sigma=sigma)
        elif heatmap_type == "attack":
            # Check if we have the required column for filtering
            if 'type' in match_data.columns:
                # Filter original match data by event type, then preprocess
                attack_match_data = match_data[match_data['type'].isin(phase_filter)]
                if not attack_match_data.empty:
                    attack_location_data = _preprocess_location_data(attack_match_data, half)
                    attack_hist, _, _ = np.histogram2d(attack_location_data['y'], attack_location_data['x'], bins=[y_bins, x_bins])
                else:
                    attack_hist = np.zeros((len(y_bins)-1, len(x_bins)-1))
            else:
                # Fallback to all location data if no type column
                attack_hist, _, _ = np.histogram2d(location_data['y'], location_data['x'], bins=[y_bins, x_bins])
            heatmap_data = gaussian_filter(attack_hist, sigma=sigma)
        elif heatmap_type == "defense":
            # Check if we have the required column for filtering
            if 'type' in match_data.columns:
                # Filter original match data by event type, then preprocess
                defense_match_data = match_data[match_data['type'].isin(phase_filter)]
                if not defense_match_data.empty:
                    defense_location_data = _preprocess_location_data(defense_match_data, half)
                    defense_hist, _, _ = np.histogram2d(defense_location_data['y'], defense_location_data['x'], bins=[y_bins, x_bins])
                else:
                    defense_hist = np.zeros((len(y_bins)-1, len(x_bins)-1))
            else:
                # Fallback to all location data if no type column
                defense_hist, _, _ = np.histogram2d(location_data['y'], location_data['x'], bins=[y_bins, x_bins])
            heatmap_data = gaussian_filter(defense_hist, sigma=sigma)
    
    # Create Plotly data - ensure all numpy arrays are converted to lists
    heatmap_kwargs = {
        'z': heatmap_data.tolist(),  # Always convert to list
        'x': x_centers.tolist(),
        'y': y_centers.tolist(),
        'colorscale': colorscale,
        'showscale': True,
        'type': 'heatmap'
    }
    
    # Add zmin/zmax for dominance heatmaps
    if zmin is not None:
        heatmap_kwargs['zmin'] = zmin
    if zmax is not None:
        heatmap_kwargs['zmax'] = zmax
    
    # Add reversescale for possession heatmaps
    if heatmap_type == "possession":
        heatmap_kwargs['reversescale'] = True
    
    # Create data array
    data = [heatmap_kwargs]
    
    # Configure layout
    layout = {
        'xaxis': {'range': [0, 80], 'visible': False, 'fixedrange': True},
        'yaxis': {'range': [0, 120], 'visible': False, 'scaleanchor': "x", 'scaleratio': 1.5, 'fixedrange': True},
        'margin': {'t': 30, 'l': 0, 'r': 0, 'b': 0},
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'autosize': True,
        'width': None,
        'height': None,
        'title': {'text': f"{half.capitalize()} Half {title_prefix}", 'x': 0.5, 'font': {'color': 'white', 'size': 14}},
        'shapes': _generate_pitch_shapes_vertical()
    }
    
    return {"data": data, "layout": layout}


# Backward compatibility wrapper functions
def generate_dominance_heatmap_json(match_data: pd.DataFrame, half: str = "full") -> dict:
    """Backward compatibility wrapper for dominance heatmaps"""
    return generate_heatmap(match_data, 'dominance', half)


def generate_team_match_heatmap(match_data: pd.DataFrame, half: str = "full") -> dict:
    """Backward compatibility wrapper for team possession heatmaps"""
    return generate_heatmap(match_data, 'possession', half)

def generate_team_attack_heatmap(match_data: pd.DataFrame, half: str = "full") -> dict:
    """Backward compatibility wrapper for team attack heatmaps"""
    return generate_heatmap(match_data, 'attack', half)

def generate_team_defense_heatmap(match_data: pd.DataFrame, half: str = "full") -> dict:
    """Backward compatibility wrapper for team defense heatmaps"""
    return generate_heatmap(match_data, 'defense', half)
