# Roman Trakhtenberg Jokes Bot — Development Plan

This document outlines the implementation plan for the Roman Trakhtenberg jokes Telegram bot.

## Project Overview

### End-user
- Admirers of humor and wit
- Russian-speaking Telegram users
- Fans of stand-up comedy and clever observations about life

### Problem it solves
- Provides instant access to a curated collection of Roman Trakhtenberg's jokes and quotes
- No need to search through books or social media — just ask the bot for a joke

### Product idea in one sentence
A Telegram bot that delivers random jokes and quotes from Roman Trakhtenberg's comedy repertoire on demand.

### Core feature
Send a command → get a random Trakhtenberg joke with inline rating buttons (👍/👎).

### Additional features
- Rating system persisted via PostgreSQL
- One-click "Next joke" for quick browsing
- Joke categorization by theme (life, relationships, work, etc.)
- API endpoint for adding new jokes

## Architecture

The project follows a 3-tier architecture:

```
┌──────────────┐     HTTP      ┌──────────────┐     PostgreSQL    ┌──────────┐
│  Telegram    │ ◄──────────►  │  Backend     │ ◄──────────────►  │  VM DB   │
│   Bot        │  API calls   │  FastAPI     │      queries      │          │
│  (aiogram)   │               │  (port 42020) │                   │          │
└──────────────┘               └──────────────┘                   └──────────┘
```

### Components

| Component | Tech | Location |
|-----------|------|----------|
| **Client** (Telegram bot) | Python, aiogram | Docker container |
| **Backend API** | Python, FastAPI, SQLAlchemy | Docker container on VM |
| **Database** | PostgreSQL 18 | Docker container on VM |

### Layered Architecture (Bot)

1. **Transport Layer** (`bot.py`) — Telegram API communication via aiogram
2. **Handler Layer** (`handlers/`) — Pure functions, testable without Telegram
3. **Service Layer** (`services/api.py`) — HTTP client to backend API
4. **Configuration** (`config.py`) — Environment variable loading

## Version 1 (Core Product)

**Goal:** Working bot with backend and database.

Features:
- ✅ `/start` — Welcome message
- ✅ `/help` — List available commands
- ✅ `/joke` — Get a random joke with rating buttons
- ✅ FastAPI backend with PostgreSQL database
- ✅ Inline keyboard: 👍 / 👎 / 🎭 Next joke
- ✅ Docker Compose orchestration
- ✅ Deployed on VM

**Success criteria:**
- ✅ Bot responds to /start and /joke
- ✅ Backend returns jokes from PostgreSQL
- ✅ Rating buttons update the message with new count

## Version 2 (Enhanced)

**Goal:** Improved user experience and deployed product.

Features:
- ✅ Rating system persisted via PostgreSQL (one vote per user per joke)
- ✅ API endpoints for categories, top jokes, stats
- ✅ Polished README with full documentation
- ✅ Pushed to GitHub repository
- ✅ Dockerized all services
- ✅ Deployed on VM (Ubuntu 24.04)

## Implementation Strategy

### Phase 1: Foundation (Version 1)
1. Create project structure (backend + bot)
2. Build FastAPI backend with PostgreSQL
3. Seed database with initial jokes
4. Implement Telegram bot with aiogram
5. Containerize with Docker Compose

### Phase 2: Enhancement (Version 2)
1. Add rating system with inline buttons
2. Add API endpoints for top jokes, categories, stats
3. Deploy to VM via Docker Compose
4. Create documentation (README + PLAN)
5. Push to GitHub

## Testing Strategy

1. **CLI test mode** — `uv run bot.py --test "/joke"` for manual testing
2. **Integration tests** — Bot talks to real backend API
3. **API tests** — Direct curl to backend endpoints
4. **Deployment verification** — Send commands via Telegram

## Technical Stack

| Layer | Technology |
|-------|-----------|
| **Language** | Python 3.12+ |
| **Telegram framework** | aiogram 3.20+ |
| **Backend framework** | FastAPI |
| **ORM** | SQLAlchemy |
| **Database** | PostgreSQL 18 |
| **HTTP client** | httpx |
| **Containerization** | Docker + Docker Compose |
| **Package manager** | uv |
