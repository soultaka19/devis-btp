#!/bin/bash
set -e

echo "=== Devis BTP — Mise a jour Production ==="

cd /opt/devis-btp

# 1. Pull latest code
echo "-> Pull du code..."
git pull origin main

# 2. Build and restart
echo "-> Build et redemarrage des services..."
docker compose -f docker-compose.prod.yml --env-file .env.prod up --build -d

# 3. Cleanup
echo "-> Nettoyage des images inutilisees..."
docker image prune -f

# 4. Health check
echo "-> Verification..."
sleep 10
if curl -sf http://localhost/api/health > /dev/null; then
    echo "   API OK"
else
    echo "   ATTENTION: API ne repond pas encore. Verifiez les logs:"
    echo "   docker compose -f docker-compose.prod.yml logs api"
fi

echo ""
echo "=== Mise a jour terminee ==="
