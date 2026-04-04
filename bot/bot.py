#!/usr/bin/env python3
"""Roman Trakhtenberg Jokes Telegram Bot - Entry point.

Usage:
    uv run bot.py              # Run the Telegram bot
    uv run bot.py --test "/joke"  # Test mode - print response to stdout
"""

import asyncio
import sys
from typing import Optional

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import settings
from handlers.commands import (
    handle_category,
    handle_help,
    handle_joke,
    handle_start,
    handle_stats,
    handle_top,
    handle_unknown,
)
from services.api import APIError, api_service


# ---------------------------------------------------------------------------
# Test mode - run handlers directly without Telegram
# ---------------------------------------------------------------------------


async def run_test_mode(command: str) -> None:
    """Run a command through the handler and print the result to stdout."""
    command = command.strip()

    if command == "/start" or command.startswith("/start "):
        result = await handle_start(command)
    elif command == "/help" or command.startswith("/help "):
        result = await handle_help(command)
    elif command == "/joke" or command.startswith("/joke "):
        result = await handle_joke(command)
    elif command.startswith("/category"):
        result = await handle_category(command)
    elif command == "/top" or command.startswith("/top "):
        result = await handle_top(command)
    elif command == "/stats" or command.startswith("/stats "):
        result = await handle_stats(command)
    else:
        result = await handle_unknown(command)

    print(result)


# ---------------------------------------------------------------------------
# Telegram bot mode - handle messages from Telegram
# ---------------------------------------------------------------------------


def create_joke_keyboard(joke_id: int) -> InlineKeyboardMarkup:
    """Create inline keyboard for joke rating."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👍 Нравится", callback_data=f"like_{joke_id}"),
                InlineKeyboardButton(text="👎 Не нравится", callback_data=f"dislike_{joke_id}"),
            ],
            [
                InlineKeyboardButton(text="🎭 Ещё шутку", callback_data="next_joke"),
            ],
        ]
    )


async def cmd_start(message: Message) -> None:
    """Handle /start command from Telegram."""
    response = await handle_start("/start")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎭 Случайная шутка", callback_data="next_joke")],
            [InlineKeyboardButton(text="❓ Помощь", callback_data="help")],
        ]
    )

    await message.answer(response, reply_markup=keyboard)


async def cmd_help(message: Message) -> None:
    """Handle /help command from Telegram."""
    response = await handle_help("/help")
    await message.answer(response)


async def cmd_joke(message: Message) -> None:
    """Handle /joke command from Telegram."""
    await send_random_joke(message)


async def cmd_category(message: Message) -> None:
    """Handle /category command from Telegram."""
    command = message.text or "/category"
    response = await handle_category(command)
    await message.answer(response)


async def cmd_top(message: Message) -> None:
    """Handle /top command from Telegram."""
    response = await handle_top("/top")
    await message.answer(response)


async def cmd_stats(message: Message) -> None:
    """Handle /stats command from Telegram."""
    response = await handle_stats("/stats")
    await message.answer(response)


async def send_random_joke(message: Message) -> None:
    """Send a random joke with rating buttons."""
    user_id = message.from_user.id

    try:
        joke = await api_service.get_random_joke(telegram_user_id=user_id)
    except APIError as e:
        await message.answer(f"Не удалось получить шутку: {e.message}")
        return

    rating_text = ""
    if joke.likes > 0 or joke.dislikes > 0:
        rating_text = f"\n👍 {joke.likes} | 👎 {joke.dislikes}"

    response = f"""{joke.text}

📂 Категория: {joke.category}
🆔 #{joke.joke_id}{rating_text}"""

    keyboard = create_joke_keyboard(joke.joke_id)
    await message.answer(response, reply_markup=keyboard)


async def handle_message(message: Message) -> None:
    """Handle plain text messages."""
    text = message.text or ""
    response = await handle_unknown(text)
    await message.answer(response)


async def handle_callback(callback: types.CallbackQuery) -> None:
    """Handle inline keyboard button clicks."""
    action = callback.data
    user_id = callback.from_user.id

    if action.startswith("like_"):
        joke_id = int(action.replace("like_", ""))
        try:
            stats = await api_service.rate_joke(joke_id, user_id, 1)
            await callback.answer("Спасибо за оценку! 👍")

            # Get updated joke data
            try:
                joke = await api_service.get_joke_by_id(joke_id, user_id)
                new_text = f"""{joke.text}

📂 Категория: {joke.category}
🆔 #{joke.joke_id}
👍 {joke.likes} | 👎 {joke.dislikes}"""
                keyboard = create_joke_keyboard(joke_id)
                await callback.message.edit_text(new_text, reply_markup=keyboard)
            except Exception:
                pass
        except APIError:
            await callback.answer("Ошибка при оценке")

    elif action.startswith("dislike_"):
        joke_id = int(action.replace("dislike_", ""))
        try:
            stats = await api_service.rate_joke(joke_id, user_id, -1)
            await callback.answer("Спасибо за оценку! 👎")

            try:
                joke = await api_service.get_joke_by_id(joke_id, user_id)
                new_text = f"""{joke.text}

📂 Категория: {joke.category}
🆔 #{joke.joke_id}
👍 {joke.likes} | 👎 {joke.dislikes}"""
                keyboard = create_joke_keyboard(joke_id)
                await callback.message.edit_text(new_text, reply_markup=keyboard)
            except Exception:
                pass
        except APIError:
            await callback.answer("Ошибка при оценке")

    elif action == "next_joke":
        await send_random_joke(callback.message)

    elif action == "show_categories":
        try:
            categories = await api_service.get_categories()
            response = f"""📂 Доступные категории:

{", ".join(categories)}

Напишите /category <название>, например:
/category жизнь"""
            await callback.message.answer(response)
        except APIError as e:
            await callback.message.answer(f"Ошибка: {e.message}")

    elif action == "show_top":
        response = await handle_top("/top")
        await callback.message.answer(response)

    elif action == "help":
        response = await handle_help("/help")
        await callback.message.answer(response)

    else:
        response = "Неизвестное действие."
        await callback.message.answer(response)

    await callback.answer()


async def run_telegram_mode() -> None:
    """Run the Telegram bot."""
    if not settings.bot_token:
        print("Error: BOT_TOKEN not set in .env.bot.secret", file=sys.stderr)
        sys.exit(1)

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    # Register handlers
    dp.message.register(cmd_start, CommandStart())
    dp.message.register(cmd_help, Command("help"))
    dp.message.register(cmd_joke, Command("joke"))
    dp.message.register(cmd_category, Command("category"))
    dp.message.register(cmd_top, Command("top"))
    dp.message.register(cmd_stats, Command("stats"))
    dp.message.register(handle_message)
    dp.callback_query.register(handle_callback)

    print("🎭 Trakhtenberg Jokes Bot is starting...")
    print(f"🔗 Backend API: {settings.api_base_url}")
    await dp.start_polling(bot)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        if len(sys.argv) < 3:
            print("Usage: bot.py --test <command>", file=sys.stderr)
            print("Example: bot.py --test '/joke'", file=sys.stderr)
            sys.exit(1)

        command = " ".join(sys.argv[2:])
        asyncio.run(run_test_mode(command))
    else:
        asyncio.run(run_telegram_mode())


if __name__ == "__main__":
    main()
