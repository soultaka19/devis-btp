# Template : Creer une App SaaS complete avec Claude Code

## De zero a une app de devis BTP fonctionnelle — pilotee a 100% par l'IA

> Ce template vous guide etape par etape pour recreer **Devis BTP**, une app SaaS qui genere des devis professionnels par commande vocale, en utilisant uniquement **Claude Code** comme copilote.

---

# PARTIE 1 — PRD (Product Requirements Document)

## 1.1 Vision produit

**Devis BTP** est un SaaS pour les artisans du batiment en France. L'artisan dicte ou tape une description de travaux en langage naturel, l'IA la transforme en lignes de devis structurees, et l'app genere un PDF professionnel envoyable par email.

**Probleme** : Les artisans perdent du temps a creer des devis manuellement sur Excel ou Word. Ils sont souvent sur chantier et n'ont pas le temps de s'asseoir pour rediger.

**Solution** : Dicter les travaux au telephone, l'IA fait le reste.

## 1.2 Personas

| Persona | Description |
|---------|-------------|
| **Artisan solo** | Plombier, electricien, peintre. Fait tout seul. Veut un devis en 2 minutes entre deux chantiers. |
| **Petit patron BTP** | 2-10 employes. Veut standardiser ses devis et suivre les stats. |

## 1.3 Fonctionnalites

### MVP (ce qu'on construit)

| # | Fonctionnalite | Description |
|---|----------------|-------------|
| F1 | **Auth** | Inscription/connexion par email + mot de passe, JWT |
| F2 | **Dictee vocale** | Micro dans le navigateur, transcription en texte |
| F3 | **Parsing IA** | Le texte est analyse par GPT-4o-mini qui extrait : lignes de devis, infos client, titre |
| F4 | **Editeur de devis** | Tableau editable : description, unite, quantite, prix unitaire, TVA |
| F5 | **Apercu temps reel** | Preview A4 du devis qui se met a jour en live |
| F6 | **Generation PDF** | PDF professionnel via WeasyPrint + template Jinja2 |
| F7 | **Envoi email** | Envoyer le devis PDF par email au client via Resend |
| F8 | **Commandes vocales** | "Telecharge le PDF", "Envoie le devis par mail" detectes automatiquement |
| F9 | **Dashboard** | Stats (total devis, ce mois, montant moyen, acceptes) + liste recente |
| F10 | **Parametres entreprise** | Infos, logo, RIB, assurance, CGV — injectes dans le PDF |
| F11 | **Layout configurable** | Sidebar ou toolbar, responsive mobile |

### Hors scope MVP
- Multi-utilisateurs / equipes
- Paiement en ligne (Stripe)
- Suivi de chantier
- Application mobile native

## 1.4 User Stories cles

```
En tant qu'artisan, je veux dicter "pose carrelage 30m2 a 35 euros pour M. Martin"
et obtenir un devis PDF professionnel en moins d'une minute.

En tant qu'artisan, je veux dire "envoie le devis par mail"
et que le client recoive le PDF en piece jointe.

En tant qu'artisan, je veux voir mes stats sur un dashboard
pour savoir combien de devis j'ai fait ce mois.
```

## 1.5 Modele de donnees

```
Users
  - id, email, password_hash, full_name, created_at

Quotes
  - id, user_id (FK), reference (auto: DEV-YYYYMM-XXXXXX)
  - status (draft | sent | accepted | rejected)
  - client_name, client_address, client_email, client_phone
  - title, description
  - subtotal_ht, total_vat, total_ttc (calcules)
  - created_at, updated_at

LineItems
  - id, quote_id (FK), position
  - description, unit (u, m2, m, h, kg, forfait)
  - quantity, unit_price, vat_rate (5.5 | 10 | 20)
  - total_ht (calcule)

CompanyInfo
  - id, user_id, name, siret, address, postal_code, city, phone, email, logo_url

Banking
  - id, user_id, bank_name, iban, bic

Insurance
  - id, user_id, provider, policy_number, coverage_zone

Terms
  - id, user_id, payment_terms, validity_days, late_penalty_rate, general_conditions
```

## 1.6 API Endpoints

