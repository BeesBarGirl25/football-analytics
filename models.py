from utils.db import db

class Competition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

class Season(db.Model):
    id = db.Column(db.String, primary_key=True)  # Unique composite key like "9-42"
    season_id = db.Column(db.Integer, nullable=False)  # StatsBomb season ID
    competition_id = db.Column(db.Integer, db.ForeignKey('competition.id'), nullable=False)
    year = db.Column(db.String(10))

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    season_id = db.Column(db.String, db.ForeignKey('season.id'), nullable=False)  # Match the new Season ID format
    home_team = db.Column(db.String(100))
    away_team = db.Column(db.String(100))
    scoreline = db.Column(db.String(20))
