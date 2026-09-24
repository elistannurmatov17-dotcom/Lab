#!/usr/bin/env bash
set -euo pipefail

command -v docker >/dev/null 2>&1 || { echo 'Docker не установлен.'; exit 1; }

randhex() { python -c 'import secrets; print(secrets.token_hex(24))'; }
randpass() { python -c 'import secrets; print(secrets.token_urlsafe(16))'; }
fernet_key() { python -c 'import base64,secrets; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())'; }

if [[ ! -f .env ]]; then
  cat > .env <<ENV
POSTGRES_PASSWORD=$(randhex)
JWT_SECRET=$(randhex)
CREDENTIAL_ENCRYPTION_KEY=$(fernet_key)
ENVIRONMENT=development
MANAGER_1_USERNAME=manager1
MANAGER_1_PASSWORD=$(randpass)
MANAGER_2_USERNAME=manager2
MANAGER_2_PASSWORD=$(randpass)
MANAGER_3_USERNAME=manager3
MANAGER_3_PASSWORD=$(randpass)
ENV
  echo 'Создан .env с секретами и первичными паролями менеджеров.'
  echo 'Сохрани пароли менеджеров из .env в безопасном месте.'
fi

docker compose up -d --build
docker compose ps
