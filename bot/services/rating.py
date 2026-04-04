"""Rating service - manages user ratings for jokes using SQLite."""

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class RatingStats:
    """Statistics for a joke's ratings."""

    joke_id: int
    likes: int
    dislikes: int
    total_votes: int


class RatingService:
    """Service for managing joke ratings."""

    def __init__(self, db_path: str = "ratings.db") -> None:
        """Initialize rating service and create database if needed."""
        self._db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Initialize database tables."""
        conn = self._get_connection()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ratings (
                    joke_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    rating INTEGER NOT NULL CHECK(rating IN (1, -1)),
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (joke_id, user_id)
                )
            """)
            conn.commit()
        finally:
            conn.close()

    def rate_joke(self, joke_id: int, user_id: int, rating: int) -> RatingStats:
        """
        Rate a joke. Rating must be 1 (like) or -1 (dislike).
        Users can change their vote - latest one counts.
        """
        conn = self._get_connection()
        try:
            # Insert or replace the rating
            conn.execute("""
                INSERT INTO ratings (joke_id, user_id, rating)
                VALUES (?, ?, ?)
                ON CONFLICT(joke_id, user_id) 
                DO UPDATE SET rating = ?, timestamp = CURRENT_TIMESTAMP
            """, (joke_id, user_id, rating, rating))
            conn.commit()
            
            return self.get_joke_stats(joke_id)
        finally:
            conn.close()

    def get_joke_stats(self, joke_id: int) -> RatingStats:
        """Get rating statistics for a specific joke."""
        conn = self._get_connection()
        try:
            row = conn.execute("""
                SELECT 
                    joke_id,
                    SUM(CASE WHEN rating = 1 THEN 1 ELSE 0 END) as likes,
                    SUM(CASE WHEN rating = -1 THEN 1 ELSE 0 END) as dislikes,
                    COUNT(*) as total_votes
                FROM ratings
                WHERE joke_id = ?
                GROUP BY joke_id
            """, (joke_id,)).fetchone()
            
            if row is None:
                return RatingStats(joke_id=joke_id, likes=0, dislikes=0, total_votes=0)
            
            return RatingStats(
                joke_id=row["joke_id"],
                likes=row["likes"],
                dislikes=row["dislikes"],
                total_votes=row["total_votes"]
            )
        finally:
            conn.close()

    def get_top_jokes(self, limit: int = 10) -> list[tuple[int, int]]:
        """
        Get top jokes by net rating (likes - dislikes).
        Returns list of (joke_id, net_score) sorted by score descending.
        """
        conn = self._get_connection()
        try:
            rows = conn.execute("""
                SELECT 
                    joke_id,
                    SUM(rating) as net_score,
                    COUNT(*) as total_votes
                FROM ratings
                GROUP BY joke_id
                HAVING total_votes >= 3
                ORDER BY net_score DESC
                LIMIT ?
            """, (limit,)).fetchall()
            
            return [(row["joke_id"], row["net_score"]) for row in rows]
        finally:
            conn.close()

    def get_user_rating(self, joke_id: int, user_id: int) -> Optional[int]:
        """Get user's rating for a specific joke."""
        conn = self._get_connection()
        try:
            row = conn.execute("""
                SELECT rating FROM ratings
                WHERE joke_id = ? AND user_id = ?
            """, (joke_id, user_id)).fetchone()
            
            return row["rating"] if row else None
        finally:
            conn.close()
