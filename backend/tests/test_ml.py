import pytest
import os
from app.ml.content_based import ContentBasedRecommender
from app.ml.collaborative import CollaborativeFilteringRecommender
from app.ml.clustering import DestinationClustering
from app.ml.hybrid import HybridRecommender, haversine_distance_km


def test_content_based_recommender():
    recommender = ContentBasedRecommender()
    assert recommender.df is not None
    assert len(recommender.df) > 0

    # Test recommendation for nature & adventure interests
    recs = recommender.recommend_for_preferences(["Nature/Hiking", "Adventure"], top_n=5)
    assert len(recs) == 5
    assert all("content_similarity_score" in r for r in recs)
    # The top results should include nature/adventure destinations
    top_categories = [r["category"] for r in recs]
    assert any("Nature" in c or "Adventure" in c for c in top_categories)


def test_item_similarity():
    recommender = ContentBasedRecommender()
    similar = recommender.get_similar_destinations(destination_id=1, top_n=3)
    assert len(similar) == 3
    assert all("similarity_score" in s for s in similar)


def test_collaborative_filtering():
    cf = CollaborativeFilteringRecommender()
    assert cf.user_item_matrix is not None
    assert cf.predicted_df is not None

    # Test recommendation for existing user
    user_recs = cf.predict_for_user(user_id=1, top_n=5)
    assert len(user_recs) == 5
    assert all("predicted_cf_rating" in r for r in user_recs)

    # Test cold start
    cold_recs = cf.get_cold_start_recommendations(top_n=5)
    assert len(cold_recs) == 5


def test_clustering():
    clustering = DestinationClustering()
    assert clustering.kmeans is not None
    assert "cluster_id" in clustering.df.columns
    assert len(clustering.df["cluster_id"].unique()) <= 5

    # Test persona mapping
    cluster = clustering.get_cluster_for_user_persona(["Surfing", "Beaches"])
    assert cluster == 0  # Beach cluster


def test_hybrid_recommender():
    hybrid = HybridRecommender()
    recs = hybrid.recommend(
        interests=["Nature/Hiking", "Adventure"],
        budget_total_lkr=40000.0,
        duration_days=3,
        num_travelers=2,
        starting_location="Colombo",
        top_n=5
    )
    assert len(recs) == 5
    first = recs[0]
    assert "hybrid_score" in first
    assert "match_percentage" in first
    assert "distance_km" in first
    assert "explanation_tags" in first
    assert 0 <= first["hybrid_score"] <= 1.0


def test_haversine_distance():
    # Distance between Colombo and Galle is roughly 110-125km
    dist = haversine_distance_km(6.9271, 79.8612, 6.0535, 80.2210)
    assert 100 <= dist <= 130
