#!/bin/bash
set -e

echo "=== Devis BTP — Deploiement Production ==="

# 1. Verifier que .env.prod existe
if [ ! -f .env.prod ]; then
    echo "ERREUR: Fichier .env.prod introuvable."
    echo "Copiez .env.prod.example en .env.prod et remplissez les valeurs."
    echo "  cp .env.prod.example .env.prod"
    exit 1
fi

# 2. Charger les variables
export $(grep -v '^#' .env.prod | xargs)

# 3. Build et lancement
echo "-> Build des images Docker..."
docker compose -f docker-compose.prod.yml build

echo "-> Demarrage des services..."
docker compose -f docker-compose.prod.yml up -d

echo "-> Attente du demarrage de la base..."
sleep 5

echo ""
echo "=== Deploiement termine ==="
echo "L'application est accessible sur : http://$(curl -s ifconfig.me)"
echo ""
echo "Commandes utiles :"
echo "  docker compose -f docker-compose.prod.yml logs -f        # Voir les logs"
echo "  docker compose -f docker-compose.prod.yml down            # Arreter"
echo "  docker compose -f docker-compose.prod.yml up -d --build   # Rebuild + restart"
