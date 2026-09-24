#!/usr/bin/env bash
set -euo pipefail
ENV_FILE="${ENV_FILE:-.env.production}"
[[ -f "$ENV_FILE" ]] || { echo "Нет $ENV_FILE"; exit 1; }
mkdir -p backups
chmod 700 backups
stamp="$(date '+%Y%m%d_%H%M%S')"
volume='kkm_optima_register_private_uploads'
docker volume inspect "$volume" >/dev/null 2>&1 || { echo "Не найден volume $volume. Подними production-стек хотя бы один раз."; exit 2; }
out="backups/documents_${stamp}.tar.gz"
docker run --rm -v "$volume:/data:ro" -v "$PWD/backups:/backup" alpine:3.22 tar -czf "/backup/documents_${stamp}.tar.gz" -C /data .
chmod 600 "$out"
find backups -type f -name 'documents_*.tar.gz' -mtime +14 -delete
echo "Создан: $out"
