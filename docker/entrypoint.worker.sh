#!/bin/bash
set -e

echo "Waiting for postgres..."

while ! nc -z postgres 5432; do
  sleep 1
done

echo "Starting worker..."

exec python app/worker/worker.py