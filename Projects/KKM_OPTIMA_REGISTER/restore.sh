#!/usr/bin/env bash
set -euo pipefail
ENV_FILE="${ENV_FILE:-.env.production}"
BACKUP_FILE="${1:-}"
[[ -f "$ENV_FILE" ]] || { echo "Нет $ENV_FILE"; exit 1; }
[[ -f "$BACKUP_FILE" ]] || { echo "Укажи backup .sql.gz"; exit 2; }
echo "ВНИМАНИЕ: текущая база KKM будет заменена содержимым $BACKUP_FILE"
read -r -p 'Для продолжения введи RESTORE: ' answer
[[ "$answer" == "RESTORE" ]] || { echo 'Отмена'; exit 3; }
docker compose --env-file "$ENV_FILE" -f docker-compose.prod.yml stop backend caddy
gzip -dc "$BACKUP_FILE" | docker compose --env-file "$ENV_FILE" -f docker-compose.prod.yml exec -T postgres psql -U kkm -d kkm
docker compose --env-file "$ENV_FILE" -f docker-compose.prod.yml start backend caddy
echo "Восстановление завершено."
