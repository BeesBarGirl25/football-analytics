from flask import Flask
from statsbombpy import sb
from utils.db import db
from models import MatchPlot, Match
from utils.plots.match_plots.xG_per_game import generate_match_graph_plot
from utils.plots.match_plots.momentum_per_game import generate_momentum_graph_plot
from utils.analytics.match_analytics.match_analysis_utils import goal_assist_stats
from app import app
import json
import pandas as pd
import logging



with app.app_context():
    db.init_app(app)

    matches = Match.query.all()
    for match in matches:
        try:
            print(f"Processing match {match.id}...")
            match_data = sb.events(match.id)

            # Generate and serialize plots
            xg_plot = generate_match_graph_plot(match_data)
            momentum_plot = generate_momentum_graph_plot(match_data)
            home_df, away_df, home, away, h_nt, a_nt, h_et, a_et, h_pen, a_pen = goal_assist_stats(match_data)

            summary_json = json.dumps({
                "home": home_df.to_dict(orient='records'),
                "away": away_df.to_dict(orient='records'),
                "homeTeam": home,
                "awayTeam": away,
                "homeTeamNormalTime": h_nt,
                "awayTeamNormalTime": a_nt,
                "homeTeamExtraTime": h_et,
                "awayTeamExtraTime": a_et,
                "homeTeamPenalties": h_pen,
                "awayTeamPenalties": a_pen,
                "scoreline": match.scoreline,
                "extraTimeDetails": f"ET: {h_et}-{a_et}, Pen: {h_pen}-{a_pen}" if h_et or a_et or h_pen or a_pen else None
            })

            plot_row = MatchPlot(
                match_id=match.id,
                xg_graph_json=json.dumps(xg_plot),
                momentum_graph_json=json.dumps(momentum_plot),
                match_summary_json=summary_json
            )

            db.session.merge(plot_row)

        except Exception as e:
            logging.exception(f"Failed to process match {match.id}: {e}")

    db.session.commit()
    print("✅ ETL complete")
