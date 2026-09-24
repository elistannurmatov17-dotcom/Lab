#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="${ENV_FILE:-.env.production}"
[[ -f "$ENV_FILE" ]] || { echo "Нет $ENV_FILE"; exit 1; }
command -v openssl >/dev/null 2>&1 || { echo "Нужен openssl на хосте"; exit 2; }
# shellcheck disable=SC1090
source "$ENV_FILE"
[[ -n "${BACKUP_PASSWORD:-}" ]] || { echo "В $ENV_FILE нет BACKUP_PASSWORD"; exit 3; }
mkdir -p backups
chmod 700 backups
stamp="$(date '+%Y%m%d_%H%M%S')"
out="backups/kkm_${stamp}.sql.gz.enc"
tmp="${out}.tmp"
trap 'rm -f "$tmp"' EXIT

docker compose --env-file "$ENV_FILE" -f docker-compose.prod.yml exec -T postgres pg_dump -U kkm -d kkm | gzip -9 | openssl enc -aes-256-cbc -pbkdf2 -salt -pass env:BACKUP_PASSWORD > "$tmp"
mv "$tmp" "$out"
chmod 600 "$out"
find backups -type f -name 'kkm_*.sql.gz.enc' -mtime +14 -delete

echo "Создан зашифрованный backup: $out"
echo 'Документы сохраняются отдельным зашифрованным архивом через ./backup-documents.sh'
