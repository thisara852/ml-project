import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.seed import seed_database

client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    seed_database()


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "documentation" in response.json()


def test_destinations_list():
    response = client.get("/api/destinations/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "name" in data[0]
    assert "category" in data[0]


def test_destinations_filter_category():
    response = client.get("/api/destinations/?category=Beaches")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all("Beaches" in d["category"] for d in data)


def test_recommendations_hybrid():
    payload = {
        "interests": ["Nature/Hiking", "Adventure"],
        "budget_total_lkr": 40000.0,
        "duration_days": 3,
        "num_travelers": 2,
        "starting_location": "Colombo",
        "top_n": 5
    }
    response = client.post("/api/recommendations/hybrid", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    assert "hybrid_score" in data[0]
    assert "match_percentage" in data[0]
    assert "explanation_tags" in data[0]


def test_itinerary_generation():
    payload = {
        "duration_days": 3,
        "starting_location": "Colombo",
        "interests": ["Nature/Hiking", "Heritage/Cultural"],
        "budget_total_lkr": 60000.0
    }
    response = client.post("/api/trips/generate-itinerary", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "itinerary" in data
    assert "budget_estimation" in data
    assert len(data["itinerary"]["days"]) == 3


def test_budget_estimation():
    payload = {
        "duration_days": 4,
        "num_travelers": 2,
        "travel_style": "mid_range",
        "transport_mode": "car_with_driver",
        "user_budget_lkr": 80000.0
    }
    response = client.post("/api/trips/estimate-budget", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "breakdown" in data
    assert "total_estimated_lkr" in data
    assert data["total_estimated_lkr"] > 0


def test_admin_stats():
    response = client.get("/api/admin/stats")
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert data["summary"]["total_destinations"] > 0
