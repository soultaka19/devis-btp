#!/bin/bash
set -e

echo "=== Devis BTP — Setup VPS ==="

# 1. Update system
echo "-> Mise a jour du systeme..."
sudo apt-get update && sudo apt-get upgrade -y

# 2. Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "-> Installation de Docker..."
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
    echo "   Docker installe. Re-login necessaire pour les permissions."
else
    echo "-> Docker deja installe."
fi

# 3. Install Docker Compose plugin if not present
if ! docker compose version &> /dev/null; then
    echo "-> Installation du plugin Docker Compose..."
    sudo apt-get install -y docker-compose-plugin
else
    echo "-> Docker Compose deja installe."
fi

# 4. Firewall
echo "-> Configuration du pare-feu (ufw)..."
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# 5. Create app directory
echo "-> Creation du repertoire /opt/devis-btp..."
sudo mkdir -p /opt/devis-btp
sudo chown $USER:$USER /opt/devis-btp

echo ""
echo "=== Setup termine ==="
echo "Prochaine etape : cloner le repo et configurer .env.prod"
echo "  git clone https://github.com/soultaka19/devis-btp.git /opt/devis-btp"
