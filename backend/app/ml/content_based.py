"""
Content-Based Filtering Recommendation Algorithm.
Uses TF-IDF Vectorization and Cosine Similarity to match user preferences
with destination features (category, activities, province, tags, description).
"""

import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DEFAULT_DEST_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "destinations.csv")


class ContentBasedRecommender:
    def __init__(self, data_path: str = None):
        self.data_path = data_path or DEFAULT_DEST_PATH
        self.df = None
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.cosine_sim_matrix = None
        self._load_and_train()

    def _load_and_train(self):
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Destination dataset not found at {self.data_path}")

        self.df = pd.read_csv(self.data_path)
        
        # Build comprehensive feature text representation for each destination
        # Repeating key categories and activities to give them higher semantic weight
        def create_feature_soup(row):
            return (
                f"{row['category']} {row['category']} "
                f"{row['activities']} {row['activities']} "
                f"{row['province']} {row['district']} "
                f"{row['best_season']} "
                f"{row['description']}"
            )

        self.df["feature_soup"] = self.df.apply(create_feature_soup, axis=1)

        # TF-IDF Vectorizer with unigrams and bigrams
        self.tfidf_vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            min_df=1
        )
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.df["feature_soup"])
        
        # Precompute destination-to-destination cosine similarity
        self.cosine_sim_matrix = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)

    def recommend_for_preferences(self, user_interests: list[str], top_n: int = 10) -> list[dict]:
        """
        Recommend destinations given a list of user interests/keywords.
        E.g., ['Nature/Hiking', 'Adventure', 'Waterfalls', 'Photography']
        """
        if not user_interests:
            query_str = "Beaches Nature Heritage Wildlife Adventure"
        else:
            query_str = " ".join(user_interests)

        # Transform user query using the fitted TF-IDF
        query_vec = self.tfidf_vectorizer.transform([query_str])
        
        # Calculate cosine similarity with all destinations
        sim_scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        
        # Normalize scores to range [0.0, 1.0]
        max_s = sim_scores.max() if sim_scores.max() > 0 else 1.0
        norm_scores = sim_scores / max_s

        ranked_indices = np.argsort(norm_scores)[::-1][:top_n]
        
        results = []
        for idx in ranked_indices:
            row = self.df.iloc[idx].to_dict()
            row["content_similarity_score"] = float(round(norm_scores[idx], 4))
            results.append(row)

        return results

    def get_similar_destinations(self, destination_id: int, top_n: int = 5) -> list[dict]:
        """
        Item-to-Item content recommendation.
        Returns top N destinations most similar to the given destination ID.
        """
        idx_matches = self.df.index[self.df["id"] == destination_id].tolist()
        if not idx_matches:
            return []
        
        dest_idx = idx_matches[0]
        sim_scores = self.cosine_sim_matrix[dest_idx]
        
        # Sort indices descending, excluding the destination itself
        sorted_indices = np.argsort(sim_scores)[::-1]
        sorted_indices = [i for i in sorted_indices if i != dest_idx][:top_n]

        results = []
        for idx in sorted_indices:
            row = self.df.iloc[idx].to_dict()
            row["similarity_score"] = float(round(sim_scores[idx], 4))
            results.append(row)

        return results

    def get_all_destination_scores(self, user_interests: list[str]) -> dict[int, float]:
        """
        Returns a dictionary mapping destination_id -> normalized content score [0, 1].
        Used by the Hybrid engine.
        """
        if not user_interests:
            query_str = "Sri Lanka Tourism Nature Beach Heritage Wildlife"
        else:
            query_str = " ".join(user_interests)

        query_vec = self.tfidf_vectorizer.transform([query_str])
        sim_scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        
        max_s = sim_scores.max() if sim_scores.max() > 0 else 1.0
        norm_scores = sim_scores / max_s

        score_map = {}
        for idx, score in enumerate(norm_scores):
            dest_id = int(self.df.iloc[idx]["id"])
            score_map[dest_id] = float(score)

        return score_map
