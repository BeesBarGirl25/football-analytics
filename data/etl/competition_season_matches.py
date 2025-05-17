from app import app, db
from models import Competition, Season, Match
from statsbombpy import sb

def load_data():
    with app.app_context():
        competitions = sb.competitions()
        for _, row in competitions.iterrows():
            comp = Competition(id=row['competition_id'], name=row['competition_name'])
            db.session.merge(comp)

            season_id = f"{row['competition_id']}-{row['season_id']}"
            season = Season(
                id=season_id,
                season_id=row['season_id'],
                competition_id=row['competition_id'],
                year=row['season_name']
            )
            db.session.merge(season)

            matches = sb.matches(competition_id=row['competition_id'], season_id=row['season_id'])
            for _, match in matches.iterrows():
                m = Match(
                    id=match['match_id'],
                    season_id=season_id,
                    home_team=match['home_team'],
                    away_team=match['away_team'],
                    scoreline=f"{match['home_score']}-{match['away_score']}"
                )
                db.session.merge(m)

        db.session.commit()

if __name__ == "__main__":
    load_data()
