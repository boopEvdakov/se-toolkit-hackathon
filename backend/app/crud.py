"""Database CRUD operations."""

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Joke, Rating


# --- Joke operations ---


def get_random_joke(db: Session) -> Joke | None:
    """Get a random joke."""
    from sqlalchemy import func
    return db.query(Joke).order_by(func.random()).first()


def get_joke_by_id(db: Session, joke_id: int) -> Joke | None:
    """Get a joke by ID."""
    return db.query(Joke).filter(Joke.id == joke_id).first()


def get_joke_by_category(db: Session, category: str) -> Joke | None:
    """Get a random joke from a category."""
    from sqlalchemy import func
    return (
        db.query(Joke)
        .filter(Joke.category == category)
        .order_by(func.random())
        .first()
    )


def get_all_categories(db: Session) -> list[str]:
    """Get all unique categories."""
    rows = db.query(Joke.category).distinct().all()
    return sorted([r[0] for r in rows])


def get_total_jokes(db: Session) -> int:
    """Get total number of jokes."""
    return db.query(Joke).count()


def get_top_jokes(db: Session, limit: int = 5) -> list[dict]:
    """Get top jokes by net rating."""
    from sqlalchemy import case

    subquery = (
        db.query(
            Rating.joke_id.label("joke_id"),
            func.sum(Rating.rating).label("net_score"),
            func.count().label("total_votes"),
        )
        .group_by(Rating.joke_id)
        .having(func.count() >= 3)
        .order_by(func.sum(Rating.rating).desc())
        .limit(limit)
        .subquery()
    )

    results = (
        db.query(
            subquery.c.joke_id,
            subquery.c.net_score,
            subquery.c.total_votes,
        )
        .all()
    )

    top_jokes = []
    for row in results:
        joke = db.query(Joke).filter(Joke.id == row.joke_id).first()
        if joke:
            top_jokes.append({
                "joke_id": row.joke_id,
                "text": joke.text,
                "category": joke.category,
                "net_score": row.net_score,
                "total_votes": row.total_votes,
            })

    return top_jokes


def seed_jokes(db: Session, jokes_data: list[dict]) -> None:
    """Insert initial jokes into database (idempotent)."""
    for joke_data in jokes_data:
        existing = db.query(Joke).filter(Joke.id == joke_data["id"]).first()
        if not existing:
            joke = Joke(
                id=joke_data["id"],
                text=joke_data["text"],
                category=joke_data["category"],
            )
            db.add(joke)
    db.commit()


# --- Rating operations ---


def rate_joke(
    db: Session, joke_id: int, telegram_user_id: int, rating: int
) -> dict:
    """Rate a joke. Updates existing rating if user already voted."""
    existing = (
        db.query(Rating)
        .filter(Rating.joke_id == joke_id, Rating.telegram_user_id == telegram_user_id)
        .first()
    )

    if existing:
        existing.rating = rating
    else:
        new_rating = Rating(
            joke_id=joke_id,
            telegram_user_id=telegram_user_id,
            rating=rating,
        )
        db.add(new_rating)

    db.commit()

    return get_joke_stats(db, joke_id)


def get_joke_stats(db: Session, joke_id: int) -> dict:
    """Get rating statistics for a joke."""
    likes = db.query(Rating).filter(
        Rating.joke_id == joke_id, Rating.rating == 1
    ).count()

    dislikes = db.query(Rating).filter(
        Rating.joke_id == joke_id, Rating.rating == -1
    ).count()

    return {
        "joke_id": joke_id,
        "likes": likes,
        "dislikes": dislikes,
        "total_votes": likes + dislikes,
    }


def get_user_rating(
    db: Session, joke_id: int, telegram_user_id: int
) -> int | None:
    """Get user's rating for a joke."""
    rating = (
        db.query(Rating)
        .filter(Rating.joke_id == joke_id, Rating.telegram_user_id == telegram_user_id)
        .first()
    )
    return rating.rating if rating else None
