"""
Plot Factory for efficient plot generation with shared data preprocessing
"""
import pandas as pd
import asyncio
import concurrent.futures
from typing import Dict, Any, Tuple
from utils.plots.match_plots.xG_per_game import generate_match_graph_plot
from utils.plots.match_plots.momentum_per_game import generate_momentum_graph_plot
from utils.plots.match_plots.unified_heatmap import generate_heatmap
from utils.analytics.match_analytics.match_analysis_utils import goal_assist_stats


class MatchDataProcessor:
    """Preprocesses match data once for use across multiple plot types"""
    
    def __init__(self, match_df: pd.DataFrame):
        self.match_df = match_df
        self.teams = match_df['team'].unique()
        if len(self.teams) >= 2:
            self.home_team, self.away_team = self.teams[0], self.teams[1]
        else:
            self.home_team = self.away_team = self.teams[0] if len(self.teams) > 0 else "Unknown"
        
        # Pre-filter team data
        self.home_team_data = match_df[match_df['team'] == self.home_team]
        self.away_team_data = match_df[match_df['team'] == self.away_team]
        
        # Pre-compute goal/assist stats once
        self._goal_assist_data = None
    
    @property
    def goal_assist_data(self):
        """Lazy load goal/assist stats"""
        if self._goal_assist_data is None:
            self._goal_assist_data = goal_assist_stats(
                self.match_df, self.home_team, self.away_team
            )
        return self._goal_assist_data


class PlotFactory:
    """Factory for generating plots efficiently with shared preprocessing"""
    
    @staticmethod
    def generate_xg_plot(processor: MatchDataProcessor) -> Dict[str, Any]:
        """Generate xG plot"""
        return generate_match_graph_plot(
            processor.match_df, processor.home_team, processor.away_team
        )
    
    @staticmethod
    def generate_momentum_plot(processor: MatchDataProcessor) -> Dict[str, Any]:
        """Generate momentum plot"""
        return generate_momentum_graph_plot(
            processor.match_df, processor.home_team, processor.away_team
        )
    
    @staticmethod
    def generate_dominance_heatmaps(processor: MatchDataProcessor) -> Dict[str, Any]:
        """Generate all dominance heatmaps (full, first, second)"""
        return {
            'dominance_heatmap': generate_heatmap(processor.match_df, 'dominance', 'full'),
            'dominance_heatmap_first': generate_heatmap(processor.match_df, 'dominance', 'first'),
            'dominance_heatmap_second': generate_heatmap(processor.match_df, 'dominance', 'second')
        }
    
    @staticmethod
    def generate_team_heatmaps(processor: MatchDataProcessor) -> Dict[str, Any]:
        """Generate all team heatmap combinations (phase × half)"""
        phases = ['possession', 'attack', 'defense']
        halves = ['full', 'first', 'second']
        
        heatmaps = {}
        for team_prefix in ['home_team', 'away_team']:
            team_data = processor.home_team_data if team_prefix == 'home_team' else processor.away_team_data
            
            for phase in phases:
                for half in halves:
                    key = f"{team_prefix}_{phase}_{half}"
                    heatmaps[key] = generate_heatmap(team_data, phase, half)
        
        # Keep backward compatibility keys
        heatmaps.update({
            'home_team_heatmap': heatmaps['home_team_possession_full'],
            'home_team_heatmap_first': heatmaps['home_team_possession_first'],
            'home_team_heatmap_second': heatmaps['home_team_possession_second'],
            'away_team_heatmap': heatmaps['away_team_possession_full'],
            'away_team_heatmap_first': heatmaps['away_team_possession_first'],
            'away_team_heatmap_second': heatmaps['away_team_possession_second']
        })
        
        return heatmaps
    
    @staticmethod
    def generate_match_summary(processor: MatchDataProcessor) -> Dict[str, Any]:
        """Generate match summary data"""
        (home_df, away_df, home_team, away_team, 
         home_norm, away_norm, home_et, away_et, home_pen, away_pen) = processor.goal_assist_data
        
        home_data = [{"player": row["player"], "contributions": list(row["contributions"])} 
                    for _, row in home_df.iterrows()]
        away_data = [{"player": row["player"], "contributions": list(row["contributions"])} 
                    for _, row in away_df.iterrows()]
        
        scoreline = f"{home_team} {home_norm} - {away_norm} {away_team}"
        extra = None
        if home_et or away_et:
            extra = f"(ET: {home_et} - {away_et})"
        if home_pen or away_pen:
            pens = f"(Pen: {home_pen} - {away_pen})"
            extra = f"{extra}, {pens}" if extra else pens
        
        return {
            "home": home_data,
            "away": away_data,
            "homeTeam": home_team,
            "awayTeam": away_team,
            "homeTeamNormalTime": home_norm,
            "awayTeamNormalTime": away_norm,
            "homeTeamExtraTime": home_et,
            "awayTeamExtraTime": away_et,
            "homeTeamPenalties": home_pen,
            "awayTeamPenalties": away_pen,
            "scoreline": scoreline,
            "extraTimeDetails": extra
        }


async def generate_all_plots_async(processor: MatchDataProcessor) -> Dict[str, Any]:
    """Generate all plots concurrently"""
    loop = asyncio.get_event_loop()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        # Submit all plot generation tasks
        tasks = {
            'xg_plot': loop.run_in_executor(executor, PlotFactory.generate_xg_plot, processor),
            'momentum_plot': loop.run_in_executor(executor, PlotFactory.generate_momentum_plot, processor),
            'dominance_plots': loop.run_in_executor(executor, PlotFactory.generate_dominance_heatmaps, processor),
            'team_plots': loop.run_in_executor(executor, PlotFactory.generate_team_heatmaps, processor),
            'match_summary': loop.run_in_executor(executor, PlotFactory.generate_match_summary, processor)
        }
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        # Combine results
        xg_plot, momentum_plot, dominance_plots, team_plots, match_summary = results
        
        # Handle any exceptions
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                raise result
        
        # Flatten the results
        all_plots = {
            'xg_graph': xg_plot,
            'momentum_graph': momentum_plot,
            'match_summary': match_summary
        }
        all_plots.update(dominance_plots)
        all_plots.update(team_plots)
        
        return all_plots


def generate_all_plots_sync(processor: MatchDataProcessor) -> Dict[str, Any]:
    """Synchronous version for compatibility"""
    return {
        'xg_graph': PlotFactory.generate_xg_plot(processor),
        'momentum_graph': PlotFactory.generate_momentum_plot(processor),
        'match_summary': PlotFactory.generate_match_summary(processor),
        **PlotFactory.generate_dominance_heatmaps(processor),
        **PlotFactory.generate_team_heatmaps(processor)
    }
