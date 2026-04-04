"""API routers."""

from fastapi import APIRouter, Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import app.crud as crud
from app.database import get_db
from app.schemas import (
    JokeCreate,
    JokeResponse,
    JokeStats,
    RatingRequest,
    TopJokeResponse,
)

app = FastAPI(title="Roman Trakhtenberg Jokes API", version="1.0.0")

router = APIRouter(prefix="/api", tags=["jokes"])


# IMPORTANT: specific routes MUST come before parameterized ones.
# FastAPI matches in declaration order, so /jokes/top and /jokes/categories
# must be defined before /jokes/{joke_id} or they get captured by it.


@router.get("/jokes/random", response_model=JokeResponse)
def get_random_joke(telegram_user_id: int | None = None, db: Session = Depends(get_db)):
    """Get a random joke."""
    joke = crud.get_random_joke(db)
    if not joke:
        raise HTTPException(status_code=404, detail="No jokes in database")

    stats = crud.get_joke_stats(db, joke.id)
    user_rating = None
    if telegram_user_id:
        user_rating = crud.get_user_rating(db, joke.id, telegram_user_id)

    return JokeResponse(
        id=joke.id,
        text=joke.text,
        category=joke.category,
        created_at=joke.created_at,
        likes=stats["likes"],
        dislikes=stats["dislikes"],
        user_rating=user_rating,
    )


@router.get("/jokes/category/{category}", response_model=JokeResponse)
def get_joke_by_category(
    category: str, telegram_user_id: int | None = None, db: Session = Depends(get_db)
):
    """Get a random joke from a specific category."""
    joke = crud.get_joke_by_category(db, category)
    if not joke:
        raise HTTPException(status_code=404, detail="No jokes in this category")

    stats = crud.get_joke_stats(db, joke.id)
    user_rating = None
    if telegram_user_id:
        user_rating = crud.get_user_rating(db, joke.id, telegram_user_id)

    return JokeResponse(
        id=joke.id,
        text=joke.text,
        category=joke.category,
        created_at=joke.created_at,
        likes=stats["likes"],
        dislikes=stats["dislikes"],
        user_rating=user_rating,
    )


@router.get("/jokes/top", response_model=list[TopJokeResponse])
def get_top_jokes(limit: int = 5, db: Session = Depends(get_db)):
    """Get top-rated jokes."""
    top_jokes = crud.get_top_jokes(db, limit)
    return [TopJokeResponse(**joke) for joke in top_jokes]


@router.get("/jokes/categories", response_model=list[str])
def get_categories(db: Session = Depends(get_db)):
    """Get all available categories."""
    return crud.get_all_categories(db)


@router.get("/jokes/{joke_id}", response_model=JokeResponse)
def get_joke(joke_id: int, telegram_user_id: int | None = None, db: Session = Depends(get_db)):
    """Get a joke by ID."""
    joke = crud.get_joke_by_id(db, joke_id)
    if not joke:
        raise HTTPException(status_code=404, detail="Joke not found")

    stats = crud.get_joke_stats(db, joke.id)
    user_rating = None
    if telegram_user_id:
        user_rating = crud.get_user_rating(db, joke.id, telegram_user_id)

    return JokeResponse(
        id=joke.id,
        text=joke.text,
        category=joke.category,
        created_at=joke.created_at,
        likes=stats["likes"],
        dislikes=stats["dislikes"],
        user_rating=user_rating,
    )


@router.post("/jokes/{joke_id}/rate")
def rate_joke(joke_id: int, request: RatingRequest, db: Session = Depends(get_db)):
    """Rate a joke (1 = like, -1 = dislike)."""
    joke = crud.get_joke_by_id(db, joke_id)
    if not joke:
        raise HTTPException(status_code=404, detail="Joke not found")

    if request.rating not in (1, -1):
        raise HTTPException(status_code=400, detail="Rating must be 1 or -1")

    stats = crud.rate_joke(db, joke_id, request.telegram_user_id, request.rating)
    return stats


@router.get("/stats", response_model=JokeStats)
def get_stats(db: Session = Depends(get_db)):
    """Get joke statistics."""
    return JokeStats(
        total_jokes=crud.get_total_jokes(db),
        categories=crud.get_all_categories(db),
        total_ratings=db.query(crud.Rating).count(),
    )


@router.post("/jokes", response_model=JokeResponse, status_code=201)
def create_joke(joke: JokeCreate, db: Session = Depends(get_db)):
    """Add a new joke to the database."""
    new_joke = crud.Joke(text=joke.text, category=joke.category)
    db.add(new_joke)
    db.commit()
    db.refresh(new_joke)

    return JokeResponse(
        id=new_joke.id,
        text=new_joke.text,
        category=new_joke.category,
        created_at=new_joke.created_at,
    )


app.include_router(router)
