"""
Collaborative Filtering Recommender
─────────────────────────────────────
Uses the Surprise library to implement SVD-based collaborative
filtering on the user-song interaction matrix.

Key concepts:
- SVD (Singular Value Decomposition): factorises the interaction
  matrix into latent user and item factors. Users with similar
  taste end up close together in latent space.
- Interaction matrix: rows = users, columns = songs,
  values = implicit rating (derived from play duration + feedback)
- Matrix sparsity: most users have not heard most songs.
  Typical sparsity is >95%. SVD handles this well.

References:
  - Surprise docs: https://surpriselib.com
  - SVD paper: Koren et al. (2009) "Matrix Factorization Techniques
    for Recommender Systems"
"""

from __future__ import annotations

import logging
import pickle
from pathlib import Path

import pandas as pd
from surprise import SVD, Dataset, Reader, accuracy
from surprise.model_selection import train_test_split

logger = logging.getLogger(__name__)

MODEL_PATH = Path(__file__).parent / "models" / "svd_model.pkl"


class MusicRecommender:
    """
    SVD-based collaborative filtering recommender.

    Usage:
        recommender = MusicRecommender()
        recommender.train(interactions_df)
        recommendations = recommender.recommend(session_id, candidate_songs)
    """

    def __init__(self, n_factors: int = 100, n_epochs: int = 20) -> None:
        """
        Args:
            n_factors: Number of latent factors. Higher = more expressive
                       but slower to train and more prone to overfitting.
            n_epochs:  Training iterations. 20 is a good starting point.
        """
        self.model = SVD(n_factors=n_factors, n_epochs=n_epochs, verbose=False)
        self.is_trained = False

    def train(self, interactions_df: pd.DataFrame) -> dict[str, float]:
        """
        Train the SVD model on user-song interactions.

        Args:
            interactions_df: DataFrame with columns:
                             [user_id, song_id, rating]
                             Rating is derived from play duration + feedback.

        Returns:
            Dict of evaluation metrics: {"rmse": float, "mae": float}
        """
        reader = Reader(rating_scale=(0, 5))
        data = Dataset.load_from_df(
            interactions_df[["user_id", "song_id", "rating"]],
            reader,
        )

        trainset, testset = train_test_split(data, test_size=0.2, random_state=42)

        logger.info("Training SVD model...")
        self.model.fit(trainset)
        self.is_trained = True

        # Evaluate on test set
        predictions = self.model.test(testset)
        rmse = accuracy.rmse(predictions, verbose=False)
        mae = accuracy.mae(predictions, verbose=False)

        metrics = {"rmse": round(rmse, 4), "mae": round(mae, 4)}
        logger.info("Training complete. Metrics: %s", metrics)

        return metrics

    def recommend(
        self,
        user_id: str,
        candidate_song_ids: list[str],
        limit: int = 10,
    ) -> list[tuple[str, float]]:
        """
        Generate top-N recommendations for a user.

        Args:
            user_id:           Session-based user identifier.
            candidate_song_ids: Songs to score (typically all songs
                                the user has NOT yet heard).
            limit:             Number of recommendations to return.

        Returns:
            List of (song_id, score) tuples sorted by score descending.
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained before calling recommend()")

        predictions = [
            (song_id, self.model.predict(user_id, song_id).est)
            for song_id in candidate_song_ids
        ]

        predictions.sort(key=lambda x: x[1], reverse=True)
        return predictions[:limit]


    def find_similar_users(
        self,
        user_id: str,
        all_user_ids: list[str],
        limit: int = 5,
    ) -> list[str]:
        """
        Find users with the most similar taste using cosine similarity
        on SVD latent factor vectors (ticket 2.3).

        If the user is not in the trainset (new user), returns an empty
        list so the caller can fall back to the co-like query.

        Args:
            user_id:      Session ID of the target user.
            all_user_ids: All known session IDs to compare against.
            limit:        Number of similar users to return.

        Returns:
            List of session_ids sorted by similarity descending.
        """
        if not self.is_trained:
            return []

        import numpy as np

        trainset = self.model.trainset

        try:
            inner_uid = trainset.to_inner_uid(user_id)
        except ValueError:
            logger.debug("User %s not in trainset — skipping SVD neighbours", user_id)
            return []

        target_vector = self.model.pu[inner_uid]
        target_norm = np.linalg.norm(target_vector) or 1.0

        similarities: list[tuple[str, float]] = []
        for other_id in all_user_ids:
            if other_id == user_id:
                continue
            try:
                other_inner = trainset.to_inner_uid(other_id)
            except ValueError:
                continue

            other_vector = self.model.pu[other_inner]
            other_norm = np.linalg.norm(other_vector) or 1.0
            cosine_sim = float(
                np.dot(target_vector, other_vector) / (target_norm * other_norm)
            )
            similarities.append((other_id, cosine_sim))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return [uid for uid, _ in similarities[:limit]]

    def save(self, path: Path = MODEL_PATH) -> None:
        """Persist trained model to disk."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self.model, f)
        logger.info("Model saved to %s", path)

    def load(self, path: Path = MODEL_PATH) -> None:
        """Load a previously trained model from disk."""
        if not path.exists():
            raise FileNotFoundError(f"No model found at {path}. Train first.")
        with open(path, "rb") as f:
            self.model = pickle.load(f)
        self.is_trained = True
        logger.info("Model loaded from %s", path)
