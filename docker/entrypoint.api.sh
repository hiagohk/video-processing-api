#!/bin/bash
set -e

echo "Waiting for postgres..."

while ! nc -z postgres 5432; do
  sleep 1
done

echo "Running migrations..."
alembic upgrade head || exit 1

echo "Starting API..."

exec uvicorn app.main:app --host 0.0.0.0 --port 8000