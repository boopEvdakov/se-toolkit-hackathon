"""Pydantic schemas for API requests/responses."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class JokeBase(BaseModel):
    """Base joke schema."""

    text: str
    category: str


class JokeCreate(JokeBase):
    """Schema for creating a joke."""

    pass


class JokeResponse(JokeBase):
    """Schema for joke response."""

    id: int
    created_at: datetime
    likes: int = 0
    dislikes: int = 0
    user_rating: Optional[int] = None

    class Config:
        from_attributes = True


class RatingRequest(BaseModel):
    """Schema for rating a joke."""

    telegram_user_id: int
    rating: int  # 1 or -1


class JokeStats(BaseModel):
    """Statistics about jokes."""

    total_jokes: int
    categories: list[str]
    total_ratings: int


class TopJokeResponse(BaseModel):
    """Top joke with score."""

    joke_id: int
    text: str
    category: str
    net_score: int
    total_votes: int
