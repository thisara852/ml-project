import os
import pandas as pd
from sqlalchemy.orm import Session
from app.db.database import Base, engine, SessionLocal
from app.models.models import Destination, User
from app.core.security import hash_password

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
DESTINATIONS_CSV = os.path.join(_DATA_DIR, "destinations.csv")


def seed_database():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # 1. Seed admin and test tourist if not exists
        admin = db.query(User).filter(User.email == "admin@srilankatourism.lk").first()
        if not admin:
            admin_user = User(
                email="admin@srilankatourism.lk",
                hashed_password=hash_password("Admin@123"),
                full_name="System Administrator",
                role="admin",
                preferred_interests="Beaches,Heritage/Cultural,Wildlife/Safari",
                preferred_budget_lkr=100000.0,
                starting_location="Colombo"
            )
            db.add(admin_user)

        tourist = db.query(User).filter(User.email == "traveler@srilankatourism.lk").first()
        if not tourist:
            tourist_user = User(
                email="traveler@srilankatourism.lk",
                hashed_password=hash_password("Traveler@123"),
                full_name="Kasun Perera",
                role="tourist",
                preferred_interests="Nature/Hiking,Adventure,Waterfalls",
                preferred_budget_lkr=45000.0,
                starting_location="Colombo"
            )
            db.add(tourist_user)

        # 2. Seed destinations from destinations.csv
        dest_count = db.query(Destination).count()
        if dest_count == 0 and os.path.exists(DESTINATIONS_CSV):
            df = pd.read_csv(DESTINATIONS_CSV)
            for _, row in df.iterrows():
                dest = Destination(
                    id=int(row["id"]),
                    name=str(row["name"]),
                    province=str(row["province"]),
                    district=str(row["district"]),
                    category=str(row["category"]),
                    latitude=float(row["latitude"]),
                    longitude=float(row["longitude"]),
                    description=str(row["description"]),
                    activities=str(row["activities"]),
                    avg_cost_lkr=float(row["avg_cost_lkr"]),
                    recommended_duration_hours=int(row["recommended_duration_hours"]),
                    best_season=str(row["best_season"]),
                    suitable_months=str(row["suitable_months"]),
                    family_friendly=int(row["family_friendly"]),
                    adventure_level=int(row["adventure_level"]),
                    serenity_score=int(row["serenity_score"]),
                    rating=float(row["rating"]),
                    num_reviews=int(row["num_reviews"]),
                    image_url=str(row["image_url"]),
                    is_active=True
                )
                db.add(dest)
            print(f"[Seed] Added {len(df)} Sri Lankan destinations to database.")

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[Seed Error] {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
