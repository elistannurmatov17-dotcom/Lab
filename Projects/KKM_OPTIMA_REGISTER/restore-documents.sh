#!/usr/bin/env bash
set -euo pipefail
ENV_FILE="${ENV_FILE:-.env.production}"
BACKUP_FILE="${1:-}"
[[ -f "$ENV_FILE" ]] || { echo "Нет $ENV_FILE"; exit 1; }
[[ -f "$BACKUP_FILE" ]] || { echo "Укажи зашифрованный backup документов .tar.gz.enc"; exit 2; }
command -v openssl >/dev/null 2>&1 || { echo "Нужен openssl на хосте"; exit 3; }
# shellcheck disable=SC1090
source "$ENV_FILE"
[[ -n "${BACKUP_PASSWORD:-}" ]] || { echo "В $ENV_FILE нет BACKUP_PASSWORD"; exit 4; }
volume='kkm_optima_register_private_uploads'
docker volume inspect "$volume" >/dev/null 2>&1 || { echo "Не найден volume $volume"; exit 5; }
echo "ВНИМАНИЕ: приватный volume документов будет заменён содержимым $BACKUP_FILE"
read -r -p 'Для продолжения введи RESTORE-DOCUMENTS: ' answer
[[ "$answer" == "RESTORE-DOCUMENTS" ]] || { echo 'Отмена'; exit 6; }
restart=0
cleanup(){ if [[ "$restart" == "1" ]]; then docker compose --env-file "$ENV_FILE" -f docker-compose.prod.yml start backend caddy >/dev/null || true; fi; }
trap cleanup EXIT
docker compose --env-file "$ENV_FILE" -f docker-compose.prod.yml stop backend caddy
restart=1
openssl enc -d -aes-256-cbc -pbkdf2 -pass env:BACKUP_PASSWORD -in "$BACKUP_FILE" | docker run --rm -i -v "$volume:/data" alpine:3.22 sh -c 'find /data -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +; tar -xzf - -C /data'
echo "Восстановление документов завершено."
