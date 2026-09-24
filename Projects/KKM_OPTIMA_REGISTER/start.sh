#!/usr/bin/env bash
set -euo pipefail

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Создан .env. Заполни секреты и пароли менеджеров, затем повтори запуск."
  exit 1
fi

docker compose up -d --build
docker compose ps
