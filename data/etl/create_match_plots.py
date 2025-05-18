
import json
import logging
import pandas as pd
from statsbombpy import sb
from flask import Flask
from utils.db import db
from models import Match, MatchPlot
from utils.plots.match_plots.xG_per_game import generate_match_graph_plot
from utils.plots.match_plots.momentum_per_game import generate_momentum_graph_plot
from utils.analytics.match_analytics.match_analysis_utils import goal_assist_stats
import plotly.io as pio

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("create_match_plots")

# Flask app context (required to use SQLAlchemy)
from app import app

def create_all_match_plots():
    with app.app_context():
        all_matches = Match.query.all()
        logger.info(f"Processing {len(all_matches)} matches...")

        for match in all_matches:
            try:
                logger.info(f"Processing match {match.id}...")
                events = sb.events(match.id).fillna(-999)
                match_df = pd.DataFrame(events)

                xg_plot = generate_match_graph_plot(match_df)
                momentum_plot = generate_momentum_graph_plot(match_df)
                home_team_df, away_team_df, home_team, away_team,                 home_norm, away_norm, home_et, away_et, home_pen, away_pen = goal_assist_stats(match_df)

                # Convert match summary data into structured dict
                home_team_data = [{"player": row["player"], "contributions": list(row["contributions"])} for _, row in home_team_df.iterrows()]
                away_team_data = [{"player": row["player"], "contributions": list(row["contributions"])} for _, row in away_team_df.iterrows()]

                scoreline = f"{home_team} {home_norm} - {away_norm} {away_team}"
                extra_time_details = None
                if home_et > 0 or away_et > 0:
                    extra_time_details = f"(ET: {home_et} - {away_et})"
                if home_pen > 0 or away_pen > 0:
                    if extra_time_details:
                        extra_time_details += f", (Pen: {home_pen} - {away_pen})"
                    else:
                        extra_time_details = f"(Pen: {home_pen} - {away_pen})"

                match_summary = {
                    'home': home_team_data,
                    'away': away_team_data,
                    'homeTeam': home_team,
                    'awayTeam': away_team,
                    'homeTeamNormalTime': home_norm,
                    'awayTeamNormalTime': away_norm,
                    'homeTeamExtraTime': home_et,
                    'awayTeamExtraTime': away_et,
                    'homeTeamPenalties': home_pen,
                    'awayTeamPenalties': away_pen,
                    'scoreline': scoreline,
                    'extraTimeDetails': extra_time_details
                }

                # Serialize plots to JSON
                xg_json = pio.to_json(xg_plot, pretty=True)
                momentum_json = pio.to_json(momentum_plot, pretty=True)
                summary_json = json.dumps(match_summary, indent=2)

                # Save to DB (update or insert)
                plot_entry = MatchPlot.query.get(match.id) or MatchPlot(match_id=match.id)
                plot_entry.xg_graph_json = xg_json
                plot_entry.momentum_graph_json = momentum_json
                plot_entry.match_summary_json = summary_json

                db.session.merge(plot_entry)
                logger.info(f"✅ Saved plot data for match {match.id}")

            except Exception as e:
                logger.error(f"❌ Failed to process match {match.id}: {e}", exc_info=True)

        db.session.commit()
        logger.info("🎉 All match plots processed and committed.")

if __name__ == "__main__":
    create_all_match_plots()
