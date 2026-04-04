# Roman Trakhtenberg Jokes Bot — Development Plan

This document outlines the implementation plan for the Roman Trakhtenberg jokes Telegram bot.

## Project Overview

### End-user
- People who enjoy humor, stand-up comedy, and Roman Trakhtenberg's witty observations about life
- Russian-speaking Telegram users looking for quick entertainment

### Problem it solves
- Provides instant access to a curated collection of Roman Trakhtenberg's jokes and quotes
- No need to search through books or social media - just ask the bot for a joke

### Product idea in one sentence
A Telegram bot that delivers random jokes and quotes from Roman Trakhtenberg's comedy repertoire on demand.

### Core feature
- Send a command or message → get a random Trakhtenberg joke
- Categorization by themes (life, relationships, work, philosophy, etc.)
- Favorite jokes saving feature

## Architecture

The bot follows a layered architecture:

1. **Transport Layer** (`bot.py`) — Handles Telegram API communication via aiogram
2. **Handler Layer** (`handlers/`) — Pure functions that process commands and return responses
3. **Service Layer** (`services/`) — Joke database and retrieval logic
4. **Configuration** (`config.py`) — Environment variable loading

This separation ensures handlers are testable without Telegram connectivity.

## Version 1 (Core Product)

**Goal:** Working bot that delivers random Trakhtenberg jokes.

Features:
- `/start` — Welcome message
- `/help` — List available commands
- `/joke` — Get a random joke
- `/category <name>` — Get a joke from a specific category
- Built-in joke database (JSON file)
- CLI test mode for development
- Docker containerization

**Success criteria:**
- Bot responds to commands
- Random joke delivery works
- Categories work correctly
- Bot runs in Docker

## Version 2 (Enhanced)

**Goal:** Improved user experience and additional features.

Features:
- "Add to favorites" — Save jokes via inline button
- `/favorites` — View saved jokes
- "Next joke" inline keyboard button for quick browsing
- LLM-powered natural language search (ask for jokes about specific topics)
- Joke rating system
- Statistics (total jokes, most popular categories)
- Deployed and accessible

## Implementation Strategy

### Phase 1: Foundation (Version 1)
1. Create project structure
2. Build joke database service with ~50+ jokes
3. Implement command handlers
4. Add CLI test mode
5. Containerize with Docker

### Phase 2: Enhancement (Version 2)
1. Add favorites system (SQLite database)
2. Implement inline keyboards
3. Add LLM-powered search
4. Deploy to VM
5. Create documentation and demo video

## Testing Strategy

1. **Unit tests** — Test handlers in isolation (pytest)
2. **Test mode** — Manual verification via `--test` flag
3. **Integration tests** — Test with real joke database
4. **Deployment verification** — Send commands via Telegram

## Technical Stack

- **Language:** Python 3.14+
- **Telegram framework:** aiogram 3.20+
- **Database:** JSON file (V1) → SQLite (V2)
- **Containerization:** Docker + docker-compose
- **LLM integration:** Optional (for V2 natural language search)
