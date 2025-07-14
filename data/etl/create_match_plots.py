import json
import logging
import pandas as pd
import plotly.io as pio
import warnings
from statsbombpy import sb
from flask import Flask
from app import app
from utils.db import db
from models import Match, MatchPlot, Season
from utils.plots.plot_factory import MatchDataProcessor, generate_all_plots_sync
from utils.analytics.match_analytics.match_analysis_utils import generate_team_stats
from utils.plots.match_plots.unified_heatmap import generate_dominance_heatmap_json, generate_team_match_heatmap, generate_team_attack_heatmap, generate_team_defense_heatmap

# Suppress common warning spam
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=pd.errors.SettingWithCopyWarning)

# Quiet noisy libs
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("matplotlib").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.engine.Engine").setLevel(logging.WARNING)

# Set up logger for this ETL script
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("create_match_plots")

print(f"Using DB URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

def safe_plotly_json(fig):
    return pio.to_json(fig, pretty=True, engine="json", validate=False)





def create_all_match_plots():
    with app.app_context():
        matches = Match.query.all()

        logger.info(f"Processing {len(matches)} matches...")

        for match in matches:
            try:
                logger.info(f"Processing match {match.id}...")

                events = sb.events(match.id).fillna(-999)
                match_df = pd.DataFrame(events)
                
                # Create processor for efficient plot generation
                processor = MatchDataProcessor(match_df)
                
                # Generate all plots using the plot factory
                factory_plots = generate_all_plots_sync(processor)
                
                # Generate additional plots not yet in factory
                home_team_data = processor.home_team_data
                away_team_data = processor.away_team_data
                
                # Generate team stats for backward compatibility
                home_team_stats = generate_team_stats(home_team_data, processor.home_team)
                away_team_stats = generate_team_stats(away_team_data, processor.away_team)

                plot_dict = {
                    # Factory-generated plots
                    "xg_graph": json.dumps(factory_plots['xg_graph']),
                    "momentum_graph": json.dumps(factory_plots['momentum_graph']),
                    "radar_chart": json.dumps(factory_plots['radar_chart']),
                    "match_summary": json.dumps(factory_plots['match_summary'], indent=2),
                    
                    # Dominance heatmaps from factory
                    "dominance_heatmap": json.dumps(factory_plots['dominance_heatmap']),
                    "dominance_heatmap_first": json.dumps(factory_plots['dominance_heatmap_first']),
                    "dominance_heatmap_second": json.dumps(factory_plots['dominance_heatmap_second']),
                    
                    # Team heatmaps from factory
                    "home_team_possession_full": json.dumps(factory_plots['home_team_possession_full']),
                    "home_team_possession_first": json.dumps(factory_plots['home_team_possession_first']),
                    "home_team_possession_second": json.dumps(factory_plots['home_team_possession_second']),
                    "home_team_attack_full": json.dumps(factory_plots['home_team_attack_full']),
                    "home_team_attack_first": json.dumps(factory_plots['home_team_attack_first']),
                    "home_team_attack_second": json.dumps(factory_plots['home_team_attack_second']),
                    "home_team_defense_full": json.dumps(factory_plots['home_team_defense_full']),
                    "home_team_defense_first": json.dumps(factory_plots['home_team_defense_first']),
                    "home_team_defense_second": json.dumps(factory_plots['home_team_defense_second']),
                    
                    "away_team_possession_full": json.dumps(factory_plots['away_team_possession_full']),
                    "away_team_possession_first": json.dumps(factory_plots['away_team_possession_first']),
                    "away_team_possession_second": json.dumps(factory_plots['away_team_possession_second']),
                    "away_team_attack_full": json.dumps(factory_plots['away_team_attack_full']),
                    "away_team_attack_first": json.dumps(factory_plots['away_team_attack_first']),
                    "away_team_attack_second": json.dumps(factory_plots['away_team_attack_second']),
                    "away_team_defense_full": json.dumps(factory_plots['away_team_defense_full']),
                    "away_team_defense_first": json.dumps(factory_plots['away_team_defense_first']),
                    "away_team_defense_second": json.dumps(factory_plots['away_team_defense_second']),
                    
                    # Backward compatibility keys from factory
                    "home_team_heatmap": json.dumps(factory_plots['home_team_heatmap']),
                    "home_team_heatmap_first": json.dumps(factory_plots['home_team_heatmap_first']),
                    "home_team_heatmap_second": json.dumps(factory_plots['home_team_heatmap_second']),
                    "away_team_heatmap": json.dumps(factory_plots['away_team_heatmap']),
                    "away_team_heatmap_first": json.dumps(factory_plots['away_team_heatmap_first']),
                    "away_team_heatmap_second": json.dumps(factory_plots['away_team_heatmap_second']),
                    
                    # Team stats for backward compatibility
                    "home_team_stats": json.dumps(home_team_stats),
                    "away_team_stats": json.dumps(away_team_stats)
                }

                for plot_type, plot_json in plot_dict.items():
                    existing = MatchPlot.query.filter_by(match_id=match.id, plot_type=plot_type).first()
                    if existing:
                        existing.plot_json = plot_json
                        logger.debug(f"🔄 Updated plot: {match.id} [{plot_type}]")
                    else:
                        new_plot = MatchPlot(match_id=match.id, plot_type=plot_type, plot_json=plot_json)
                        db.session.add(new_plot)
                        logger.debug(f"➕ Inserted plot: {match.id} [{plot_type}]")

                # Force session flush + commit
                db.session.flush()
                db.session.commit()

                logger.info(f"✅ Saved plot data for match {match.id}")

            except Exception as e:
                logger.error(f"❌ Failed to process match {getattr(match, 'id', 'unknown')}: {e}", exc_info=True)

        db.session.commit()
        total = MatchPlot.query.count()
        logger.info(f"🎉 All match plots committed. Total rows in match_plots: {total}")



if __name__ == "__main__":
    create_all_match_plots()
