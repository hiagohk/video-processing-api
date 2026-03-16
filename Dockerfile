
FROM python:3.11

WORKDIR /app

COPY requirements.txt .
COPY requirements-dev.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-dev.txt
RUN pip install psycopg2-binary

COPY . .

ENV PYTHONPATH=/app
RUN chmod +x docker/entrypoint.sh
CMD ["bash", "docker/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]