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

print(f"Using DB URI: {app.config['SQLALCHEMY_DATABASE_URI']}")



def create_all_match_plots():
    with app.app_context():
        matches = Match.query.all()
        logger.info(f"Processing {len(matches)} matches...")

        for match in matches:
            try:
                logger.info(f"Processing match {match.id}...")

                events = sb.events(match.id).fillna(-999)
                match_df = pd.DataFrame(events)

                xg_plot = generate_match_graph_plot(match_df)
                momentum_plot = generate_momentum_graph_plot(match_df)
                home_df, away_df, home_team, away_team, home_norm, away_norm, home_et, away_et, home_pen, away_pen = goal_assist_stats(match_df)

                # Match summary JSON
                home_data = [{"player": row["player"], "contributions": list(row["contributions"])} for _, row in home_df.iterrows()]
                away_data = [{"player": row["player"], "contributions": list(row["contributions"])} for _, row in away_df.iterrows()]

                scoreline = f"{home_team} {home_norm} - {away_norm} {away_team}"
                extra = None
                if home_et or away_et:
                    extra = f"(ET: {home_et} - {away_et})"
                if home_pen or away_pen:
                    pens = f"(Pen: {home_pen} - {away_pen})"
                    extra = f"{extra}, {pens}" if extra else pens

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
                    "extraTimeDetails": extra
                }

                # Prepare plots
                plot_dict = {
                    "xg_graph": pio.to_json(xg_plot, pretty=True),
                    "momentum_graph": pio.to_json(momentum_plot, pretty=True),
                    "match_summary": json.dumps(match_summary, indent=2)
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
