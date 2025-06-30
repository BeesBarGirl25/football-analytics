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

def _determine_team_attacking_directions(match_data: pd.DataFrame) -> dict:
    """Determine which direction each team attacks in each half based on shot locations"""
    shot_data = match_data[match_data['type'] == 'Shot'].copy()
    
    if shot_data.empty:
        # Fallback: assume standard setup if no shots available
        teams = match_data['team'].unique()
        return {team: {1: 'right', 2: 'left'} for team in teams}
    
    team_directions = {}
    
    for team in shot_data['team'].unique():
        team_shots = shot_data[shot_data['team'] == team]
        team_directions[team] = {}
        
        for period in [1, 2]:
            period_shots = team_shots[team_shots['period'] == period]
            
            if not period_shots.empty:
                # Extract x-coordinates (length of pitch)
                x_coords = []
                for _, row in period_shots.iterrows():
                    if isinstance(row['location'], list) and len(row['location']) >= 2:
                        x_coords.append(row['location'][0])
                
                if x_coords:
                    avg_x = sum(x_coords) / len(x_coords)
                    # If average shot x > 60 (middle), team attacks towards x=120 (right)
                    # If average shot x < 60, team attacks towards x=0 (left)
                    team_directions[team][period] = 'right' if avg_x > 60 else 'left'
                else:
                    # Fallback based on period
                    team_directions[team][period] = 'right' if period == 1 else 'left'
            else:
                # Fallback based on period
                team_directions[team][period] = 'right' if period == 1 else 'left'
    
    return team_directions


def _preprocess_location_data(match_data: pd.DataFrame, half: str = "full") -> pd.DataFrame:
    """Preprocess and normalize location data with correct attacking direction detection"""
    location_data = match_data[['location', 'team', 'period']].dropna()
    location_data = location_data[location_data['location'].apply(lambda loc: isinstance(loc, list) and len(loc) == 2)]

    teams = location_data['team'].dropna().unique()
    if len(teams) != 1:
        raise ValueError(f"Expected 1 team in match_data, found: {teams}")
    team_name = teams[0]

    # Determine actual attacking directions for this team
    attacking_directions = _determine_team_attacking_directions(match_data)
    team_directions = attacking_directions.get(team_name, {1: 'right', 2: 'left'})

    # Normalize coordinates to consistent attacking direction (always towards y=120/top)
    def normalize(loc, team, period):
        x_sb, y_sb = loc  # StatsBomb: x = length (0-120), y = width (0-80)

        # Get the team's actual attacking direction for this period
        attacking_direction = team_directions.get(period, 'right')
        
        # If team attacks left (towards x=0), flip coordinates to normalize to right attack
        if attacking_direction == 'left':
            x_sb = 120 - x_sb  # Flip length coordinate
            y_sb = 80 - y_sb   # Flip width coordinate

        # Convert to plot coordinates: x = width (horizontal), y = length (vertical)
        return [y_sb, x_sb]

    location_data['normalized_location'] = location_data.apply(
        lambda row: normalize(row['location'], row['team'], row['period']),
        axis=1
    )

    # Assign plot coordinates: x = width (0-80), y = length (0-120)
    location_data[['x', 'y']] = pd.DataFrame(location_data['normalized_location'].tolist(), index=location_data.index)

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


def _get_team_colorscale():
    """Get consistent colorscale for team heatmaps (possession, attack, defense)"""
    return [
        [0.0, "rgb(255,255,255)"],   # White (low activity)
        [0.1, "rgb(240,249,232)"],
        [0.2, "rgb(204,235,197)"],
        [0.3, "rgb(168,221,181)"],
        [0.4, "rgb(123,204,196)"],
        [0.5, "rgb(78,179,211)"],
        [0.6, "rgb(43,140,190)"],
        [0.7, "rgb(8,104,172)"],
        [0.8, "rgb(8,64,129)"],
        [0.9, "rgb(37,52,148)"],
        [1.0, "rgb(68,1,84)"]        # Dark purple (high activity)
    ]


