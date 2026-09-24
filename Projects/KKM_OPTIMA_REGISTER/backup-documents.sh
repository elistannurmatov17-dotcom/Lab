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
out="backups/documents_${stamp}.tar.gz.enc"
tmp="${out}.tmp"
volume='kkm_optima_register_private_uploads'

docker volume inspect "$volume" >/dev/null 2>&1 || {
  echo "Не найден volume $volume. Подними production-стек хотя бы один раз."
  exit 4
}

trap 'rm -f "$tmp"' EXIT
docker run --rm -v "$volume:/data:ro" alpine:3.22 tar -czf - -C /data . |
  openssl enc -aes-256-cbc -pbkdf2 -salt -pass env:BACKUP_PASSWORD > "$tmp"

mv "$tmp" "$out"
chmod 600 "$out"
find backups -type f -name 'documents_*.tar.gz.enc' -mtime +14 -delete
echo "Создан зашифрованный backup документов: $out"
