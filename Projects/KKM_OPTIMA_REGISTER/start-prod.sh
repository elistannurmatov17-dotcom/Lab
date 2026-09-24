#!/usr/bin/env bash
set -euo pipefail
command -v docker >/dev/null 2>&1 || { echo 'Docker не установлен.'; exit 1; }
ENV_FILE=".env.production"
PUBLIC_DOMAIN="${1:-}"
ADMIN_DOMAIN="${2:-}"
if [[ -z "$PUBLIC_DOMAIN" || -z "$ADMIN_DOMAIN" ]]; then
  echo "Использование: ./start-prod.sh public.example.com admin.example.com"
  exit 2
fi
randhex() { python -c 'import secrets; print(secrets.token_hex(32))'; }
randpass() { python -c 'import secrets; print(secrets.token_urlsafe(20))'; }
fernet_key() { python -c 'import base64,secrets; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())'; }
if [[ ! -f "$ENV_FILE" ]]; then
  umask 077
  cat > "$ENV_FILE" <<ENV
PUBLIC_DOMAIN=$PUBLIC_DOMAIN
ADMIN_DOMAIN=$ADMIN_DOMAIN
POSTGRES_PASSWORD=$(randhex)
JWT_SECRET=$(randhex)
CREDENTIAL_ENCRYPTION_KEY=$(fernet_key)
MANAGER_1_USERNAME=manager1
MANAGER_1_PASSWORD=$(randpass)
MANAGER_2_USERNAME=manager2
MANAGER_2_PASSWORD=$(randpass)
MANAGER_3_USERNAME=manager3
MANAGER_3_PASSWORD=$(randpass)
ENV
  echo "Создан $ENV_FILE. Пароли менеджеров сохранены только в нём."
  echo "Сделай отдельную защищённую копию этого файла до первого запуска."
fi
if grep -q '^PUBLIC_DOMAIN=$' "$ENV_FILE" 2>/dev/null; then
  echo "В $ENV_FILE не настроен PUBLIC_DOMAIN"; exit 3
fi
chmod 600 "$ENV_FILE"
docker compose --env-file "$ENV_FILE" -f docker-compose.prod.yml config >/dev/null
docker compose --env-file "$ENV_FILE" -f docker-compose.prod.yml up -d --build
docker compose --env-file "$ENV_FILE" -f docker-compose.prod.yml ps
echo
echo "Public: https://$PUBLIC_DOMAIN"
echo "Admin:  https://$ADMIN_DOMAIN/"
echo "Backup: ./backup.sh"
