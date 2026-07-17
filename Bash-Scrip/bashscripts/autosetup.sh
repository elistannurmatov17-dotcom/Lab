#!/bin/bash
set -e

if [ "$EUID" -ne 0 ]; then
  echo "Please run this script with sudo!"
  exit 1
fi

echo "=== Updating system ==="
apt update && apt upgrade -y

echo "=== Installing packages ==="
apt install -y sudo curl ufw openssh-server ansible docker.io docker-compose git htop bash-completion

echo "=== Setting up SSH Key ==="
mkdir -p /etc/ssh/keys
chmod 700 /etc/ssh/keys

if [ ! -f /etc/ssh/keys/id_ed25519 ]; then
  ssh-keygen -t ed25519 -N "" -f /etc/ssh/keys/id_ed25519 -C "global-server"
  chmod 600 /etc/ssh/keys/id_ed25519
  echo "=========================================="
  echo "PUBLIC KEY GENERATED:"
  cat /etc/ssh/keys/id_ed25519.pub
  echo "=========================================="
else
  echo "Common SSH key already exists."
fi

echo "=== Configuring UFW ==="
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
echo "y" | ufw enable

echo "=== SETUP OK ==="
