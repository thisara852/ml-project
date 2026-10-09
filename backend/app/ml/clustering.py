"""
K-Means Clustering Module for Tourist Persona and Destination Archetypes.
Clusters Sri Lankan destinations into distinct travel personas based on
adventure level, serenity, family friendliness, cost, duration, and categories.
"""

import os
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


CLUSTER_LABELS = {
    0: "Sun, Sand & Coastal Retreats",
    1: "Adrenaline Adventure & Mountain Treks",
    2: "Cultural Heritage, Royalty & Sacred Shrines",
    3: "Untamed Wildlife Safaris & Eco Reserves",
    4: "Misty Tea Highlands & Waterfalls"
}

PERSONA_CATEGORY_MAP = {
    "beaches": 0,
    "coastal": 0,
    "water sports": 0,
    "adventure": 1,
    "hiking": 1,
    "trekking": 1,
    "cultural": 2,
    "heritage": 2,
    "history": 2,
    "spiritual": 2,
    "wildlife": 3,
    "safari": 3,
    "animals": 3,
    "tea country": 4,
    "scenic": 4,
    "waterfalls": 4,
    "relaxation": 4
}


_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
DEFAULT_DEST_PATH = os.path.join(_DATA_DIR, "destinations.csv")


class DestinationClustering:
    def __init__(self, destinations_path: str = None, n_clusters: int = 5):
        self.destinations_path = destinations_path or DEFAULT_DEST_PATH
        self.n_clusters = n_clusters
        self.df = None
        self.kmeans = None
        self.scaler = None
        self.feature_names = []
        self._load_and_train()

    def _load_and_train(self):
        if not os.path.exists(self.destinations_path):
            raise FileNotFoundError(f"Destinations data not found at {self.destinations_path}")

        self.df = pd.read_csv(self.destinations_path)

        # Build feature matrix
        numerical_cols = [
            "family_friendly",
            "adventure_level",
            "serenity_score",
            "avg_cost_lkr",
            "recommended_duration_hours"
        ]
        
        # One-hot encode category
        category_dummies = pd.get_dummies(self.df["category"], prefix="cat")
        
        features_df = pd.concat([self.df[numerical_cols], category_dummies], axis=1)
        self.feature_names = features_df.columns.tolist()

        # Scale features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(features_df)

        # Train KMeans
        self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
        self.df["cluster_id"] = self.kmeans.fit_predict(X_scaled)
        self.df["cluster_name"] = self.df["cluster_id"].map(CLUSTER_LABELS)

    def get_cluster_for_user_persona(self, interests: list[str]) -> int:
        """
        Determine which cluster persona aligns best with the user's selected interests.
        """
        if not interests:
            return 0  # Default to beach/coastal

        votes = {i: 0 for i in range(self.n_clusters)}
        for interest in interests:
            interest_lower = interest.lower()
            for keyword, cluster_id in PERSONA_CATEGORY_MAP.items():
                if keyword in interest_lower:
                    votes[cluster_id] += 1

        best_cluster = max(votes, key=votes.get)
        return best_cluster

    def get_cluster_affinity_scores(self, user_interests: list[str]) -> dict[int, float]:
        """
        Returns a mapping of {destination_id: affinity_score [0.2 to 1.0]}
        Destinations in the user's matching cluster receive 1.0, others receive lower weight.
        """
        target_cluster = self.get_cluster_for_user_persona(user_interests)
        affinity_map = {}

        for _, row in self.df.iterrows():
            dest_id = int(row["id"])
            if row["cluster_id"] == target_cluster:
                affinity_map[dest_id] = 1.0
            else:
                affinity_map[dest_id] = 0.35  # baseline background affinity

        return affinity_map

    def get_cluster_destinations(self, cluster_id: int) -> list[dict]:
        subset = self.df[self.df["cluster_id"] == cluster_id]
        return subset.to_dict(orient="records")

    def get_all_clustered_destinations(self) -> list[dict]:
        return self.df.to_dict(orient="records")
