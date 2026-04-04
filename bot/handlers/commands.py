"""Command handlers - pure functions that call backend API.

These handlers have no dependency on Telegram. They can be called from:
- The --test CLI mode
- Unit tests
- The Telegram bot
"""

from services.api import APIError, api_service


async def handle_start(command: str) -> str:
    """Handle /start command - welcome message."""
    try:
        stats = await api_service.get_stats()
        total_jokes = stats["total_jokes"]
        return f"""Привет! Добро пожаловать в бота с анекдотами Романа Трахтенберга! 🎭

В моей коллекции {total_jokes} шуток и цитат.

Используй /help, чтобы узнать, что я умею."""
    except APIError:
        return """Привет! Добро пожаловать в бота с анекдотами Романа Трахтенберга! 🎭

Используй /help, чтобы узнать, что я умею."""


async def handle_help(command: str) -> str:
    """Handle /help command - list available commands."""
    return """Доступные команды:

/start - Приветствие
/help - Показать это сообщение
/joke - Случайный анекдот

Нажмите кнопки под шуткой, чтобы оценить её:
👍 — нравится
👎 — не нравится
🎭 — показать следующую шутку"""


async def handle_joke(command: str) -> str:
    """Handle /joke command - get a random joke."""
    try:
        joke = await api_service.get_random_joke()
        rating_text = f"\n👍 {joke.likes} | 👎 {joke.dislikes}"
        return f"""{joke.text}

📂 Категория: {joke.category}
🆔 #{joke.joke_id}{rating_text}"""
    except APIError as e:
        return f"Не удалось получить шутку: {e.message}. Проверьте соединение с сервером."


async def handle_category(command: str) -> str:
    """Handle /category <name> command - get a joke from specific category."""
    category = command.replace("/category", "").strip()

    if not category:
        try:
            categories = await api_service.get_categories()
            categories_text = ", ".join(categories)
        except APIError:
            categories_text = "загрузка..."

        return f"""Пожалуйста, укажите категорию.

Доступные категории:
{categories_text}

Пример: /category жизнь"""

    try:
        joke = await api_service.get_joke_by_category(category)
        rating_text = f"\n👍 {joke.likes} | 👎 {joke.dislikes}"
        return f"""{joke.text}

📂 Категория: {joke.category}
🆔 #{joke.joke_id}{rating_text}"""
    except APIError as e:
        try:
            categories = await api_service.get_categories()
            categories_text = ", ".join(categories)
        except APIError:
            categories_text = "загрузка..."

        return f"""Категория "{category}" не найдена.

Доступные категории:
{categories_text}"""


async def handle_top(command: str) -> str:
    """Handle /top command - show top-rated jokes."""
    try:
        top_jokes = await api_service.get_top_jokes(limit=5)

        if not top_jokes:
            return "Пока нет оценок. Оценивайте шутки кнопками 👍/👎!"

        lines = ["🏆 Топ шуток по оценкам пользователей:\n"]

        for rank, joke_data in enumerate(top_jokes, 1):
            lines.append(f"""{rank}. {joke_data['text']}
   📂 {joke_data['category']} | 👍 {joke_data['net_score']} | 🗳 {joke_data['total_votes']} голосов
""")

        return "\n".join(lines)
    except APIError as e:
        return f"Не удалось получить топ шуток: {e.message}"


async def handle_stats(command: str) -> str:
    """Handle /stats command - show joke statistics."""
    try:
        stats = await api_service.get_stats()
        categories = stats.get("categories", [])

        lines = ["📊 Статистика:", ""]
        lines.append(f"Всего шуток: {stats['total_jokes']}")
        lines.append(f"Категорий: {len(categories)}")
        lines.append(f"Оценок: {stats['total_ratings']}")
        lines.append("")
        lines.append("Шуток по категориям:")

        for category in categories:
            lines.append(f"  • {category}")

        return "\n".join(lines)
    except APIError as e:
        return f"Не удалось получить статистику: {e.message}"


async def handle_unknown(text: str) -> str:
    """Handle unknown commands or plain text."""
    return """Я не понял команду. 🤔

Используйте /help, чтобы узнать, что я умею.

Или попробуйте:
/joke - случайный анекдот
/category жизнь - анекдот из категории"""
