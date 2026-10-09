"""
Collaborative Filtering Recommendation Algorithm.
Implements Matrix Factorization via TruncatedSVD and Item-Based Collaborative Filtering
on the user-destination interaction matrix.
"""

import os
import pandas as pd
import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
DEFAULT_RATINGS_PATH = os.path.join(_DATA_DIR, "user_ratings.csv")
DEFAULT_DEST_PATH = os.path.join(_DATA_DIR, "destinations.csv")


class CollaborativeFilteringRecommender:
    def __init__(
        self,
        ratings_path: str = None,
        destinations_path: str = None,
        ratings_df: pd.DataFrame = None,
        destinations_df: pd.DataFrame = None,
        n_components: int = 12
    ):
        self.ratings_path = ratings_path or DEFAULT_RATINGS_PATH
        self.destinations_path = destinations_path or DEFAULT_DEST_PATH
        self.n_components = n_components
        
        self.ratings_df = ratings_df
        self.destinations_df = destinations_df
        self.user_item_matrix = None
        self.item_user_matrix = None
        self.svd_model = None
        self.predicted_matrix = None
        self.item_similarity_matrix = None
        self.global_mean_rating = 3.5
        self.destination_mean_ratings = {}

        self._load_and_train()

    def _load_and_train(self):
        if self.ratings_df is None:
            if not os.path.exists(self.ratings_path):
                raise FileNotFoundError(f"Ratings data not found at {self.ratings_path}")
            self.ratings_df = pd.read_csv(self.ratings_path)

        if self.destinations_df is None:
            if not os.path.exists(self.destinations_path):
                raise FileNotFoundError(f"Destinations data not found at {self.destinations_path}")
            self.destinations_df = pd.read_csv(self.destinations_path)

        # Global average rating
        self.global_mean_rating = float(self.ratings_df["rating"].mean())
        
        # Per-destination mean ratings
        dest_means = self.ratings_df.groupby("destination_id")["rating"].mean()
        self.destination_mean_ratings = dest_means.to_dict()

        # Build User-Item Pivot Matrix: rows=users, columns=destinations
        all_dest_ids = sorted(self.destinations_df["id"].unique())
        self.user_item_matrix = self.ratings_df.pivot_table(
            index="user_id",
            columns="destination_id",
            values="rating",
            fill_value=0.0
        ).reindex(columns=all_dest_ids, fill_value=0.0).fillna(0.0)

        # Center non-zero ratings around mean for accurate SVD prediction
        rating_mask = (self.user_item_matrix > 0).astype(float)
        centered_matrix = self.user_item_matrix.copy()
        for col in centered_matrix.columns:
            mean_val = self.destination_mean_ratings.get(col, self.global_mean_rating)
            centered_matrix[col] = np.where(self.user_item_matrix[col] > 0, self.user_item_matrix[col] - mean_val, 0.0)

        # 1. Truncated SVD Matrix Factorization
        n_comp = min(self.n_components, len(all_dest_ids) - 1, len(self.user_item_matrix) - 1)
        self.svd_model = TruncatedSVD(n_components=n_comp, random_state=42)
        user_factors = self.svd_model.fit_transform(centered_matrix.values)
        reconstructed_residuals = np.dot(user_factors, self.svd_model.components_)
        
        # Add back destination means
        dest_means_array = np.array([self.destination_mean_ratings.get(d, self.global_mean_rating) for d in all_dest_ids])
        self.predicted_matrix = np.clip(reconstructed_residuals + dest_means_array, 1.0, 5.0)
        self.predicted_df = pd.DataFrame(
            self.predicted_matrix,
            index=self.user_item_matrix.index,
            columns=self.user_item_matrix.columns
        )

        # 2. Item-Item Cosine Similarity for unrated/in-session rating inference
        item_matrix = self.user_item_matrix.T.values
        self.item_similarity_matrix = cosine_similarity(item_matrix, item_matrix)
        self.dest_id_to_idx = {dest_id: idx for idx, dest_id in enumerate(all_dest_ids)}
        self.idx_to_dest_id = {idx: dest_id for idx, dest_id in enumerate(all_dest_ids)}

    def predict_for_user(self, user_id: int, top_n: int = 10) -> list[dict]:
        """
        Get collaborative filtering recommendations for an existing user ID.
        """
        if user_id in self.predicted_df.index:
            user_preds = self.predicted_df.loc[user_id]
            # Exclude places the user already rated
            rated_mask = self.user_item_matrix.loc[user_id] > 0
            unrated_preds = user_preds[~rated_mask]
            
            top_dest_ids = unrated_preds.sort_values(ascending=False).head(top_n).index.tolist()
            results = []
            for dest_id in top_dest_ids:
                dest_row = self.destinations_df[self.destinations_df["id"] == dest_id].iloc[0].to_dict()
                dest_row["predicted_cf_rating"] = float(round(user_preds[dest_id], 2))
                results.append(dest_row)
            return results
        else:
            return self.get_cold_start_recommendations(top_n=top_n)

    def predict_from_user_ratings(self, user_ratings_dict: dict[int, float]) -> dict[int, float]:
        """
        Given a dictionary of {destination_id: rating} provided by the current user session,
        compute Item-Based Collaborative Filtering scores for all destinations.
        Returns: {destination_id: normalized_cf_score [0, 1]}
        """
        all_dest_ids = sorted(self.destinations_df["id"].unique())
        cf_scores = {}

        if not user_ratings_dict:
            # Fallback to normalized destination average ratings
            for dest_id in all_dest_ids:
                mean_r = self.destination_mean_ratings.get(dest_id, self.global_mean_rating)
                cf_scores[dest_id] = float(np.clip(mean_r / 5.0, 0.0, 1.0))
            return cf_scores

        for dest_id in all_dest_ids:
            if dest_id in user_ratings_dict:
                # Already rated; give it a direct normalized score
                cf_scores[dest_id] = float(user_ratings_dict[dest_id] / 5.0)
                continue

            target_idx = self.dest_id_to_idx[dest_id]
            weighted_sum = 0.0
            sim_sum = 0.0

            for rated_id, rating_val in user_ratings_dict.items():
                if rated_id in self.dest_id_to_idx:
                    rated_idx = self.dest_id_to_idx[rated_id]
                    sim = self.item_similarity_matrix[target_idx, rated_idx]
                    if sim > 0:
                        weighted_sum += sim * rating_val
                        sim_sum += sim

            if sim_sum > 0:
                pred_rating = weighted_sum / sim_sum
            else:
                pred_rating = self.destination_mean_ratings.get(dest_id, self.global_mean_rating)

            cf_scores[dest_id] = float(np.clip(pred_rating / 5.0, 0.0, 1.0))

        return cf_scores

    def get_cold_start_recommendations(self, top_n: int = 10) -> list[dict]:
        """
        Cold-start handling: rank by weighted Bayesian rating (incorporates rating & popularity).
        """
        v = self.destinations_df["num_reviews"]
        r = self.destinations_df["rating"]
        c = self.destinations_df["rating"].mean()
        m = 500  # minimum reviews threshold

        # IMDB style weighted rating formula
        weighted_scores = (v / (v + m) * r) + (m / (v + m) * c)
        top_indices = weighted_scores.sort_values(ascending=False).head(top_n).index

        results = []
        for idx in top_indices:
            row = self.destinations_df.iloc[idx].to_dict()
            row["predicted_cf_rating"] = float(round(weighted_scores[idx], 2))
            results.append(row)
        return results
