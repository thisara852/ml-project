from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import Destination
from app.services.weather import get_live_weather

router = APIRouter(prefix="/weather", tags=["Weather"])


@router.get("/destination/{destination_id}")
async def get_weather_for_destination(destination_id: int, db: Session = Depends(get_db)):
    dest = db.query(Destination).filter(Destination.id == destination_id).first()
    if not dest:
        raise HTTPException(status_code=404, detail="Destination not found")

    weather_data = await get_live_weather(dest.latitude, dest.longitude)
    weather_data["destination_name"] = dest.name
    weather_data["district"] = dest.district
    weather_data["province"] = dest.province
    return weather_data


@router.get("/coordinates")
async def get_weather_by_coords(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude")
):
    return await get_live_weather(lat, lon)
