# Extending the Football Dashboard System

This guide provides step-by-step instructions for extending the Football Dashboard with new features, integrations, and capabilities.

## 📚 Table of Contents

- [System Extension Overview](#system-extension-overview)
- [Adding New Data Sources](#adding-new-data-sources)
- [Creating Custom Analytics](#creating-custom-analytics)
- [Building New Visualizations](#building-new-visualizations)
- [Integrating External APIs](#integrating-external-apis)
- [Performance Optimization](#performance-optimization)
- [Advanced Features](#advanced-features)
- [Maintenance and Updates](#maintenance-and-updates)

## 🔧 System Extension Overview

### Extension Points

The Football Dashboard is designed with several key extension points:

1. **Data Layer**: Add new data sources and ETL processes
2. **Analytics Layer**: Create custom statistical calculations
3. **Visualization Layer**: Build new plot types and interactive components
4. **API Layer**: Add new endpoints and data services
5. **Frontend Layer**: Create new pages and user interfaces

### Extension Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Extension Points                         │
├─────────────────────────────────────────────────────────────┤
│  New Data Sources → ETL → Analytics → Plots → Frontend      │
│       ↓               ↓        ↓         ↓        ↓         │
│  - APIs            - Custom  - New     - Custom - New       │
│  - Files           - Calcs   - Stats   - Plots  - Pages     │
│  - Databases       - Models  - Metrics - Views  - Features  │
└─────────────────────────────────────────────────────────────┘
```

## 📊 Adding New Data Sources

### 1. External API Integration

#### Step 1: Create API Client

```python
# utils/external_apis/new_api_client.py
import requests
import json
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class NewAPIClient:
    """Client for integrating with a new football data API"""
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
    
    def get_matches(self, competition_id: int, season: str) -> List[Dict]:
        """Fetch matches from the new API"""
        try:
            url = f"{self.base_url}/competitions/{competition_id}/matches"
            params = {'season': season}
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Fetched {len(data.get('matches', []))} matches")
            
            return self._transform_matches(data.get('matches', []))
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
    
    def get_match_events(self, match_id: int) -> List[Dict]:
        """Fetch detailed match events"""
        try:
            url = f"{self.base_url}/matches/{match_id}/events"
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            return self._transform_events(data.get('events', []))
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch match events: {e}")
            raise
    
    def _transform_matches(self, raw_matches: List[Dict]) -> List[Dict]:
        """Transform API match data to our format"""
        transformed = []
        
        for match in raw_matches:
            transformed.append({
                'match_id': match['id'],
                'home_team': match['homeTeam']['name'],
                'away_team': match['awayTeam']['name'],
                'match_date': match['utcDate'],
                'home_score': match['score']['fullTime']['homeTeam'],
                'away_score': match['score']['fullTime']['awayTeam'],
                'competition_id': match['competition']['id'],
                'season': match['season']['startDate'][:4]
            })
        
        return transformed
    
    def _transform_events(self, raw_events: List[Dict]) -> List[Dict]:
        """Transform API event data to our format"""
        transformed = []
        
        for event in raw_events:
            transformed.append({
                'minute': event.get('minute'),
                'type': event.get('type'),
                'team': event.get('team', {}).get('name'),
                'player': event.get('player', {}).get('name'),
                'x': event.get('coordinates', {}).get('x'),
                'y': event.get('coordinates', {}).get('y'),
                'outcome': event.get('outcome')
            })
        
        return transformed
```

#### Step 2: Create ETL Process

```python
# data/etl/new_api_etl.py
from utils.external_apis.new_api_client import NewAPIClient
from models import Match, MatchPlot, db
from utils.analytics.match_analytics.match_analysis_utils import generate_team_stats
import pandas as pd
import os

def sync_new_api_data():
    """Sync data from the new API"""
    
    # Initialize API client
    api_key = os.environ.get('NEW_API_KEY')
    if not api_key:
        raise ValueError("NEW_API_KEY environment variable not set")
    
    client = NewAPIClient(api_key, 'https://api.newprovider.com/v1')
    
    # Fetch competitions
    competitions = [
        {'id': 1, 'name': 'Premier League', 'season': '2023'},
        {'id': 2, 'name': 'La Liga', 'season': '2023'}
    ]
    
    for comp in competitions:
        print(f"Processing {comp['name']}...")
        
        # Fetch matches
        matches = client.get_matches(comp['id'], comp['season'])
        
        for match_data in matches:
            # Check if match already exists
            existing_match = Match.query.filter_by(
                match_id=match_data['match_id']
            ).first()
            
            if existing_match:
                print(f"Match {match_data['match_id']} already exists, skipping...")
                continue
            
            # Create new match record
            new_match = Match(
                match_id=match_data['match_id'],
                home_team=match_data['home_team'],
                away_team=match_data['away_team'],
                match_date=match_data['match_date'],
                home_score=match_data['home_score'],
                away_score=match_data['away_score'],
                competition_id=match_data['competition_id']
            )
            
            db.session.add(new_match)
            
            # Fetch and process match events
            try:
                events = client.get_match_events(match_data['match_id'])
                process_match_events(match_data['match_id'], events)
                
            except Exception as e:
                print(f"Failed to process events for match {match_data['match_id']}: {e}")
        
        db.session.commit()
        print(f"✓ Processed {len(matches)} matches for {comp['name']}")

def process_match_events(match_id: int, events: List[Dict]):
    """Process match events and generate plots"""
    
    # Convert to DataFrame
    df = pd.DataFrame(events)
    
    if df.empty:
        print(f"No events found for match {match_id}")
        return
    
    # Get team names
    home_team = df[df['team'].notna()]['team'].iloc[0] if not df.empty else 'Home'
    away_team = df[df['team'].notna() & (df['team'] != home_team)]['team'].iloc[0] if len(df['team'].unique()) > 1 else 'Away'
    
    # Generate analytics
    home_data = df[df['team'] == home_team]
    away_data = df[df['team'] == away_team]
    
    home_stats = generate_team_stats(home_data, home_team)
    away_stats = generate_team_stats(away_data, away_team)
    
    # Save to database
    save_plot(match_id, 'home_team_stats', home_stats)
    save_plot(match_id, 'away_team_stats', away_stats)

def save_plot(match_id: int, plot_type: str, plot_data: Dict):
    """Save plot data to database"""
    plot = MatchPlot(
        match_id=match_id,
        plot_type=plot_type,
        plot_json=json.dumps(plot_data)
    )
    db.session.add(plot)
```

### 2. File-Based Data Sources

#### CSV Data Integration

```python
# data/etl/csv_data_loader.py
import pandas as pd
import numpy as np
from models import Match, MatchPlot, db
from datetime import datetime
import json

def load_csv_data(file_path: str, data_type: str):
    """Load data from CSV files"""
    
    try:
        df = pd.read_csv(file_path)
        print(f"Loaded {len(df)} rows from {file_path}")
        
        if data_type == 'matches':
            process_match_csv(df)
        elif data_type == 'events':
            process_events_csv(df)
        elif data_type == 'player_stats':
            process_player_stats_csv(df)
        else:
            raise ValueError(f"Unknown data type: {data_type}")
            
    except Exception as e:
        print(f"Error loading CSV data: {e}")
        raise

def process_match_csv(df: pd.DataFrame):
    """Process match data from CSV"""
    
    for _, row in df.iterrows():
        # Check if match exists
        existing = Match.query.filter_by(match_id=row['match_id']).first()
        if existing:
            continue
        
        # Create new match
        match = Match(
            match_id=row['match_id'],
            home_team=row['home_team'],
            away_team=row['away_team'],
            match_date=pd.to_datetime(row['match_date']).date(),
            home_score=row['home_score'],
            away_score=row['away_score'],
            competition_id=row.get('competition_id', 1)
        )
        
        db.session.add(match)
    
    db.session.commit()
    print(f"✓ Processed {len(df)} matches from CSV")

def process_events_csv(df: pd.DataFrame):
    """Process event data from CSV"""
    
    # Group by match
    for match_id, match_events in df.groupby('match_id'):
        
        # Generate custom analytics
        analytics = generate_csv_analytics(match_events)
        
        # Save analytics as plots
        for plot_type, plot_data in analytics.items():
            save_plot(match_id, plot_type, plot_data)
    
    db.session.commit()
    print(f"✓ Processed events for {df['match_id'].nunique()} matches")

def generate_csv_analytics(events_df: pd.DataFrame) -> Dict:
    """Generate analytics from CSV event data"""
    
    analytics = {}
    
    # Example: Pass completion rate over time
    passes = events_df[events_df['type'] == 'Pass']
    if not passes.empty:
        pass_success = passes.groupby('minute')['successful'].mean()
        
        analytics['pass_completion_timeline'] = {
            'data': [{
                'x': pass_success.index.tolist(),
                'y': pass_success.values.tolist(),
                'type': 'scatter',
                'mode': 'lines',
                'name': 'Pass Completion %'
            }],
            'layout': {
                'title': 'Pass Completion Rate Over Time',
                'xaxis': {'title': 'Minute'},
                'yaxis': {'title': 'Completion Rate'}
            }
        }
    
    # Example: Shot locations
    shots = events_df[events_df['type'] == 'Shot']
    if not shots.empty:
        analytics['shot_map'] = {
            'data': [{
                'x': shots['x'].tolist(),
                'y': shots['y'].tolist(),
                'mode': 'markers',
                'type': 'scatter',
                'marker': {
                    'size': 10,
                    'color': ['red' if outcome == 'Goal' else 'blue' 
                             for outcome in shots['outcome']]
                },
                'text': shots['outcome'].tolist()
            }],
            'layout': {
                'title': 'Shot Locations',
                'xaxis': {'title': 'X Position'},
                'yaxis': {'title': 'Y Position'}
            }
        }
    
    return analytics
```

## 📈 Creating Custom Analytics

### 1. Advanced Statistical Metrics

```python
# utils/analytics/advanced_metrics.py
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from scipy import stats
from sklearn.cluster import KMeans

def calculate_expected_threat(events_df: pd.DataFrame, xt_grid: pd.DataFrame) -> Dict:
    """Calculate Expected Threat (xT) for each action"""
    
    # Load xT grid values
    xt_values = xt_grid.set_index(['x_bin', 'y_bin'])['xt_value'].to_dict()
    
    # Calculate xT for each event
    events_df['x_bin'] = pd.cut(events_df['x'], bins=16, labels=range(16))
    events_df['y_bin'] = pd.cut(events_df['y'], bins=12, labels=range(12))
    
    events_df['xt_value'] = events_df.apply(
        lambda row: xt_values.get((row['x_bin'], row['y_bin']), 0), axis=1
    )
    
    # Aggregate by team
    team_xt = events_df.groupby('team')['xt_value'].agg(['sum', 'mean', 'count'])
    
    return {
        'team_xt_summary': team_xt.to_dict(),
        'event_xt': events_df[['minute', 'team', 'player', 'xt_value']].to_dict('records')
    }

def calculate_pressing_intensity(events_df: pd.DataFrame) -> Dict:
    """Calculate pressing intensity metrics"""
    
    # Define pressing actions
    pressing_actions = ['Pressure', 'Interception', 'Tackle', 'Block']
    pressing_events = events_df[events_df['type'].isin(pressing_actions)]
    
    # Calculate PPDA (Passes per Defensive Action)
    passes = events_df[events_df['type'] == 'Pass']
    defensive_actions = events_df[events_df['type'].isin(['Interception', 'Tackle', 'Block'])]
    
    ppda_by_team = {}
    for team in events_df['team'].unique():
        if pd.isna(team):
            continue
            
        team_passes = len(passes[passes['team'] != team])  # Opposition passes
        team_defensive_actions = len(defensive_actions[defensive_actions['team'] == team])
        
        ppda = team_passes / max(team_defensive_actions, 1)
        ppda_by_team[team] = ppda
    
    # Calculate pressing zones
    pressing_zones = calculate_pressing_zones(pressing_events)
    
    return {
        'ppda': ppda_by_team,
        'pressing_zones': pressing_zones,
        'pressing_timeline': calculate_pressing_timeline(pressing_events)
    }

def calculate_pressing_zones(pressing_events: pd.DataFrame) -> Dict:
    """Calculate where teams press most"""
    
    # Divide pitch into zones
    pressing_events['zone_x'] = pd.cut(pressing_events['x'], bins=3, labels=['Defensive', 'Middle', 'Attacking'])
    pressing_events['zone_y'] = pd.cut(pressing_events['y'], bins=3, labels=['Left', 'Center', 'Right'])
    
    zone_counts = pressing_events.groupby(['team', 'zone_x', 'zone_y']).size().reset_index(name='count')
    
    return zone_counts.to_dict('records')

def calculate_build_up_patterns(events_df: pd.DataFrame) -> Dict:
    """Analyze team build-up play patterns"""
    
    # Identify build-up sequences (passes starting from defensive third)
    passes = events_df[events_df['type'] == 'Pass'].copy()
    passes['defensive_third'] = passes['x'] < 33.33
    
    # Find sequences starting from defensive third
    build_up_sequences = []
    current_sequence = []
    
    for _, event in passes.iterrows():
        if event['defensive_third'] and not current_sequence:
            # Start new sequence
            current_sequence = [event]
        elif current_sequence and event['team'] == current_sequence[-1]['team']:
            # Continue sequence
            current_sequence.append(event)
        else:
            # End sequence
            if len(current_sequence) >= 3:  # Minimum 3 passes
                build_up_sequences.append(current_sequence)
            current_sequence = []
    
    # Analyze patterns
    patterns = analyze_sequence_patterns(build_up_sequences)
    
    return {
        'total_sequences': len(build_up_sequences),
        'avg_sequence_length': np.mean([len(seq) for seq in build_up_sequences]) if build_up_sequences else 0,
        'patterns': patterns
    }

def analyze_sequence_patterns(sequences: List[List]) -> Dict:
    """Analyze common patterns in build-up sequences"""
    
    patterns = {
        'short_passing': 0,
        'long_passing': 0,
        'wide_play': 0,
        'central_play': 0
    }
    
    for sequence in sequences:
        if len(sequence) < 2:
            continue
        
        # Calculate average pass distance
        distances = []
        y_positions = []
        
        for i in range(len(sequence) - 1):
            curr = sequence[i]
            next_pass = sequence[i + 1]
            
            distance = np.sqrt((next_pass['x'] - curr['x'])**2 + (next_pass['y'] - curr['y'])**2)
            distances.append(distance)
            y_positions.append(curr['y'])
        
        avg_distance = np.mean(distances)
        avg_y_position = np.mean(y_positions)
        
        # Classify pattern
        if avg_distance < 15:
            patterns['short_passing'] += 1
        else:
            patterns['long_passing'] += 1
        
        if avg_y_position < 25 or avg_y_position > 75:
            patterns['wide_play'] += 1
        else:
            patterns['central_play'] += 1
    
    return patterns

def calculate_player_networks(events_df: pd.DataFrame) -> Dict:
    """Calculate player interaction networks"""
    
    passes = events_df[events_df['type'] == 'Pass'].copy()
    
    # Create pass network
    networks = {}
    
    for team in passes['team'].unique():
        if pd.isna(team):
            continue
        
        team_passes = passes[passes['team'] == team]
        
        # Count passes between players
        pass_counts = team_passes.groupby(['player', 'pass_recipient']).size().reset_index(name='count')
        
        # Calculate average positions
        avg_positions = team_passes.groupby('player')[['x', 'y']].mean()
        
        networks[team] = {
            'pass_counts': pass_counts.to_dict('records'),
            'avg_positions': avg_positions.to_dict('index')
        }
    
    return networks
```

### 2. Machine Learning Analytics

```python
# utils/analytics/ml_analytics.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
import joblib

def train_shot_outcome_model(shots_df: pd.DataFrame) -> Dict:
    """Train a model to predict shot outcomes"""
    
    # Feature engineering
    features = create_shot_features(shots_df)
    
    # Prepare target variable
    y = (shots_df['outcome'] == 'Goal').astype(int)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        features, y, test_size=0.2, random_state=42
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': features.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    # Save model
    joblib.dump(model, 'models/shot_outcome_model.pkl')
    joblib.dump(scaler, 'models/shot_scaler.pkl')
    
    return {
        'accuracy': accuracy,
        'feature_importance': feature_importance.to_dict('records'),
        'classification_report': classification_report(y_test, y_pred, output_dict=True)
    }

def create_shot_features(shots_df: pd.DataFrame) -> pd.DataFrame:
    """Create features for shot outcome prediction"""
    
    features = pd.DataFrame()
    
    # Distance to goal
    features['distance_to_goal'] = np.sqrt(
        (shots_df['x'] - 100)**2 + (shots_df['y'] - 50)**2
    )
    
    # Angle to goal
    features['angle_to_goal'] = np.arctan2(
        abs(shots_df['y'] - 50), 100 - shots_df['x']
    )
    
    # Shot type
    features['shot_type_volley'] = (shots_df['shot_type'] == 'Volley').astype(int)
    features['shot_type_header'] = (shots_df['shot_type'] == 'Header').astype(int)
    
    # Body part
    features['body_part_foot'] = (shots_df['body_part'] == 'Foot').astype(int)
    features['body_part_head'] = (shots_df['body_part'] == 'Head').astype(int)
    
    # Pressure
    features['under_pressure'] = shots_df['under_pressure'].fillna(0).astype(int)
    
    # Time in match
    features['minute'] = shots_df['minute']
    features['first_half'] = (shots_df['minute'] <= 45).astype(int)
    
    return features

def predict_match_outcome(match_features: pd.DataFrame) -> Dict:
    """Predict match outcome based on in-game features"""
    
    # This would use a pre-trained model
    # For demonstration, we'll create a simple example
    
    features = [
        'possession_diff', 'shots_diff', 'shots_on_target_diff',
        'corners_diff', 'fouls_diff', 'cards_diff'
    ]
    
    # Simulate prediction (in reality, load trained model)
    home_win_prob = 0.45
    draw_prob = 0.25
    away_win_prob = 0.30
    
    return {
        'home_win_probability': home_win_prob,
        'draw_probability': draw_prob,
        'away_win_probability': away_win_prob,
        'most_likely_outcome': 'Home Win' if home_win_prob > max(draw_prob, away_win_prob) else 'Draw' if draw_prob > away_win_prob else 'Away Win'
    }

def cluster_playing_styles(team_stats_df: pd.DataFrame) -> Dict:
    """Cluster teams by playing style"""
    
    # Select relevant features
    style_features = [
        'avg_possession', 'passes_per_game', 'pass_accuracy',
        'shots_per_game', 'crosses_per_game', 'tackles_per_game',
        'interceptions_per_game', 'fouls_per_game'
    ]
    
    # Normalize features
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(team_stats_df[style_features])
    
    # Perform clustering
    kmeans = KMeans(n_clusters=4, random_state=42)
    clusters = kmeans.fit_predict(features_scaled)
    
    # Add cluster labels
    team_stats_df['playing_style_cluster'] = clusters
    
    # Analyze clusters
    cluster_analysis = {}
    for cluster_id in range(4):
        cluster_teams = team_stats_df[team_stats_df['playing_style_cluster'] == cluster_id]
        
        cluster_analysis[f'cluster_{cluster_id}'] = {
            'teams': cluster_teams['team'].tolist(),
            'characteristics': cluster_teams[style_features].mean().to_dict(),
            'style_description': describe_playing_style(cluster_teams[style_features].mean())
        }
    
    return cluster_analysis

def describe_playing_style(avg_stats: pd.Series) -> str:
    """Generate description of playing style based on stats"""
    
    descriptions = []
    
    if avg_stats['avg_possession'] > 55:
        descriptions.append("possession-based")
    elif avg_stats['avg_possession'] < 45:
        descriptions.append("counter-attacking")
    
    if avg_stats['passes_per_game'] > 500:
        descriptions.append("high passing volume")
    
    if avg_stats['crosses_per_game'] > 20:
        descriptions.append("wing-focused")
    
    if avg_stats['tackles_per_game'] > 20:
        descriptions.append("aggressive pressing")
    
    return ", ".join(descriptions) if descriptions else "balanced"
```

## 🎨 Building New Visualizations

### 1. Advanced Plot Types

```python
# utils/plots/match_plots/advanced_plots.py
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

def create_player_radar_chart(player_stats: Dict, comparison_player: Dict = None) -> Dict:
    """Create radar chart for player comparison"""
    
    categories = ['Goals', 'Assists', 'Passes', 'Tackles', 'Interceptions', 'Dribbles']
    
    fig = go.Figure()
    
    # Main player
    fig.add_trace(go.Scatterpolar(
        r=[player_stats.get(cat.lower(), 0) for cat in categories],
        theta=categories,
        fill='toself',
        name=player_stats.get('name', 'Player 1'),
        line_color='#1f77b4'
    ))
    
    # Comparison player (if provided)
    if comparison_player:
        fig.add_trace(go.Scatterpolar(
            r=[comparison_player.get(cat.lower(), 0) for cat in categories],
            theta=categories,
            fill='toself',
            name=comparison_player.get('name', 'Player 2'),
            line_color='#ff7f0e'
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max([player_stats.get(cat.lower(), 0) for cat in categories]) * 1.1]
            )
        ),
        showlegend=True,
        title="Player Performance Radar",
        template="plotly_dark"
    )
    
    return fig.to_dict()

def create_pass_network(pass_data: pd.DataFrame, avg_positions: Dict) -> Dict:
    """Create pass network visualization"""
    
    fig = go.Figure()
    
    # Add pitch outline
    fig = add_pitch_outline(fig)
    
    # Add player positions
    for player, pos in avg_positions.items():
        fig.add_trace(go.Scatter(
            x=[pos['x']],
            y=[pos['y']],
            mode='markers+text',
            marker=dict(size=20, color='blue'),
            text=player.split()[-1],  # Last name only
            textposition="middle center",
            name=player,
            showlegend=False
        ))
    
    # Add pass connections
    for _, pass_info in pass_data.iterrows():
        passer_pos = avg_positions.get(pass_info['player'])
        receiver_pos = avg_positions.get(pass_info['pass_recipient'])
        
        if passer_pos and receiver_pos and pass_info['count'] > 5:  # Only show frequent connections
            fig.add_trace(go.Scatter(
                x=[passer_pos['x'], receiver_pos['x']],
                y=[passer_pos['y'], receiver_pos['y']],
                mode='lines',
                line=dict(width=pass_info['count']/5, color='rgba(255,255,255,0.6)'),
                showlegend=False,
                hoverinfo='skip'
            ))
    
    fig.update_layout(
        title="Pass Network",
        xaxis=dict(range=[0, 100], showgrid=False, zeroline=False),
        yaxis=dict(range=[0, 100], showgrid=False, zeroline=False),
        template="plotly_dark",
        height=600
    )
    
    return fig.to_dict()

def create_expected_goals_flow(xg_data: pd.DataFrame) -> Dict:
    """Create flowing xG visualization"""
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Cumulative xG', 'xG per 5-minute period'),
        vertical_spacing=0.1
    )
    
    # Cumulative xG
    for team in xg_data['team'].unique():
        team_data = xg_data[xg_data['team'] == team].sort_values('minute')
        team_data['cumulative_xg'] = team_data['xg'].cumsum()
        
        fig.add_trace(
            go.Scatter(
                x=team_data['minute'],
                y=team_data['cumulative_xg'],
                mode='lines+markers',
                name=f'{team} (Cumulative)',
                line=dict(width=3),
                fill='tonexty' if team != xg_data['team'].unique()[0] else None
            ),
            row=1
