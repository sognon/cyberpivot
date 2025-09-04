#!/bin/bash
set -e

APP_NAME="cyberpivot"
PORT=8501

echo "== 🚀 Build & Run $APP_NAME =="

# Supprime l'ancien conteneur s'il existe
if [ "$(docker ps -aq -f name=$APP_NAME)" ]; then
  echo "🛑 Suppression de l'ancien conteneur..."
  docker rm -f $APP_NAME || true
fi

# Build l'image
echo "🔨 Construction de l'image Docker..."
docker build -t $APP_NAME:latest .

# Lance le conteneur
echo "▶️ Lancement du conteneur..."
docker run -d \
  --name $APP_NAME \
  -p $PORT:8501 \
  -e CYBERPIVOT_DEV_MODE=1 \
  -v "$(pwd)/data:/app/data" \
  $APP_NAME:latest

echo "✅ Application lancée : http://localhost:$PORT"

