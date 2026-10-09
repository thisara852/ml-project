import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import Trip, Destination, User
from app.schemas.schemas import ItineraryRequest, TripSaveRequest, TripResponse, BudgetEstimateRequest
from app.api.auth import get_current_user
from app.services.itinerary import generate_itinerary
from app.services.budget import estimate_trip_budget

router = APIRouter(prefix="/trips", tags=["Trips & Itineraries"])


@router.post("/generate-itinerary")
def create_itinerary(req: ItineraryRequest, db: Session = Depends(get_db)):
    destinations = []
    if req.destination_ids:
        dest_records = db.query(Destination).filter(Destination.id.in_(req.destination_ids)).all()
        destinations = [
            {
                "id": d.id,
                "name": d.name,
                "province": d.province,
                "district": d.district,
                "category": d.category,
                "description": d.description,
                "activities": d.activities,
                "avg_cost_lkr": d.avg_cost_lkr,
                "image_url": d.image_url,
                "rating": d.rating
            }
            for d in dest_records
        ]
    else:
        # Pick top popular destinations
        dest_records = db.query(Destination).filter(Destination.is_active == True).order_by(Destination.rating.desc()).limit(10).all()
        destinations = [
            {
                "id": d.id,
                "name": d.name,
                "province": d.province,
                "district": d.district,
                "category": d.category,
                "description": d.description,
                "activities": d.activities,
                "avg_cost_lkr": d.avg_cost_lkr,
                "image_url": d.image_url,
                "rating": d.rating
            }
            for d in dest_records
        ]

    itinerary = generate_itinerary(
        destinations=destinations,
        duration_days=req.duration_days,
        starting_location=req.starting_location,
        interests=req.interests
    )

    # Attach budget estimation
    cost_list = [d.get("avg_cost_lkr", 10000.0) for d in destinations]
    budget_info = estimate_trip_budget(
        duration_days=req.duration_days,
        num_travelers=req.num_travelers,
        destination_avg_costs=cost_list,
        user_budget_lkr=req.budget_total_lkr
    )

    return {
        "itinerary": itinerary,
        "budget_estimation": budget_info
    }


@router.post("/estimate-budget")
def calculate_budget(req: BudgetEstimateRequest, db: Session = Depends(get_db)):
    cost_list = []
    if req.destination_ids:
        dest_records = db.query(Destination.avg_cost_lkr).filter(Destination.id.in_(req.destination_ids)).all()
        cost_list = [c[0] for c in dest_records]

    return estimate_trip_budget(
        duration_days=req.duration_days,
        num_travelers=req.num_travelers,
        destination_avg_costs=cost_list,
        travel_style=req.travel_style,
        transport_mode=req.transport_mode,
        user_budget_lkr=req.user_budget_lkr
    )


@router.post("/save", response_model=TripResponse)
def save_trip(
    trip_in: TripSaveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trip = Trip(
        user_id=current_user.id,
        title=trip_in.title,
        starting_location=trip_in.starting_location,
        duration_days=trip_in.duration_days,
        num_travelers=trip_in.num_travelers,
        budget_lkr=trip_in.budget_lkr,
        itinerary_data=json.dumps(trip_in.itinerary_data)
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)

    # Deserialize for response
    trip.itinerary_data = json.loads(trip.itinerary_data)
    return trip


@router.get("/my-trips", response_model=List[TripResponse])
def get_user_trips(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trips = db.query(Trip).filter(Trip.user_id == current_user.id).order_by(Trip.created_at.desc()).all()
    for t in trips:
        try:
            t.itinerary_data = json.loads(t.itinerary_data)
        except Exception:
            pass
    return trips


@router.delete("/{trip_id}")
def delete_trip(trip_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    db.delete(trip)
    db.commit()
    return {"message": "Trip deleted successfully"}
