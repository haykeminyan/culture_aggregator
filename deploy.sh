#!/bin/bash
docker compose down
git pull
docker compose -f docker-compose.yaml -f docker-compose.prod.yaml up -d --build
docker image prune -f                         # удаляем только старые (dangling) образы, базовый python остаётся
docker builder prune -f --filter until=168h   # чистим build cache старше недели, свежий кэш pip/слоёв остаётся
