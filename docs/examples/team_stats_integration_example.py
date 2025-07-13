# Add this to utils/analytics/match_analytics/match_analysis_utils.py

def generate_team_stats_table(match_data: pd.DataFrame, team_name: str) -> dict:
    """
    Generate stats table for a single team using your existing calculate_team_stats function
    
    Args:
        match_data: Full match DataFrame (both teams)
        team_name: Name of the team to generate stats for
    
    Returns:
        Dict with team stats in format ready for frontend consumption
    """
    
    # Use your existing function to calculate all team stats
    team_stats_df = calculate_team_stats(match_data)
    
    # Extract stats for the specific team
    if team_name not in team_stats_df.index:
        # Return empty stats if team not found
        return {
            "team_stats": {
                "team_name": team_name,
                "stats": []
            }
        }
    
    team_row = team_stats_df.loc[team_name]
    
    # Convert to frontend-friendly format with success rates where applicable
    
    # Calculate success rates
    shots_on_target_rate = (team_row['shots_on_target'] / team_row['shots'] * 100) if team_row['shots'] > 0 else 0
    goal_conversion_rate = (team_row['goals'] / team_row['shots'] * 100) if team_row['shots'] > 0 else 0
    
    stats_list = [
        {"stat_name": "Shots", "value": str(int(team_row['shots']))},
        {"stat_name": "Goals", "value": f"{int(team_row['goals'])}/{int(team_row['shots'])} ({goal_conversion_rate:.1f}%)" if team_row['shots'] > 0 else "0/0 (0.0%)"},
        {"stat_name": "xG", "value": f"{team_row['xG']:.2f}"},
        {"stat_name": "Shots on Target", "value": f"{int(team_row['shots_on_target'])}/{int(team_row['shots'])} ({shots_on_target_rate:.1f}%)" if team_row['shots'] > 0 else "0/0 (0.0%)"},
        {"stat_name": "Passes", "value": f"{int(team_row['successful_passes'])}/{int(team_row['total_passes'])} ({team_row['pass_accuracy_%']:.1f}%)" if team_row['total_passes'] > 0 else "0/0 (0.0%)"},
        {"stat_name": "Key Passes", "value": str(int(team_row['key_passes']))},
        {"stat_name": "Assists", "value": str(int(team_row['goal_assists']))},
        {"stat_name": "Fouls Committed", "value": str(int(team_row['fouls_committed']))},
        {"stat_name": "Fouls Won", "value": str(int(team_row['fouls_won']))},
        {"stat_name": "Yellow Cards", "value": str(int(team_row['yellow_cards']))},
        {"stat_name": "Red Cards", "value": str(int(team_row['red_cards']))},
        {"stat_name": "Interceptions", "value": str(int(team_row['interceptions']))},
        {"stat_name": "Clearances", "value": str(int(team_row['clearances']))},
        {"stat_name": "Under Pressure", "value": str(int(team_row['under_pressure_events']))}
    ]
    
    return {
        "team_stats": {
            "team_name": team_name,
            "stats": stats_list
        }
    }


# Add this to utils/plots/plot_factory.py in the PlotFactory class

@staticmethod
def generate_team_stats_tables(processor: MatchDataProcessor) -> Dict[str, Any]:
    """Generate stats tables for both teams using existing calculate_team_stats function"""
    return {
        'home_team_stats': generate_team_stats_table(processor.match_df, processor.home_team),
        'away_team_stats': generate_team_stats_table(processor.match_df, processor.away_team)
    }


# Update generate_all_plots_sync() in plot_factory.py to include:

def generate_all_plots_sync(processor: MatchDataProcessor) -> Dict[str, Any]:
    """Synchronous version for compatibility"""
    return {
        'xg_graph': PlotFactory.generate_xg_plot(processor),
        'momentum_graph': PlotFactory.generate_momentum_plot(processor),
        'match_summary': PlotFactory.generate_match_summary(processor),
        **PlotFactory.generate_dominance_heatmaps(processor),
        **PlotFactory.generate_team_heatmaps(processor),
        **PlotFactory.generate_team_stats_tables(processor)  # Add this line
    }
