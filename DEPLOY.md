# Deploiement Devis BTP

Guide de deploiement sur VPS Hetzner (Ubuntu/Debian).

## Pre-requis

- VPS avec Ubuntu 22.04+ ou Debian 12+
- Acces SSH (user avec sudo)
- Repo GitHub `soultaka19/devis-btp` accessible

## 1. Setup initial du VPS

```bash
ssh dev@46.225.215.223

# Telecharger et executer le script de setup
curl -fsSL https://raw.githubusercontent.com/soultaka19/devis-btp/main/deploy/setup.sh | bash

# Se re-connecter pour activer le groupe docker
exit
ssh dev@46.225.215.223
```

Ou manuellement :
```bash
# Installer Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Pare-feu
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

## 2. Cloner le repo

```bash
git clone https://github.com/soultaka19/devis-btp.git /opt/devis-btp
cd /opt/devis-btp
```

## 3. Configurer l'environnement

```bash
cp .env.prod.example .env.prod
nano .env.prod
```

Remplir les valeurs :
- `DB_PASSWORD` : mot de passe PostgreSQL (generer avec `openssl rand -hex 32`)
- `SECRET_KEY` : cle JWT (generer avec `openssl rand -hex 64`)
- `OPENAI_API_KEY` : cle API OpenAI
- `DOMAIN` : laisser `localhost` pour acces par IP, ou mettre votre domaine

## 4. Lancer l'application

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod up --build -d
```

## 5. Verifier

```bash
# Sante de l'API
curl http://localhost/api/health

# Logs
docker compose -f docker-compose.prod.yml logs -f

# Statut des services
docker compose -f docker-compose.prod.yml ps
```

## Mises a jour

```bash
cd /opt/devis-btp
bash deploy/deploy.sh
```

## Configurer HTTPS (quand le domaine est pret)

1. Pointer le DNS A vers l'IP du VPS : `46.225.215.223`
2. Modifier `.env.prod` : `DOMAIN=votre-domaine.fr`
3. Relancer :
```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d
```
Caddy obtient automatiquement un certificat Let's Encrypt.

## Commandes utiles

```bash
# Voir les logs d'un service
docker compose -f docker-compose.prod.yml logs api
docker compose -f docker-compose.prod.yml logs frontend

# Arreter tout
docker compose -f docker-compose.prod.yml down

# Rebuild un seul service
docker compose -f docker-compose.prod.yml up --build -d api

# Acces base de donnees
docker compose -f docker-compose.prod.yml exec db psql -U postgres devis_btp

# Sauvegarder la base
docker compose -f docker-compose.prod.yml exec db pg_dump -U postgres devis_btp > backup.sql
```

## Architecture de production

```
Internet → Caddy (:80/:443) → nginx/frontend (:80 interne) → API (:8000)
                                                                   ↓
                                                             PostgreSQL (:5432)
```

- **Caddy** : reverse proxy, HTTPS automatique via Let's Encrypt
- **Frontend** : nginx servant l'app Angular + proxy /api vers le backend
- **API** : FastAPI avec 2 workers uvicorn
- **DB** : PostgreSQL 16
