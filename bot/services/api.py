"""API service - communicates with the jokes backend."""

import httpx
from typing import Optional
from dataclasses import dataclass

from config import settings


@dataclass
class Joke:
    """Represents a joke from the API."""

    joke_id: int
    text: str
    category: str
    likes: int = 0
    dislikes: int = 0
    user_rating: Optional[int] = None


@dataclass
class RatingStats:
    """Rating statistics for a joke."""

    joke_id: int
    likes: int
    dislikes: int
    total_votes: int


class APIError(Exception):
    """API error."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ApiService:
    """Service for communicating with the jokes backend API."""

    def __init__(self) -> None:
        """Initialize API service."""
        self.base_url = settings.api_base_url

    async def _get(self, path: str, params: dict | None = None) -> dict:
        """Make GET request to API."""
        url = f"{self.base_url}{path}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            if response.status_code == 404:
                raise APIError("Not found", 404)
            elif response.status_code != 200:
                raise APIError(f"API error: {response.text}", response.status_code)
            return response.json()

    async def post(self, path: str, json: dict) -> dict:
        """Make POST request to API."""
        url = f"{self.base_url}{path}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=json)
            if response.status_code not in (200, 201):
                raise APIError(f"API error: {response.text}", response.status_code)
            return response.json()

    async def get_random_joke(self, telegram_user_id: int | None = None) -> Joke:
        """Get a random joke from backend."""
        params = {}
        if telegram_user_id:
            params["telegram_user_id"] = telegram_user_id

        data = await self._get("/api/jokes/random", params)
        return Joke(
            joke_id=data["id"],
            text=data["text"],
            category=data["category"],
            likes=data["likes"],
            dislikes=data["dislikes"],
            user_rating=data.get("user_rating"),
        )

    async def get_joke_by_id(
        self, joke_id: int, telegram_user_id: int | None = None
    ) -> Joke:
        """Get a joke by ID."""
        params = {}
        if telegram_user_id:
            params["telegram_user_id"] = telegram_user_id

        data = await self._get(f"/api/jokes/{joke_id}", params)
        return Joke(
            joke_id=data["id"],
            text=data["text"],
            category=data["category"],
            likes=data["likes"],
            dislikes=data["dislikes"],
            user_rating=data.get("user_rating"),
        )

    async def get_joke_by_category(
        self, category: str, telegram_user_id: int | None = None
    ) -> Joke:
        """Get a joke from specific category."""
        params = {}
        if telegram_user_id:
            params["telegram_user_id"] = telegram_user_id

        data = await self._get(f"/api/jokes/category/{category}", params)
        return Joke(
            joke_id=data["id"],
            text=data["text"],
            category=data["category"],
            likes=data["likes"],
            dislikes=data["dislikes"],
            user_rating=data.get("user_rating"),
        )

    async def get_categories(self) -> list[str]:
        """Get all available categories."""
        data = await self._get("/api/jokes/categories")
        return data

    async def get_top_jokes(self, limit: int = 5) -> list[dict]:
        """Get top-rated jokes."""
        data = await self._get("/api/jokes/top", {"limit": limit})
        return data

    async def get_stats(self) -> dict:
        """Get joke statistics."""
        return await self._get("/api/stats")

    async def rate_joke(
        self, joke_id: int, telegram_user_id: int, rating: int
    ) -> RatingStats:
        """Rate a joke."""
        data = await self.post(
            f"/api/jokes/{joke_id}/rate",
            {"telegram_user_id": telegram_user_id, "rating": rating},
        )
        return RatingStats(
            joke_id=data["joke_id"],
            likes=data["likes"],
            dislikes=data["dislikes"],
            total_votes=data["total_votes"],
        )


# Global service instance
api_service = ApiService()
