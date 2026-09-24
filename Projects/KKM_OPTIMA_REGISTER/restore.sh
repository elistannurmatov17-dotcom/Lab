#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="${ENV_FILE:-.env.production}"
BACKUP_FILE="${1:-}"
[[ -f "$ENV_FILE" ]] || { echo "Нет $ENV_FILE"; exit 1; }
[[ -f "$BACKUP_FILE" ]] || { echo "Укажи зашифрованный backup .sql.gz.enc"; exit 2; }
command -v openssl >/dev/null 2>&1 || { echo "Нужен openssl на хосте"; exit 3; }
# shellcheck disable=SC1090
source "$ENV_FILE"
[[ -n "${BACKUP_PASSWORD:-}" ]] || { echo "В $ENV_FILE нет BACKUP_PASSWORD"; exit 4; }

echo "ВНИМАНИЕ: текущая база KKM будет заменена содержимым $BACKUP_FILE"
read -r -p 'Для продолжения введи RESTORE: ' answer
[[ "$answer" == "RESTORE" ]] || { echo 'Отмена'; exit 5; }

docker compose --env-file "$ENV_FILE" -f docker-compose.prod.yml stop backend caddy
trap 'docker compose --env-file "$ENV_FILE" -f docker-compose.prod.yml start backend caddy >/dev/null 2>&1 || true' EXIT

openssl enc -d -aes-256-cbc -pbkdf2 -pass env:BACKUP_PASSWORD -in "$BACKUP_FILE" |
  gzip -dc |
  docker compose --env-file "$ENV_FILE" -f docker-compose.prod.yml exec -T postgres psql -U kkm -d kkm

echo "Восстановление базы завершено."
