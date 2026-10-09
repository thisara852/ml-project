from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict


# Auth & User Schemas
class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str
    preferred_interests: Optional[str] = "Beaches,Nature/Hiking"
    preferred_budget_lkr: Optional[float] = 50000.0
    starting_location: Optional[str] = "Colombo"


class UserLogin(BaseModel):
    email: str
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    preferred_interests: Optional[str] = None
    preferred_budget_lkr: Optional[float] = None
    starting_location: Optional[str] = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    role: str
    preferred_interests: Optional[str]
    preferred_budget_lkr: Optional[float]
    starting_location: Optional[str]
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# Destination Schemas
class DestinationBase(BaseModel):
    name: str
    province: str
    district: str
    category: str
    latitude: float
    longitude: float
    description: str
    activities: str
    avg_cost_lkr: float
    recommended_duration_hours: int
    best_season: str
    suitable_months: str
    family_friendly: int
    adventure_level: int
    serenity_score: int
    image_url: Optional[str] = None


class DestinationCreate(DestinationBase):
    pass


class DestinationResponse(DestinationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rating: float
    num_reviews: int
    is_active: bool


# Recommendation Request & Response
class RecommendationRequest(BaseModel):
    interests: List[str] = ["Nature/Hiking", "Adventure"]
    budget_total_lkr: float = 40000.0
    duration_days: int = 3
    num_travelers: int = 2
    starting_location: str = "Colombo"
    user_ratings: Optional[Dict[int, float]] = None
    travel_month: Optional[int] = None
    top_n: int = 10


class RecommendedDestinationResponse(DestinationBase):
    id: int
    rating: float
    num_reviews: int
    hybrid_score: float
    match_percentage: int
    content_score: float
    collaborative_score: float
    cluster_affinity_score: float
    distance_km: float
    starting_hub: str
    budget_status: str
    is_best_season: bool
    explanation_tags: List[str]


# Trip Planning Schemas
class ItineraryRequest(BaseModel):
    destination_ids: Optional[List[int]] = None
    duration_days: int = 3
    starting_location: str = "Colombo"
    interests: Optional[List[str]] = None
    budget_total_lkr: float = 50000.0
    num_travelers: int = 2


class TripSaveRequest(BaseModel):
    title: str
    starting_location: str = "Colombo"
    duration_days: int = 3
    num_travelers: int = 2
    budget_lkr: float = 50000.0
    itinerary_data: Dict[str, Any]


class TripResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    starting_location: str
    duration_days: int
    num_travelers: int
    budget_lkr: float
    itinerary_data: Any
    created_at: datetime


# Review Schemas
class ReviewCreate(BaseModel):
    destination_id: int
    rating: float
    comment: Optional[str] = None


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    destination_id: int
    rating: float
    comment: Optional[str]
    created_at: datetime
    user_name: Optional[str] = None


# Budget Estimate Request
class BudgetEstimateRequest(BaseModel):
    duration_days: int = 3
    num_travelers: int = 2
    destination_ids: Optional[List[int]] = None
    travel_style: str = "mid_range"
    transport_mode: str = "car_with_driver"
    user_budget_lkr: float = 50000.0
