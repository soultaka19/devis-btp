# Déploiement du front sur Vercel

Le front Angular est servi par Vercel, l'API tourne sur le VPS. La configuration
tient dans `frontend/vercel.json` — ce document explique les choix, puisque JSON
n'admet pas de commentaires.

## Réglages du projet Vercel

| Réglage | Valeur |
|---|---|
| Repository | `soultaka19/devis-btp` |
| Production Branch | `main` |
| **Root Directory** | **`frontend`** |
| Framework Preset | Angular (détection automatique) |
| Build Command | forcé par `vercel.json` (`npm run build`) — voir ci-dessous |
| Install Command | *laisser vide* |
| Output Directory | fourni par `vercel.json` (`dist/frontend/browser`) |
| Domaine | `devis-btp.soultaka.com` |

## Pourquoi `buildCommand` est écrit noir sur blanc

Le tableau de bord du projet portait `cd frontend && npm ci && npm run build`.
Le Root Directory valant déjà `frontend`, ce `cd` échouait :
`sh: line 1: cd: frontend: No such file or directory`.

Ce réglage vit **dans le projet Vercel**, pas dans le dépôt : déplacer ou vider
le `vercel.json` ne l'atteint pas. Deux déploiements ont échoué sur cette même
ligne pour cette raison.

`vercel.json` a la priorité sur les réglages du projet. Déclarer
`"buildCommand": "npm run build"` écrase donc la valeur du tableau de bord
depuis le dépôt, sans dépendre d'un accès à l'interface. **Ne pas retirer ce
champ** tant que le tableau de bord n'a pas été vidé à la main : l'omission
laisse simplement le réglage cassé reprendre la main.

Angular 17+ écrit dans `dist/<projet>/browser`, pas `dist/<projet>` — d'où le
`outputDirectory` explicite, que la détection automatique ne devine pas toujours.

## Pourquoi une réécriture `/api` plutôt que du CORS

`environment.prod.ts` appelle `/api`, un chemin relatif. La réécriture Vercel
envoie ces requêtes vers `https://devis-btp-api.soultaka.com` **sans que le
navigateur voie un changement d'origine**.

Conséquence : pas de configuration CORS à maintenir, et surtout pas de requête
`OPTIONS` de préflight avant chaque POST, PUT et DELETE. Le VPS étant à
Nuremberg (~130 ms d'Ottawa), ce préflight ajouterait un aller-retour
transatlantique complet avant même l'envoi de la donnée.

## Pourquoi le WebSocket ne passe pas par là

Vercel ne proxifie pas les upgrades WebSocket. `environment.prod.ts` vise donc
`wss://devis-btp-api.soultaka.com/ws` en direct.

Cette URL est **absolue à dessein** : `new WebSocket()` refuse un chemin relatif.
La configuration de production portait `/ws`, ce qui ne pouvait pas fonctionner —
le mode développement le masquait avec `ws://localhost:8000/ws`.

L'authentification voyage dans un paramètre `token` de la requête, jamais dans un
cookie : la poignée de main inter-origines n'a donc rien à demander à CORS.

## Le repli SPA

Vercel sert les fichiers existants **avant** d'appliquer les réécritures. La
règle attrape-tout `/(.*)` → `/index.html` ne capture donc jamais les bundles ni
les assets, seulement les routes Angular.
