"""Database models."""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class Joke(Base):
    """Joke model."""

    __tablename__ = "jokes"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    category = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    ratings = relationship("Rating", back_populates="joke", cascade="all, delete-orphan")


class Rating(Base):
    """User rating for a joke."""

    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    joke_id = Column(Integer, ForeignKey("jokes.id", ondelete="CASCADE"), nullable=False)
    telegram_user_id = Column(Integer, nullable=False)
    rating = Column(Integer, nullable=False)  # 1 = like, -1 = dislike
    created_at = Column(DateTime, default=datetime.utcnow)

    joke = relationship("Joke", back_populates="ratings")

    __table_args__ = (
        UniqueConstraint("joke_id", "telegram_user_id", name="uq_joke_user"),
    )
