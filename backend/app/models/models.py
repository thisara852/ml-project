from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), default="tourist")  # 'tourist' or 'admin'
    preferred_interests = Column(String(255), default="Beaches,Nature/Hiking")
    preferred_budget_lkr = Column(Float, default=50000.0)
    starting_location = Column(String(50), default="Colombo")
    created_at = Column(DateTime, default=datetime.utcnow)

    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")
    trips = relationship("Trip", back_populates="user", cascade="all, delete-orphan")


class Destination(Base):
    __tablename__ = "destinations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, index=True)
    province = Column(String(50), nullable=False, index=True)
    district = Column(String(50), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    description = Column(Text, nullable=False)
    activities = Column(String(255), nullable=False)
    avg_cost_lkr = Column(Float, default=10000.0)
    recommended_duration_hours = Column(Integer, default=24)
    best_season = Column(String(100), default="December to April")
    suitable_months = Column(String(50), default="1,2,3,4,11,12")
    family_friendly = Column(Integer, default=4)
    adventure_level = Column(Integer, default=3)
    serenity_score = Column(Integer, default=4)
    rating = Column(Float, default=4.5)
    num_reviews = Column(Integer, default=100)
    image_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)

    reviews = relationship("Review", back_populates="destination", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="destination", cascade="all, delete-orphan")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    destination_id = Column(Integer, ForeignKey("destinations.id"), nullable=False)
    rating = Column(Float, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="reviews")
    destination = relationship("Destination", back_populates="reviews")


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    destination_id = Column(Integer, ForeignKey("destinations.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="favorites")
    destination = relationship("Destination", back_populates="favorites")


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(150), nullable=False)
    starting_location = Column(String(50), default="Colombo")
    duration_days = Column(Integer, default=3)
    num_travelers = Column(Integer, default=2)
    budget_lkr = Column(Float, default=50000.0)
    itinerary_data = Column(Text, nullable=False)  # JSON serialized string
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="trips")
