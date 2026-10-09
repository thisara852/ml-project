from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.database import get_db
from app.models.models import Destination
from app.schemas.schemas import DestinationResponse

router = APIRouter(prefix="/destinations", tags=["Destinations"])


@router.get("/", response_model=List[DestinationResponse])
def get_destinations(
    category: Optional[str] = Query(None, description="Filter by category e.g. Beaches, Nature/Hiking"),
    province: Optional[str] = Query(None, description="Filter by province e.g. Southern, Central, Uva"),
    district: Optional[str] = Query(None, description="Filter by district e.g. Matale, Galle"),
    min_rating: Optional[float] = Query(None, ge=1.0, le=5.0),
    search: Optional[str] = Query(None, description="Keyword search in name, description, or activities"),
    db: Session = Depends(get_db)
):
    query = db.query(Destination).filter(Destination.is_active == True)

    if category:
        query = query.filter(Destination.category.ilike(f"%{category}%"))
    if province:
        query = query.filter(Destination.province.ilike(f"%{province}%"))
    if district:
        query = query.filter(Destination.district.ilike(f"%{district}%"))
    if min_rating is not None:
        query = query.filter(Destination.rating >= min_rating)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Destination.name.ilike(search_pattern),
                Destination.description.ilike(search_pattern),
                Destination.activities.ilike(search_pattern),
                Destination.province.ilike(search_pattern)
            )
        )

    return query.order_by(Destination.rating.desc()).all()


@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Destination.category).distinct().all()
    provinces = db.query(Destination.province).distinct().all()
    districts = db.query(Destination.district).distinct().all()
    return {
        "categories": sorted([c[0] for c in categories if c[0]]),
        "provinces": sorted([p[0] for p in provinces if p[0]]),
        "districts": sorted([d[0] for d in districts if d[0]])
    }


@router.get("/{destination_id}", response_model=DestinationResponse)
def get_destination_by_id(destination_id: int, db: Session = Depends(get_db)):
    dest = db.query(Destination).filter(Destination.id == destination_id).first()
    if not dest:
        raise HTTPException(status_code=404, detail="Destination not found")
    return dest
