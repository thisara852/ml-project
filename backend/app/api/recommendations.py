from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.schemas import RecommendationRequest, RecommendedDestinationResponse
from app.ml.content_based import ContentBasedRecommender
from app.ml.collaborative import CollaborativeFilteringRecommender
from app.ml.clustering import DestinationClustering
from app.ml.hybrid import HybridRecommender
from app.ml.evaluate import evaluate_models

router = APIRouter(prefix="/recommendations", tags=["ML Recommendations"])

# Singleton ML engine instances for fast inference
_cb = None
_cf = None
_km = None
_hybrid = None


def get_hybrid_engine() -> HybridRecommender:
    global _cb, _cf, _km, _hybrid
    if _hybrid is None:
        _cb = ContentBasedRecommender()
        _cf = CollaborativeFilteringRecommender()
        _km = DestinationClustering()
        _hybrid = HybridRecommender(_cb, _cf, _km)
    return _hybrid


@router.post("/hybrid", response_model=List[RecommendedDestinationResponse])
def get_hybrid_recommendations(req: RecommendationRequest):
    engine = get_hybrid_engine()
    results = engine.recommend(
        interests=req.interests,
        budget_total_lkr=req.budget_total_lkr,
        duration_days=req.duration_days,
        num_travelers=req.num_travelers,
        starting_location=req.starting_location,
        user_ratings=req.user_ratings,
        travel_month=req.travel_month,
        top_n=req.top_n
    )
    return results


@router.get("/content-based")
def get_content_based(interests: str = Query("Nature,Adventure"), top_n: int = 10):
    engine = get_hybrid_engine()
    interests_list = [i.strip() for i in interests.split(",") if i.strip()]
    return engine.cb.recommend_for_preferences(interests_list, top_n=top_n)


@router.get("/collaborative")
def get_collaborative(user_id: Optional[int] = Query(1), top_n: int = 10):
    engine = get_hybrid_engine()
    return engine.cf.predict_for_user(user_id, top_n=top_n)


@router.get("/clustering")
def get_clusters():
    engine = get_hybrid_engine()
    return engine.km.get_all_clustered_destinations()


@router.get("/evaluation-metrics")
def get_evaluation_metrics(k: int = Query(5, ge=3, le=10)):
    """
    Returns offline Precision@K, Recall@K, F1@K, MAE, and RMSE comparison table.
    """
    return evaluate_models(k=k)