```
POST   /auth/register
POST   /auth/login
POST   /auth/refresh

GET    /quotes              # Liste des devis
POST   /quotes              # Creer un devis
GET    /quotes/{id}         # Detail d'un devis
PUT    /quotes/{id}         # Modifier un devis
DELETE /quotes/{id}         # Supprimer un devis
POST   /quotes/{id}/duplicate
POST   /quotes/{id}/generate-pdf
POST   /quotes/{id}/send-email
POST   /quotes/parse-text   # IA : texte -> lignes de devis
POST   /quotes/voice-to-text

GET    /company             # Infos entreprise
PUT    /company             # Modifier infos
POST   /company/logo        # Upload logo
GET    /company/banking
PUT    /company/banking
GET    /company/insurance
PUT    /company/insurance
GET    /company/terms
PUT    /company/terms

GET    /dashboard/stats
GET    /dashboard/recent
GET    /health
```

---

# PARTIE 2 — Choix techniques

## 2.1 Stack

| Couche | Techno | Pourquoi |
|--------|--------|----------|
| **Frontend** | Angular 21 + Angular Material 21 | Framework robuste, Material pour le design system |
| **State** | Angular Signals | Plus simple que NgRx, natif Angular 21 |
| **Styles** | SCSS + CSS Custom Properties | Theming facile, responsive |
| **Backend** | FastAPI (Python) | Async natif, auto-doc OpenAPI, rapide |
| **ORM** | SQLAlchemy 2 (async) | Standard Python, support async |
| **BDD** | PostgreSQL 16 | Fiable, performant |
| **Migrations** | Alembic | Standard avec SQLAlchemy |
| **Auth** | JWT (HS256) | Simple, stateless |
| **IA** | OpenAI GPT-4o-mini | Bon rapport qualite/prix, function calling |
| **PDF** | WeasyPrint + Jinja2 | HTML -> PDF, templates flexibles |
| **Email** | Resend | API simple, delivrabilite, pas cher |
| **Infra** | Docker Compose | Dev local simple : PostgreSQL + API |

## 2.2 Architecture

```
devis-btp/
├── frontend/              # Angular 21
│   └── src/app/
│       ├── core/          # Auth, API service, guards, interceptors
│       └── features/      # Modules metier
│           ├── auth/      # Login, Register
│           ├── dashboard/ # Stats, liste recente
│           ├── quote/     # Compose, chat, editeur, preview, voice
│           └── company/   # Parametres entreprise
├── backend/               # FastAPI
│   └── app/
│       ├── core/          # Auth dependencies
│       ├── features/      # Modules metier (meme structure)
│       │   ├── auth/
│       │   ├── quote/     # AI parser, PDF, email, voice
│       │   ├── company/
│       │   └── dashboard/
│       └── templates/     # Templates PDF Jinja2
├── docker-compose.yml     # PostgreSQL + API
└── CLAUDE.md              # Instructions pour Claude Code
```

## 2.3 Conventions

