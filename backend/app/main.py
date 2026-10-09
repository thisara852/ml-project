from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import Base, engine
from app.db.seed import seed_database

# Import routers
from app.api.auth import router as auth_router
from app.api.destinations import router as destinations_router
from app.api.recommendations import router as recommendations_router
from app.api.trips import router as trips_router
from app.api.reviews import router as reviews_router
from app.api.weather import router as weather_router
from app.api.admin import router as admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure database schema and seed initial data
    print("[Startup] Initializing database tables and seeding data...")
    Base.metadata.create_all(bind=engine)
    seed_database()
    print("[Startup] System ready!")
    yield
    print("[Shutdown] Cleaning up...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="ML-Based Personalized Tourism Recommendation and Trip Planning System for Sri Lanka API",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(destinations_router, prefix=settings.API_V1_STR)
app.include_router(recommendations_router, prefix=settings.API_V1_STR)
app.include_router(trips_router, prefix=settings.API_V1_STR)
app.include_router(reviews_router, prefix=settings.API_V1_STR)
app.include_router(weather_router, prefix=settings.API_V1_STR)
app.include_router(admin_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {
        "message": "Welcome to Sri Lanka Tourism ML Recommendation & Trip Planning System API",
        "documentation": "/docs",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/api/auth",
            "destinations": "/api/destinations",
            "recommendations": "/api/recommendations/hybrid",
            "trips": "/api/trips",
            "weather": "/api/weather",
            "admin": "/api/admin/stats"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
