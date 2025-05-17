from app import app
from utils.db import db

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("✅ Tables created")
