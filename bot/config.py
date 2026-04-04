"""Configuration loading from environment variables."""

from pydantic_settings import BaseSettings


class BotSettings(BaseSettings):
    """Bot configuration loaded from environment variables."""

    # Telegram bot token
    bot_token: str = ""

    # Backend API URL
    api_base_url: str = "http://localhost:42001"

    class Config:
        env_file = ".env.bot.secret"
        env_file_encoding = "utf-8"


# Global settings instance
settings = BotSettings()
