
FROM python:3.11

WORKDIR /app

COPY requirements.txt .
COPY requirements-dev.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-dev.txt
RUN pip install psycopg2-binary
RUN apt-get update && apt-get install -y netcat-openbsd

COPY . .

ENV PYTHONPATH=/app
RUN chmod +x docker/entrypoint.api.sh
RUN chmod +x docker/entrypoint.worker.sh