- **UI** : Texte en francais, code en anglais
- **Backend** : Ruff linter, line length 100, Python 3.11+
- **Frontend** : Prettier, single quotes, 100 chars
- **Composants** : Inline templates/styles (Angular standalone)
- **Theme** : Bleu marine (#1B2A4A) + Or (#D4920B), coins arrondis, ombres douces

---

# PARTIE 3 — Prompts Claude Code (etape par etape)

> **Pre-requis** : Avoir Claude Code installe (`npm install -g @anthropic-ai/claude-code`)
> Creer un dossier vide, y entrer, lancer `claude`

---

## ETAPE 0 — Initialisation du projet

### Prompt 0.1 : Structure + Docker + Backend de base

```
Cree un projet "Devis BTP" avec cette structure :
- frontend/ : Angular 21 (cree avec @angular/cli, standalone components, SCSS)
- backend/ : FastAPI avec SQLAlchemy 2 async + PostgreSQL
- docker-compose.yml : PostgreSQL 16 + API backend

Backend :
- pyproject.toml avec : fastapi, uvicorn, sqlalchemy[asyncio], asyncpg, alembic, pydantic-settings, python-jose, passlib[bcrypt], python-multipart, openai, weasyprint, jinja2, resend
- Structure backend/app/ avec : main.py, config.py (pydantic-settings, toutes les vars d'env), database.py (async engine + session)
- Initialise Alembic avec le bon database URL async

Frontend :
- Ajoute Angular Material 21 et configure le theme
- Cree un fichier environments/environment.ts avec apiUrl: http://localhost:8000

Cree un CLAUDE.md a la racine decrivant l'architecture du projet pour guider les prochaines sessions.
```

### Prompt 0.2 : Theme et design system

```
Configure le design system dans frontend/src/styles.scss :
- Font : Inter (Google Fonts)
- CSS Custom Properties :
  - --primary: #1B2A4A (bleu marine)
  - --primary-light: #2D4A7A
  - --accent: #D4920B (or)
  - --accent-light: #F5C842
  - --surface: #F8F9FA
  - --danger: #C0392B
  - --success: #1B7A3D
  - --warning: #E67E22
  - --text-primary: #1A1A2E
  - --text-secondary: #6B7280
  - --border: #E5E7EB
  - --radius-sm/md/lg: 6/10/16px
  - --shadow-sm/md/lg/xl
  - --transition: 0.2s cubic-bezier(0.4, 0, 0.2, 1)
- Breakpoints : mobile (<768px), tablet (768px+), desktop (1024px+)
- Reset de base + scrollbar custom
- Classes utilitaires pour les boutons (.btn-primary avec le gradient accent)
```

---

## ETAPE 1 — Authentification

### Prompt 1.1 : Backend auth

```
Cree le module auth dans backend/app/features/auth/ :
- models.py : modele User (id, email, password_hash, full_name, created_at)
- schemas.py : RegisterRequest, LoginRequest, TokenResponse, UserResponse
- service.py : register_user, authenticate_user, create_tokens (access 30min + refresh 7j)
- router.py : POST /register, POST /login, POST /refresh
- Monte le router sur /auth dans main.py

Dans backend/app/core/dependencies.py :
- get_current_user : decode le JWT Bearer token et retourne le User

Configure CORS dans main.py pour autoriser http://localhost:4200.
Cree la migration Alembic pour la table users.
```

### Prompt 1.2 : Frontend auth

```
Cree le module auth dans frontend/src/app/features/auth/ :
- models/auth.model.ts : interfaces LoginRequest, RegisterRequest, TokenResponse, User
- services/auth.service.ts : login(), register(), logout(), refreshToken(), isLoggedIn()
  - Stocke access_token et refresh_token dans localStorage
- state/auth.store.ts : store Angular Signals (user, loading, error)

Dans core/ :
- api/api.service.ts : wrapper HttpClient avec baseUrl, methodes get/post/put/delete/upload/postBlob
- auth/auth.interceptor.ts : injecte Bearer token, intercepte 401 -> refresh ou logout
- auth/auth.guard.ts : canActivate qui redirige vers /auth/login si pas connecte

Pages :
- auth/components/login/ : formulaire email + mot de passe, bouton "Se connecter", lien vers register
- auth/components/register/ : formulaire full_name + email + password + confirm, bouton "S'inscrire"
- Design : carte centree, logo "Devis BTP" avec icone construction, fond surface

Routes : /auth/login, /auth/register. Redirect / -> /dashboard.
Toutes les routes sauf /auth/* protegees par authGuard.
```

---

## ETAPE 2 — Layout et navigation

### Prompt 2.1 : App layout

```
Cree le layout principal dans app.ts / app.html / app.scss :

Layout systeme configurable avec 2 modes (persiste dans localStorage) :
- Mode "sidebar" (defaut) : sidebar bleu marine a gauche (260px, collapsible a 68px)
  - Header : icone construction + "Devis BTP"
  - Nav links : Dashboard (icone dashboard), Nouveau Devis (icone add_circle), Entreprise (icone business)
  - Footer : avatar user (cercle gradient), nom+email, bouton settings (toggle layout), bouton logout
  - Lien actif : fond clair + icone or
- Mode "toolbar" : barre horizontale en haut, memes liens

Mobile (<768px) : force le mode toolbar avec menu hamburger.

Utilise mat-sidenav-container d'Angular Material.
Les signals layoutMode et sidebarCollapsed sont persistees dans localStorage (cles: btp_layout_mode, btp_sidebar_collapsed).
```

---

## ETAPE 3 — Module Devis (coeur de l'app)

### Prompt 3.1 : Backend devis — Modeles et CRUD

```
Cree le module quote dans backend/app/features/quote/ :

models.py :
- QuoteStatus enum : draft, sent, accepted, rejected
- Quote : id, user_id, reference (auto-gen DEV-YYYYMM-XXXXXX), status, client_name, client_address, client_email, client_phone, title, description, subtotal_ht, total_vat, total_ttc, created_at, updated_at
- LineItem : id, quote_id, position, description, unit (u/m2/m/h/kg/forfait), quantity, unit_price, vat_rate, total_ht
- Relation Quote -> LineItems (cascade delete, order by position)

schemas.py : LineItemCreate, LineItemResponse, QuoteCreate, QuoteUpdate, QuoteResponse, QuoteListResponse

calculator.py : calc_line_total(qty, price, vat) et calc_quote_totals(lines) -> {subtotal_ht, total_vat, total_ttc}

service.py : create_quote, get_quote, list_quotes, update_quote, delete_quote, duplicate_quote
- create/update recalculent les totaux automatiquement
- update remplace toutes les line items (delete + recreate)

router.py : tous les endpoints CRUD, monte sur /quotes dans main.py.
Cree la migration Alembic pour quotes + line_items.
```

### Prompt 3.2 : Backend — Parser IA

```
Cree backend/app/features/quote/ai_parser.py :

Fonction parse_text_to_line_items(text) qui utilise OpenAI GPT-4o-mini avec function calling :
- System prompt : expert extraction devis BTP francais
- Extraire : title (titre court du devis), line_items (description, unit, quantity, unit_price, vat_rate), client (name, address, email, phone)
- Regles : TVA 10% renovation / 20% neuf, unites auto (m2, m, h, forfait...), separer fourniture et main d'oeuvre
- IMPORTANT : si le texte contient une adresse email (@), l'extraire dans client.email
- Temperature 0.1 pour la coherence
- Retourne {title, line_items, client}

Schemas : ParseTextRequest(text), ParseTextResponse(title, line_items, client)
Endpoint : POST /quotes/parse-text
```

### Prompt 3.3 : Backend — Transcription vocale

```
Cree backend/app/features/quote/voice_service.py :
- Fonction transcribe_audio(audio_data, filename) qui utilise l'API OpenAI Whisper
- Retourne {text, duration_ms}

Schema : VoiceToTextResponse(text, duration_ms)
Endpoint : POST /quotes/voice-to-text (recoit un UploadFile)
```

### Prompt 3.4 : Frontend — Page de composition du devis

```
Cree la page de composition du devis (quote/components/compose/) :

Layout deux colonnes (responsive, empile sur mobile) :

COLONNE GAUCHE :
1. Panneau de saisie (quote-input-panel) :
   - Header "Description des travaux" avec icone edit_note
   - Zone de chat : historique des messages user (bleu, droite) et IA (gris, gauche)
   - Message IA avec resume + bouton "Voir detail" qui expand la liste des lignes parsees
   - Animation "Analyse en cours..." avec dots pendant le parsing
   - Barre de saisie en bas : bouton micro + input texte + bouton envoyer (rond)
   - Animations fadeIn sur les messages

2. Editeur de lignes (line-items-editor) :
   - Tableau avec colonnes : Description, Unite (dropdown), Qte (input), P.U. HT (input), TVA (dropdown 5.5/10/20%), Total HT (calcule), bouton supprimer
   - Header bleu, lignes alternees
   - Bouton "+ Ajouter une ligne" (bordure dashed)
   - Animation slideIn quand les lignes apparaissent progressivement (150ms entre chaque)

3. Barre d'actions (sticky bottom) :
   - Bouton "Telecharger PDF"
   - Bouton "Envoyer par Email"
   - Bouton "Sauvegarder" (primary)

COLONNE DROITE :
- Apercu A4 du devis (quote-preview) :
  - Header bleu marine "DEVIS" + reference
  - Section client (fond clair, bordure gauche accent)
  - Titre du devis
  - Tableau des lignes (header or/ambre)
  - Encadre totaux : Total HT, TVA, Total TTC (fond bleu, texte blanc)
  - Pied de page CGV
  - Se met a jour en temps reel

Routes : /quote/new et /quote/:id
```

### Prompt 3.5 : Frontend — Store du devis

```
Cree le store du devis (quote/state/quote.store.ts) avec Angular Signals :

Signals :
- draftQuote (Partial<Quote>), lineItems, chatMessages, quotes, currentQuote, loading, parsingStatus, error

Computed :
- totals : calcule subtotal_ht, total_vat, total_ttc depuis lineItems

Methodes :
- loadQuotes(), loadQuote(id)
- parseText(text) : detecte les commandes (PDF, email) OU envoie au backend pour parsing IA
  - Ajoute le texte user dans le chat, puis la reponse IA
  - Applique le titre et les infos client automatiquement
  - Ajoute les lignes progressivement (animation cascade 150ms)
- downloadPdf() : sauvegarde le devis si pas d'id, puis telecharge le PDF
- sendEmail() : verifie client_email, sauvegarde si besoin, envoie via API
- saveQuote() : cree ou met a jour, avec messages chat de feedback
- resetDraft()
- addLineItem, updateLineItem, removeLineItem, updateDraftField

Detection commandes vocales :
- isPdfCommand(text) : detecte "pdf" + action (telecharge/genere/exporte) + cible (devis/document)
- isEmailCommand(text) : detecte action (envoie/envoyer/transmet) + (email/mail OU devis/document)
  - IMPORTANT : "email" seul ne suffit pas, il faut un verbe d'action pour eviter les faux positifs
```

### Prompt 3.6 : Frontend — Bouton vocal

```
Cree le composant voice-input-button (quote/components/voice/) :

Deux variantes : standalone (gros bouton) et inline (petit, dans la barre de chat)

Fonctionnement :
- Utilise Web Speech API (SpeechRecognition, lang: fr-FR) en priorite
- Fallback : MediaRecorder + envoi au backend /quotes/voice-to-text
- Emet le texte transcrit via Output

Animations visuelles :
- Au repos : bouton rond avec icone micro, fond gradient or
- En enregistrement :
  - Bouton passe en rouge (danger) avec animation pulse
  - 3 anneaux concentriques qui s'expandent (wave-expand keyframe, staggered delays)
  - Label "Enregistrement..." clignotant
```

---

## ETAPE 4 — PDF

### Prompt 4.1 : Backend PDF

```
Cree le generateur PDF dans backend/app/features/quote/pdf_generator.py :
- generate_pdf_bytes(db, user_id, quote_id) -> bytes : charge devis + company + banking + insurance + terms, rend le template Jinja2, genere le PDF via WeasyPrint
- generate_quote_pdf() : appelle generate_pdf_bytes() et retourne un StreamingResponse

Cree le template backend/app/templates/quote_pdf.html :
- Template Jinja2 HTML/CSS stylise pour rendu PDF A4
- Header avec logo entreprise + infos entreprise
- Infos client
- Tableau des lignes avec totaux
- Pied de page : RIB, assurance, CGV
- Endpoint : POST /quotes/{id}/generate-pdf
```

---

## ETAPE 5 — Email

### Prompt 5.1 : Envoi email

```
Cree backend/app/features/quote/email_service.py :
- send_quote_email(db, user_id, quote_id, recipient_email?) :
  1. Charge le devis et les infos entreprise
  2. Verifie qu'il y a un email destinataire (parametre ou client_email du devis)
  3. Genere le PDF en bytes via generate_pdf_bytes()
  4. Envoie via resend.Emails.send() avec le PDF en piece jointe (base64)
  5. Met a jour le statut du devis en "sent"

Config : ajouter RESEND_FROM_EMAIL dans config.py
Schemas : SendEmailRequest(recipient_email?), SendEmailResponse(message)
Endpoint : POST /quotes/{id}/send-email

Frontend : ajouter sendEmail(id, email?) dans quote-api.service.ts
```

---

## ETAPE 6 — Dashboard

### Prompt 6.1 : Dashboard complet

```
Cree le module dashboard :

Backend (features/dashboard/) :
- service.py : get_stats(db, user_id) -> {total_quotes, monthly_quotes, average_value, accepted_quotes}, get_recent_quotes(db, user_id, limit=5)
- router.py : GET /dashboard/stats, GET /dashboard/recent

Frontend (features/dashboard/) :
- dashboard-home.component.ts :
  - Greeting "Bonjour, {nom}" + date du jour en francais
  - 4 cartes stats en grid responsive :
    - Total devis (icone description, bordure bleue)
    - Ce mois (icone calendar_month, bordure or)
    - Montant moyen (icone euro, bordure verte)
    - Devis acceptes (icone check_circle, bordure orange)
  - Effet hover : carte monte de 2px avec ombre
  - Liste des devis recents : reference (bleu), client, titre, badge statut colore, montant, chevron
  - Etat vide : icone + message + bouton "Creer votre premier devis"
  - Bouton "Nouveau Devis" en haut a droite
```

---

## ETAPE 7 — Parametres entreprise

### Prompt 7.1 : Module entreprise

```
Cree le module company :

Backend (features/company/) :
- models.py : CompanyInfo, Banking, Insurance, Terms (tous lies a user_id)
- service.py : get/update pour chaque entite + upload_logo (stockage local ou S3)
- router.py : endpoints REST pour chaque entite

Frontend (features/company/) :
- company-settings.component.ts : page avec 4 onglets Material Tabs :
  1. Informations : nom, SIRET (14 chiffres, valide), adresse, CP, ville, tel, email + upload logo drag-and-drop
  2. Bancaire : banque, IBAN, BIC
  3. Assurance : assureur, numero police, zone de couverture
  4. Conditions : delai paiement, validite devis (jours), penalites retard (%), CGV (textarea)
- Chaque tab : formulaire reactif avec validation, bouton sauvegarder, barre de progression, message erreur
```

---

## ETAPE 8 — Polish et finalisation

### Prompt 8.1 : CLAUDE.md final

```
Mets a jour le CLAUDE.md a la racine du projet pour documenter :
- Vue d'ensemble du projet
- Architecture (monorepo, stacks frontend/backend)
- Commandes courantes (npm start, uvicorn, pytest, docker-compose)
- Architecture frontend (Signals, layout system, feature modules pattern, key files)
- Architecture backend (feature modules pattern, API routes, AI parsing, config)
- Base de donnees (modeles, migrations, credentials dev)
- Conventions de style (SCSS, Ruff, langue UI vs code)
```

---

# PARTIE 4 — Checklist de verification

Avant de considerer le projet termine, verifiez :

```
[ ] docker-compose up demarre PostgreSQL + API sans erreur
[ ] npm start demarre le frontend sur :4200
[ ] Inscription + connexion fonctionnent
[ ] Creer un nouveau devis : dicter ou taper du texte
[ ] L'IA extrait les lignes, le titre, les infos client
[ ] L'apercu A4 se met a jour en temps reel
[ ] Modifier une ligne -> les totaux se recalculent
[ ] Telecharger le PDF -> fichier propre avec toutes les infos
[ ] Envoyer par email -> le client recoit le PDF
[ ] Dashboard affiche les stats et la liste des devis
[ ] Parametres entreprise : toutes les infos se sauvegardent
[ ] Responsive : l'app fonctionne sur mobile
[ ] Commande vocale : "envoie le devis par mail" fonctionne
```

---

# PARTIE 5 — Variables d'environnement

Creez un fichier `backend/.env` :

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/devis_btp
SECRET_KEY=votre-cle-secrete-ici
OPENAI_API_KEY=sk-votre-cle-openai
RESEND_API_KEY=re_votre-cle-resend
RESEND_FROM_EMAIL=devis@votre-domaine.com
```

---

# PARTIE 6 — Conseils pour reussir avec Claude Code

1. **Un prompt = une etape.** Ne demandez pas tout d'un coup. Suivez l'ordre.
2. **Testez apres chaque etape.** Lancez le serveur, verifiez que ca marche avant de passer a la suite.
3. **Utilisez le CLAUDE.md.** Il sert de memoire a Claude Code entre les sessions.
4. **Si ca plante** : copiez l'erreur et collez-la a Claude Code avec "corrige cette erreur".
5. **Commitez souvent.** Apres chaque etape qui marche, faites un commit.

---

> **Temps estime** : 2-4 heures pour tout construire avec Claude Code.
> **Resultat** : Une app SaaS complete, fonctionnelle, deployable.

---

*Cree avec Claude Code — programmation pilotee par l'IA*
