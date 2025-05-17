from statsbombpy import sb
from app import app, db
from models import Competition, Season, Match

def load_data():
    with app.app_context():
        competitions = sb.competitions()

        for _, row in competitions.iterrows():
            # Create or update Competition
            comp = Competition(id=row['competition_id'], name=row['competition_name'])
            db.session.merge(comp)

            # Check if this Season already exists with matching competition + external season_id
            existing_season = Season.query.filter_by(
                competition_id=row['competition_id'],
                season_id=row['season_id']
            ).first()

            if not existing_season:
                # Create a new Season
                season = Season(
                    season_id=row['season_id'],  # external ID
                    competition_id=row['competition_id'],
                    year=row['season_name']
                )
                db.session.add(season)
                db.session.commit()  # So it has an internal ID we can use
            else:
                season = existing_season

            # Load matches using the external StatsBomb ID
            matches = sb.matches(
                competition_id=row['competition_id'],
                season_id=row['season_id']
            )

            for _, match in matches.iterrows():
                m = Match(
                    id=match['match_id'],
                    season_id=season.id,  # use internal PK
                    home_team=match['home_team'],
                    away_team=match['away_team'],
                    scoreline=f"{match['home_score']}-{match['away_score']}"
                )
                db.session.merge(m)

        db.session.commit()
