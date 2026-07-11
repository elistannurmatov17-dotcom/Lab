#!/bin/bash

if [ "$EUID" -ne 0 ]; then
echo "pls write whis sudo"
exit 1
fi

echo "updating"
apt update && apt upgrade

echo "install packs"
apt install -y sudo curl ufw  openssh-server ansible docker.io docker-compose git htop bash-completion

echo "sshkey" #ssh key /etc/shh/
mkdir -p /etc/ssh/keys
if [ ! -f /etc/ssh/keys/id_ed25519 ]; then
ssh-keygen -t ed25519 -N "" -f /etc/ssh/keys/id_ed25519 -C "global-server"
echo "pubkey"
cat /etc/ssh/keys/id_ed25519.pub
echo "==================="
else
echo "common ssh key allready existed"
fi

echo "ufw"
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
echo "y" | ufw enable

echo "SETUP OK"
