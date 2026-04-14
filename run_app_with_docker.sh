#!/usr/bin/env bash

# This script is used to run the FastAPI application using Docker

# check if .env file exists
if [ ! -f .env ]; then
  echo ".env file not found!"
  exit 1
fi

# Load environment variables from .env file
source .env

# Check if Docker is installed
if ! [ -x "$(command -v docker)" ]; then
  echo 'Error: Docker is not installed.' >&2
  exit 1
fi

# Check if Docker Compose is installed
if ! [ -x "$(command -v docker-compose)" ]; then
  echo 'Error: Docker Compose is not installed.' >&2
  exit 1
fi

# Normalize PROJECT_ENV (lowercase, default to dev if not set)
PROJECT_ENV_LOWER="${PROJECT_ENV,,}"
PROJECT_ENV_LOWER="${PROJECT_ENV_LOWER:-dev}"

echo "Environment: $PROJECT_ENV"

# Build and run the Docker image
sudo docker compose -f docker-compose.yml -f docker-compose."$PROJECT_ENV_LOWER".yml up --build -d
