#!/bin/bash

# Wait for database to be ready
echo "Waiting for database to be ready..."
while ! pg_isready -h $POSTGRES_SERVER -p $POSTGRES_PORT -U $POSTGRES_USER; do
  echo "Database is unavailable - sleeping"
  sleep 2
done

echo "Database is ready!"

# Run Alembic migrations
echo "Running Alembic migrations..."
alembic upgrade head

# Start the application
echo "Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000



