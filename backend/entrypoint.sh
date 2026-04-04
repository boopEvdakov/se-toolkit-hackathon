#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
sleep 5

echo "Running database seed..."
PYTHONPATH=/app python -c "from app.seed import seed; seed()"

echo "Starting FastAPI server..."
export PYTHONPATH=/app
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
