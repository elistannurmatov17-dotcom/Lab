#!/usr/bin/env bash
set -euo pipefail
ENV_FILE="${ENV_FILE:-.env.production}"
[[ -f "$ENV_FILE" ]] || { echo "Нет $ENV_FILE"; exit 1; }
mkdir -p backups
chmod 700 backups
stamp="$(date '+%Y%m%d_%H%M%S')"
out="backups/kkm_${stamp}.sql.gz"
docker compose --env-file "$ENV_FILE" -f docker-compose.prod.yml exec -T postgres pg_dump -U kkm -d kkm | gzip -9 > "$out"
chmod 600 "$out"
find backups -type f -name 'kkm_*.sql.gz' -mtime +14 -delete
echo "Создан: $out"
echo 'Не забудь отдельно выполнить ./backup-documents.sh для приватных документов.'
