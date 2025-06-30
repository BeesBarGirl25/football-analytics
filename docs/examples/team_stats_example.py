# Add this function to utils/analytics/match_analytics/match_analysis_utils.py

def generate_team_stats(match_data: pd.DataFrame, team_name: str) -> dict:
    """
    Generate comprehensive stats for a single team using full match data for context
    
    Args:
        match_data: Full match DataFrame (both teams)
        team_name: Name of the team to generate stats for
    
    Returns:
        Dict with team stats in format ready for frontend consumption
    """
    
    # Get team-specific data
    team_data = match_data[match_data['team'] == team_name]
    opponent_data = match_data[match_data['team'] != team_name]
    
    # Calculate stats that need full match context
    total_passes = len(match_data[match_data['type'] == 'Pass'])
    team_passes = len(team_data[team_data['type'] == 'Pass'])
    possession_pct = round((team_passes / total_passes * 100), 1) if total_passes > 0 else 0
    
    # Calculate team-specific stats
    shots = len(team_data[team_data['type'] == 'Shot'])
    shots_on_target = len(team_data[
        (team_data['type'] == 'Shot') & 
        (team_data['shot_outcome'].isin(['Goal', 'Saved']))
    ])
    
    successful_passes = len(team_data[
        (team_data['type'] == 'Pass') & 
        (team_data['pass_outcome'].isna())  # Successful passes have no outcome
    ])
    pass_accuracy = round((successful_passes / team_passes * 100), 1) if team_passes > 0 else 0
    
    # Add more stats as needed
    corners = len(team_data[team_data['type'] == 'Corner'])
    fouls = len(team_data[team_data['type'] == 'Foul Committed'])
    
    return {
        "team_stats": {
            "team_name": team_name,
            "stats": [
                {"stat_name": "Possession", "value": f"{possession_pct}%"},
                {"stat_name": "Shots", "value": str(shots)},
                {"stat_name": "Shots on Target", "value": str(shots_on_target)},
                {"stat_name": "Passes", "value": str(team_passes)},
                {"stat_name": "Pass Accuracy", "value": f"{pass_accuracy}%"},
                {"stat_name": "Corners", "value": str(corners)},
                {"stat_name": "Fouls", "value": str(fouls)}
            ]
        }
    }
