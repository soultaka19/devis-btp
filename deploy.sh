#!/bin/bash
# Point d'entree conserve pour compatibilite : la procedure de deploiement
# est dans deploy/deploy.sh (qui charge .env.prod via `docker compose --env-file`).
# L'ancienne version chargeait .env.prod avec `export $(... | xargs)`, ce qui
# supprimait les guillemets de CORS_ORIGINS et empechait l'API de demarrer.
exec bash "$(dirname "$0")/deploy/deploy.sh" "$@"
