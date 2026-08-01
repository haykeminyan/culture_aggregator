#!/bin/bash
docker compose down
git pull
docker compose -f docker-compose.yaml -f docker-compose.prod.yaml up -d --build
docker image prune -af       # удаляем старые образы после билда
docker builder prune -af     # чистим build cache
