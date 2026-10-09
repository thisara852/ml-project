from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import get_db
from app.models.models import Destination, User, Review, Trip
from app.schemas.schemas import DestinationCreate, DestinationResponse, UserResponse
from app.api.auth import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin Module"])


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative privileges required"
        )
    return current_user


@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_destinations = db.query(Destination).count()
    total_users = db.query(User).count()
    total_reviews = db.query(Review).count()
    total_trips = db.query(Trip).count()

    # Category breakdown
    category_counts = db.query(
        Destination.category, func.count(Destination.id)
    ).group_by(Destination.category).all()

    # Province breakdown
    province_counts = db.query(
        Destination.province, func.count(Destination.id)
    ).group_by(Destination.province).all()

    # Top rated destinations
    top_destinations = db.query(Destination).order_by(Destination.rating.desc()).limit(5).all()

    return {
        "summary": {
            "total_destinations": total_destinations,
            "total_users": total_users,
            "total_reviews": total_reviews,
            "total_trips_created": total_trips
        },
        "categories": [{"category": c[0], "count": c[1]} for c in category_counts],
        "provinces": [{"province": p[0], "count": p[1]} for p in province_counts],
        "top_destinations": [
            {"id": d.id, "name": d.name, "rating": d.rating, "reviews": d.num_reviews}
            for d in top_destinations
        ]
    }


@router.post("/destinations", response_model=DestinationResponse)
def create_destination(
    dest_in: DestinationCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    dest = Destination(**dest_in.model_dump())
    db.add(dest)
    db.commit()
    db.refresh(dest)
    return dest


@router.put("/destinations/{dest_id}", response_model=DestinationResponse)
def update_destination(
    dest_id: int,
    dest_in: DestinationCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    dest = db.query(Destination).filter(Destination.id == dest_id).first()
    if not dest:
        raise HTTPException(status_code=404, detail="Destination not found")

    for key, value in dest_in.model_dump().items():
        setattr(dest, key, value)

    db.commit()
    db.refresh(dest)
    return dest


@router.delete("/destinations/{dest_id}")
def delete_destination(
    dest_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    dest = db.query(Destination).filter(Destination.id == dest_id).first()
    if not dest:
        raise HTTPException(status_code=404, detail="Destination not found")

    dest.is_active = False
    db.commit()
    return {"message": f"Destination '{dest.name}' deactivated successfully"}
