import json
import logging
import pandas as pd
import plotly.io as pio
import warnings
from statsbombpy import sb
from flask import Flask
from app import app
from utils.db import db
from models import Match, MatchPlot
from utils.plots.match_plots.xG_per_game import generate_match_graph_plot
from utils.plots.match_plots.momentum_per_game import generate_momentum_graph_plot
from utils.analytics.match_analytics.match_analysis_utils import goal_assist_stats

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


def create_all_match_plots():
    with app.app_context():
        all_matches = Match.query.all()
        logger.info(f"Processing {len(all_matches)} matches...")

        for match in all_matches:
            try:
                logger.info(f"Processing match {match.id}...")

                events = sb.events(match.id).fillna(-999)
                match_df = pd.DataFrame(events)

                # Generate plots
                xg_plot = generate_match_graph_plot(match_df)
                momentum_plot = generate_momentum_graph_plot(match_df)
                home_df, away_df, home_team, away_team, home_norm, away_norm, home_et, away_et, home_pen, away_pen = goal_assist_stats(match_df)

                # Generate match summary JSON
                home_data = [{"player": row["player"], "contributions": list(row["contributions"])} for _, row in home_df.iterrows()]
                away_data = [{"player": row["player"], "contributions": list(row["contributions"])} for _, row in away_df.iterrows()]

                scoreline = f"{home_team} {home_norm} - {away_norm} {away_team}"
                extra_details = None
                if home_et > 0 or away_et > 0:
                    extra_details = f"(ET: {home_et} - {away_et})"
                if home_pen > 0 or away_pen > 0:
                    extra = f"(Pen: {home_pen} - {away_pen})"
                    extra_details = f"{extra_details}, {extra}" if extra_details else extra

                match_summary = {
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
                    "extraTimeDetails": extra_details
                }

                # Convert to JSON
                plots = {
                    "xg_graph": pio.to_json(xg_plot, pretty=True),
                    "momentum_graph": pio.to_json(momentum_plot, pretty=True),
                    "match_summary": json.dumps(match_summary, indent=2)
                }

                # Save each plot as its own row
                for plot_type, plot_json in plots.items():
                    db.session.merge(MatchPlot(
                        match_id=match.id,
                        plot_type=plot_type,
                        plot_json=plot_json
                    ))

                logger.info(f"✅ Saved plot data for match {match.id}")

            except Exception as e:
                logger.error(f"❌ Failed to process match {getattr(match, 'id', 'unknown')}: {e}", exc_info=False)

        db.session.commit()
        logger.info("🎉 All match plots processed and committed.")


if __name__ == "__main__":
    create_all_match_plots()
