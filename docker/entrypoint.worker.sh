#!/bin/bash
set -e

echo "Waiting for postgres..."

while ! nc -z postgres 5432; do
  sleep 1
done

until curl -s http://localstack:4566/_localstack/health | grep '"sqs": "running"'; do
  sleep 2
done

echo "Starting worker..."

exec python app/worker/worker.py