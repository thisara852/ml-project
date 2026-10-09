"""
Hybrid Recommendation Engine.
Fuses Content-Based similarity, Collaborative Filtering, and K-Means Persona Clustering
with physical distance, budget feasibility, and seasonal weather suitability.
"""

import math
from datetime import datetime
import pandas as pd
import numpy as np

from .content_based import ContentBasedRecommender
from .collaborative import CollaborativeFilteringRecommender
from .clustering import DestinationClustering


# Prominent Sri Lankan transit starting hubs
SRI_LANKA_HUBS = {
    "colombo": (6.9271, 79.8612),
    "katunayake": (7.1803, 79.8841),  # Bandaranaike International Airport
    "kandy": (7.2906, 80.6337),
    "galle": (6.0535, 80.2210),
    "jaffna": (9.6615, 80.0255),
    "ella": (6.8728, 81.0466),
    "trincomalee": (8.5874, 81.2152)
}


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance between two points in km."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 1)


class HybridRecommender:
    def __init__(
        self,
        content_recommender: ContentBasedRecommender = None,
        cf_recommender: CollaborativeFilteringRecommender = None,
        clustering: DestinationClustering = None
    ):
        self.cb = content_recommender or ContentBasedRecommender()
        self.cf = cf_recommender or CollaborativeFilteringRecommender()
        self.km = clustering or DestinationClustering()
        self.destinations_df = self.cb.df

    def recommend(
        self,
        interests: list[str],
        budget_total_lkr: float = 50000.0,
        duration_days: int = 3,
        num_travelers: int = 2,
        starting_location: str = "Colombo",
        user_ratings: dict[int, float] | None = None,
        travel_month: int | None = None,
        weights: dict[str, float] | None = None,
        top_n: int = 10
    ) -> list[dict]:
        """
        Produce personalized hybrid destination recommendations.
        """
        if weights is None:
            # Default ensemble weights: Content (45%), Collab (35%), Persona Cluster (20%)
            weights = {"content": 0.45, "collab": 0.35, "cluster": 0.20}

        # Current or specified month (1-12)
        target_month = travel_month if travel_month else datetime.now().month

        # Calculate daily budget allowance per traveler
        travelers = max(1, num_travelers)
        days = max(1, duration_days)
        daily_budget_per_person = budget_total_lkr / (travelers * days)

        # 1. Content-based scores
        cb_scores = self.cb.get_all_destination_scores(interests)

        # 2. Collaborative filtering scores
        cf_scores = self.cf.predict_from_user_ratings(user_ratings or {})

        # 3. K-Means Persona cluster affinity
        cluster_scores = self.km.get_cluster_affinity_scores(interests)
        user_cluster_id = self.km.get_cluster_for_user_persona(interests)

        # Determine starting coordinates
        hub_key = starting_location.strip().lower()
        start_coords = SRI_LANKA_HUBS.get(hub_key, SRI_LANKA_HUBS["colombo"])

        ranked_results = []
        for _, row in self.destinations_df.iterrows():
            dest_id = int(row["id"])
            dest_lat = float(row["latitude"])
            dest_lon = float(row["longitude"])
            dest_avg_cost = float(row["avg_cost_lkr"])

            # Compute geographical distance from starting point
            distance_km = haversine_distance_km(
                start_coords[0], start_coords[1], dest_lat, dest_lon
            )

            # Component scores [0.0 - 1.0]
            s_cb = cb_scores.get(dest_id, 0.5)
            s_cf = cf_scores.get(dest_id, 0.5)
            s_km = cluster_scores.get(dest_id, 0.5)

            raw_ensemble = (
                weights["content"] * s_cb +
                weights["collab"] * s_cf +
                weights["cluster"] * s_km
            )

            # Budget factor:
            # If within budget: 0 penalty. If exceeds daily budget: scale down gently.
            if dest_avg_cost <= daily_budget_per_person:
                budget_multiplier = 1.0
                budget_status = "Within Budget"
            elif dest_avg_cost <= daily_budget_per_person * 1.35:
                budget_multiplier = 0.88
                budget_status = "Slightly Above Target"
            else:
                budget_multiplier = 0.70
                budget_status = "High Budget Tier"

            # Distance factor:
            # For shorter trips (e.g. 1-2 days), long distances (>250km) are penalized.
            # For 3+ days, Sri Lanka is easily traversable.
            if days <= 2 and distance_km > 220:
                distance_penalty = 0.12
            else:
                distance_penalty = 0.0

            # Seasonal & Weather suitability bonus:
            # Check if current/target month is in destination's suitable_months
            suitable_months_str = str(row.get("suitable_months", ""))
            suitable_months = [int(m.strip()) for m in suitable_months_str.split(",") if m.strip().isdigit()]
            is_best_season = target_month in suitable_months
            season_bonus = 0.08 if is_best_season else -0.04

            # Compute final hybrid score clamped to [0.0, 1.0]
            final_score = (raw_ensemble * budget_multiplier) - distance_penalty + season_bonus
            final_score = float(np.clip(final_score, 0.05, 0.99))
            match_percentage = int(round(final_score * 100))

            # Generate explainability tags
            explanation_tags = []
            if s_cb >= 0.65:
                explanation_tags.append(f"Strong match for your interests ({row['category']})")
            if s_cf >= 0.70:
                explanation_tags.append("Highly rated by travelers with similar tastes")
            if row.get("cluster_id") == user_cluster_id:
                explanation_tags.append("Aligns with your travel persona archetype")
            if is_best_season:
                explanation_tags.append(f"Ideal visiting weather for {datetime(2026, target_month, 1).strftime('%B')}")
            if budget_status == "Within Budget":
                explanation_tags.append(f"Fits within Rs. {int(daily_budget_per_person):,}/day budget")

            dest_dict = row.to_dict()
            dest_dict.update({
                "hybrid_score": round(final_score, 4),
                "match_percentage": match_percentage,
                "content_score": round(s_cb, 3),
                "collaborative_score": round(s_cf, 3),
                "cluster_affinity_score": round(s_km, 3),
                "distance_km": distance_km,
                "starting_hub": starting_location,
                "budget_status": budget_status,
                "is_best_season": is_best_season,
                "explanation_tags": explanation_tags[:3]
            })

            ranked_results.append(dest_dict)

        # Sort descending by hybrid_score
        ranked_results.sort(key=lambda x: x["hybrid_score"], reverse=True)
        return ranked_results[:top_n]
