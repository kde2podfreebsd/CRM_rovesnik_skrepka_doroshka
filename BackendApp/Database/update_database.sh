#!/bin/bash

# Переменные окружения
export POSTGRES_USER=dev
export POSTGRES_PASSWORD=root
export POSTGRES_DB=rovesnik
export POSTGRES_HOST=127.0.0.1
export POSTGRES_PORT=5432

echo "Dropping all tables in the database..."
alembic downgrade base

echo "Initializing a new migration..."
alembic revision --autogenerate -m 'init'

echo "Applying the migration..."
alembic upgrade heads

echo "Migration script executed successfully."
