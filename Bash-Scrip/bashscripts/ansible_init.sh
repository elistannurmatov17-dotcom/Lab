#!/bin/bash
set -e

SSH_KEY="$HOME/.ssh/id_ed25519"

if [ ! -f "$SSH_KEY" ]; then
    echo "Ошибка: SSH-ключ не найден по пути $SSH_KEY"
    echo "Пожалуйста, сгенерируйте ключ командой 'ssh-keygen -t ed25519' или укажите правильный путь в скрипте."
    exit 1
fi

echo "=== Использование существующего ключа: $SSH_KEY ==="

echo -n "Введите IP-адрес удаленного сервера: "
read SERVER_IP

if [[ ! $SERVER_IP =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Ошибка: Неверный формат IP-адреса!"
    exit 1
fi

echo -n "Введите имя пользователя на сервере [по умолчанию: root]: "
read SSH_USER
SSH_USER=${SSH_USER:-root}

echo -n "Задайте имя сервера для Ansible (например: web-server, db-server): "
read ANSIBLE_HOST_NAME
if [ -z "$ANSIBLE_HOST_NAME" ]; then
    ANSIBLE_HOST_NAME="server_$SERVER_IP"
fi

echo "=== 1. Проверка связи с сервером $SERVER_IP ==="
if ! ping -c 1 -W 2 "$SERVER_IP" &> /dev/null; then
    echo "Внимание: Сервер не отвечает на ping, пробуем подключиться..."
fi

echo "=== 2. Отправка ключа на сервер ==="
ssh-copy-id -o StrictHostKeyChecking=accept-new -i "${SSH_KEY}.pub" "$SSH_USER@$SERVER_IP"

echo "=== 3. Проверка беспарольного доступа по SSH ==="
if ssh -i "$SSH_KEY" -o PasswordAuthentication=no -o ConnectTimeout=3 "$SSH_USER@$SERVER_IP" "echo 'Связь установлена!'" &> /dev/null; then
    echo "Успех! Беспарольный доступ работает отлично."
else
    echo "Ошибка: Не удалось войти по ключу. Проверьте пароль или настройки SSH удаленного сервера."
    exit 1
fi

echo "=== 4. Добавление сервера в инвентарь Ansible ==="
mkdir -p inventory

if [ ! -f "inventory/hosts.ini" ]; then
    echo "[managed_servers]" > inventory/hosts.ini
fi

if grep -q "$SERVER_IP" inventory/hosts.ini; then
    echo "Этот сервер ($SERVER_IP) уже есть в файле inventory/hosts.ini. Обновляем запись."
    sed -i "/$SERVER_IP/d" inventory/hosts.ini
fi

echo "$ANSIBLE_HOST_NAME ansible_host=$SERVER_IP ansible_user=$SSH_USER ansible_ssh_private_key_file=$SSH_KEY" >> inventory/hosts.ini

cat << EOF > ansible.cfg
[defaults]
inventory = ./inventory/hosts.ini
host_key_checking = False
stdout_callback = yaml
EOF

echo "=== НАСТРОЙКА ЗАВЕРШЕНА ==="
echo "Сервер '$ANSIBLE_HOST_NAME' успешно добавлен!"
echo "Вы можете запускать этот скрипт снова для добавления других серверов."
echo "Посмотреть текущий список серверов: cat inventory/hosts.ini"
