"""Joke database service - provides access to Roman Trakhtenberg's jokes."""

import random
from dataclasses import dataclass
from typing import Optional


@dataclass
class Joke:
    """Represents a single joke."""

    text: str
    category: str
    joke_id: int


# Built-in joke database
JOKES_DATABASE = [
    {
        "id": 1,
        "text": "Мужик возвращается домой под утро пьяный. Открывает дверь, при этом задевает стремянку, та рушится на велосипед, он сшибает на пол вазу, ваза падает на кота… Из комнат выглядывают жена и сын.\n— Что, не спится без папки?",
        "category": "семья",
    },
    {
        "id": 2,
        "text": "Океанский лайнер терпит кораблекрушение. Спаслись всего два человека: один из пассажиров и Клаудия Шиффер. Им удалось добраться до острова, который оказался необитаемым. Поселились они там, значит, живут и вовсю любят друг друга. Все бы хорошо, только пассажир с каждым днем все грустнее и грустнее.\n— Что такое, дорогой? — спрашивает Клаудия Шиффер. — Я могу чем-то помочь?\n— Да. Надень мои пальто и шляпу.\nКлаудия выполнила просьбу. Пассажир, обращаясь к переодетой супермодели, восторженно воскликнул:\n— Представляешь, мужик, я с Клаудией Шиффер сплю!",
        "category": "отношения",
    },
    {
        "id": 3,
        "text": "— Что-то у меня бритва не бреет, — говорит муж.\n— Странно. А линолеум она хорошо резала, — отвечает жена.",
        "category": "семья",
    },
    {
        "id": 4,
        "text": "В трамвае едет старушка, рядом с ней стоит мальчик. Бабушка достает табакерку, берет понюшку и чихает.\n— Будьте здоровы, бабушка! — говорит мальчик.\n— Спасибо, внучек.\nБабушка опять берет табачку, делает понюшку и опять чихает.\n— Будьте здоровы, бабушка! — опять говорит мальчик.\n— Ну ты и глупый! Я же чихаю не потому, что болею, а потому, что табак нюхаю.\n— Да вы, бабушка, хоть помет нюхайте, а пионер всегда должен быть вежливым!",
        "category": "жизнь",
    },
    {
        "id": 5,
        "text": "Заметка в газете: «Гражданка Иванова родила шестерых детей. Врачи надеются, что им удастся спасти жизнь гражданина Иванова».",
        "category": "здоровье",
    },
    {
        "id": 6,
        "text": "— Товарищ милиционер, по этой улице ходить опасно?\n— Было бы опасно, фиг бы я здесь стоял.",
        "category": "жизнь",
    },
    {
        "id": 7,
        "text": "Поручик Ржевский сидит с Наташей Ростовой на лавочке. Она ему:\n— Поручик, посмотрите, какое прекрасное звездное небо!..\nТот отвечает:\n— Знаете, Наташа. Просто не хочется.",
        "category": "отношения",
    },
    {
        "id": 8,
        "text": "Собрался конгресс женщин. На повестке дня три вопроса: 1) нечего носить, 2) все мужики козлы, 3) разное.",
        "category": "жизнь",
    },
    {
        "id": 9,
        "text": "— Ну как пиво?\n— Пенистое.\n— Что, по-русски не мог сказать, что хреновое? А то выпендрился по-латыни.",
        "category": "жизнь",
    },
    {
        "id": 10,
        "text": "Молодой милиционер пришел устраиваться в органы. Его приняли. Проходит месяц, два, три, а он так ни разу и не пришел за зарплатой.\nВызывает его начальник и спрашивает:\n— Ты что это за зарплатой не приходишь? Не нужна, что ли?!\n— Я думал, дали пистолет — и крутись как хочешь.",
        "category": "работа",
    },
]


class JokeService:
    """Service for managing and retrieving jokes."""

    def __init__(self) -> None:
        """Initialize the joke service."""
        self._jokes: list[Joke] = [
            Joke(
                text=joke_data["text"],
                category=joke_data["category"],
                joke_id=joke_data["id"],
            )
            for joke_data in JOKES_DATABASE
        ]
        self._categories: set[str] = {joke.category for joke in self._jokes}

    def get_random_joke(self) -> Joke:
        """Get a random joke."""
        return random.choice(self._jokes)

    def get_joke_by_id(self, joke_id: int) -> Optional[Joke]:
        """Get a joke by its ID."""
        for joke in self._jokes:
            if joke.joke_id == joke_id:
                return joke
        return None

    def get_random_joke_by_category(self, category: str) -> Optional[Joke]:
        """Get a random joke from a specific category."""
        category_jokes = [joke for joke in self._jokes if joke.category == category]
        if not category_jokes:
            return None
        return random.choice(category_jokes)

    def get_categories(self) -> list[str]:
        """Get list of all available categories."""
        return sorted(self._categories)

    def get_jokes_by_category(self, category: str) -> list[Joke]:
        """Get all jokes from a specific category."""
        return [joke for joke in self._jokes if joke.category == category]

    def get_total_jokes_count(self) -> int:
        """Get total number of jokes in the database."""
        return len(self._jokes)

    def search_jokes(self, query: str) -> list[Joke]:
        """Search jokes by text (case-insensitive)."""
        query_lower = query.lower()
        return [joke for joke in self._jokes if query_lower in joke.text.lower()]

    def get_all_jokes(self) -> list[Joke]:
        """Get all jokes."""
        return self._jokes.copy()


# Global service instance
joke_service = JokeService()
