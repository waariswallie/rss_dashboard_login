#!/bin/bash
echo "🧹 Cleaning up previous Docker containers..."
docker compose down

echo "🚀 Building Docker container..."
docker compose build

echo "🔄 Starting Docker container..."
docker compose up -d

echo "✅ Setup complete."