def _normalize_heatmap_data(data: np.ndarray, normalization_type: str = "percentile") -> tuple:
    """
    Normalize heatmap data and return normalized data with consistent zmin/zmax
    
    Args:
        data: Raw heatmap data
        normalization_type: 'percentile', 'minmax', or 'none'
    
    Returns:
        tuple: (normalized_data, zmin, zmax)
    """
    if normalization_type == "percentile":
        # Use 95th percentile to avoid outliers affecting the scale
        p95 = np.percentile(data[data > 0], 95) if np.any(data > 0) else 1.0
        normalized_data = np.clip(data / p95, 0, 1)
        return normalized_data, 0, 1
    elif normalization_type == "minmax":
        # Standard min-max normalization
        data_min, data_max = data.min(), data.max()
        if data_max > data_min:
            normalized_data = (data - data_min) / (data_max - data_min)
        else:
            normalized_data = data
        return normalized_data, 0, 1
    else:  # normalization_type == "none"
        # No normalization, use raw data
        return data, None, None


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
    
    # Set defaults based on heatmap type - ALL use dominance colorscale for consistency
    if heatmap_type == "dominance":
        bins = bins or (24, 16)
        sigma = sigma or 1.5
        colorscale = colorscale or _get_dominance_colorscale()
        title_prefix = title_prefix or "Dominant Team Map"
        normalization_type = "none"  # Dominance already normalized to 0-1
    elif heatmap_type == "possession":
        bins = bins or (48, 32)
        sigma = sigma or 2.5
        colorscale = colorscale or _get_dominance_colorscale()  # Use dominance colorscale
        title_prefix = title_prefix or "Possession Map"
        normalization_type = "percentile"
    elif heatmap_type == "attack":
        bins = bins or (48, 32)
        sigma = sigma or 2.5
        colorscale = colorscale or _get_dominance_colorscale()  # Use dominance colorscale
        title_prefix = title_prefix or "Attack Map"
        normalization_type = "percentile"
        phase_filter = _generate_phase_filters("attack")
    elif heatmap_type == "defense":
        bins = bins or (48, 32)
        sigma = sigma or 2.5
        colorscale = colorscale or _get_dominance_colorscale()  # Use dominance colorscale
        title_prefix = title_prefix or "Defense Map"
        normalization_type = "percentile"
        phase_filter = _generate_phase_filters("defense")
    else:
        raise ValueError(f"Unknown heatmap_type: {heatmap_type}. Must be 'dominance', 'possession', 'attack', or 'defense'")
    
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
        
        # Determine actual attacking directions for both teams
        attacking_directions = _determine_team_attacking_directions(match_data)
        team_a_directions = attacking_directions.get(team_a, {1: 'right', 2: 'left'})
        team_b_directions = attacking_directions.get(team_b, {1: 'left', 2: 'right'})
        
        # Normalize coordinates so teams attack in consistent direction for dominance comparison
        def normalize_dominance(loc, team, period):
            x_sb, y_sb = loc  # StatsBomb: x = length (0-120), y = width (0-80)
            
            # Get the team's actual attacking direction for this period
            if team == team_a:
                attacking_direction = team_a_directions.get(period, 'right')
                # Normalize team_a to always attack towards y=120 (top of pitch)
                if attacking_direction == 'left':
                    x_sb = 120 - x_sb  # Flip length coordinate
                    y_sb = 80 - y_sb   # Flip width coordinate
            else:  # team_b
                attacking_direction = team_b_directions.get(period, 'left')
                # Normalize team_b to always attack towards y=0 (bottom of pitch)
                if attacking_direction == 'right':
                    x_sb = 120 - x_sb  # Flip length coordinate
                    y_sb = 80 - y_sb   # Flip width coordinate
            
            # Convert to plot coordinates: x = width (horizontal), y = length (vertical)
            return [y_sb, x_sb]
        
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
        zmin, zmax = 0, 1  # Set explicit range for dominance heatmaps
        
    else:
        # For single-team heatmaps (possession, attack, defense), use the preprocessing function
        location_data = _preprocess_location_data(match_data, half)
        
        if heatmap_type == "possession":
            team_hist, _, _ = np.histogram2d(location_data['y'], location_data['x'], bins=[y_bins, x_bins])
            raw_heatmap_data = gaussian_filter(team_hist, sigma=sigma)
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
            raw_heatmap_data = gaussian_filter(attack_hist, sigma=sigma)
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
            raw_heatmap_data = gaussian_filter(defense_hist, sigma=sigma)
        
        # Apply normalization to team heatmaps
        heatmap_data, zmin, zmax = _normalize_heatmap_data(raw_heatmap_data, normalization_type)
    
    # Create Plotly data - ensure all numpy arrays are converted to lists
    heatmap_kwargs = {
        'z': heatmap_data.tolist(),  # Always convert to list
        'x': x_centers.tolist(),
        'y': y_centers.tolist(),
        'colorscale': colorscale,
        'showscale': True,
        'type': 'heatmap'
    }
    
    # Add zmin/zmax for all heatmaps to ensure consistent scaling
    if zmin is not None:
        heatmap_kwargs['zmin'] = zmin
    if zmax is not None:
        heatmap_kwargs['zmax'] = zmax
    
    # No reversescale needed since all heatmaps use the same color scheme
    
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
