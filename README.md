# Devis BTP

## Overview

Devis BTP is a SaaS web application that lets French building contractors (artisans du BTP)
produce a professional quote ("devis") from a plain-language description of the work, typed or
dictated. The description is turned into structured line items by an LLM, totals and VAT are
computed server-side, and the quote is rendered as a branded PDF that can be downloaded or
emailed to the client.

The repository is a monorepo: an Angular 21 single-page application (`frontend/`) and a FastAPI
API (`backend/`) backed by PostgreSQL 16, with Docker Compose files and deployment scripts for a
single-VPS production setup.

## Problem

Small contractors spend 20 to 40 minutes per quote: notes taken on site are re-typed in the
evening, VAT and totals are computed by hand, legal mentions are copied from a previous document,
then exported to PDF and emailed. The process is slow, error-prone and delays the quote, which
costs deals.

## Solution

A single screen where the contractor describes the job ("pose de carrelage 20 m² à 45 euros,
client M. Martin, 12 rue des Lilas...") by voice or text. The API sends the text to GPT-4o-mini
with a function-calling schema tuned for French construction vocabulary and returns clean line
items (description, unit, quantity, unit price, VAT rate) plus the client details it found. The
contractor adjusts the lines in a table, sees the live preview, and downloads or emails the PDF,
which carries the company's logo, SIRET, bank details, decennial insurance and payment terms.

## Key Features

- Email/password accounts with JWT access and refresh tokens.
- Chat-like quote composer: text input, or voice dictation through the browser's Web Speech API
  with a server-side Whisper transcription endpoint as fallback.
- AI extraction of line items and client information (OpenAI GPT-4o-mini, function calling), with
  server-side sanitisation of the model output (quantities, prices, VAT rates, units).
- Editable line items (units, quantities, unit prices, 5.5 / 10 / 20 % VAT) with totals computed
  per line and per VAT rate.
- Company profile: identity (SIRET validation), logo upload (validated as PNG/JPEG/WEBP), bank
  details (IBAN normalisation), decennial insurance and payment terms.
- PDF generation with WeasyPrint from a Jinja2 template (logo embedded, VAT breakdown, legal
  footer), download or email with the PDF attached (Resend).
- Dashboard: number of quotes, quotes this month, average value, status breakdown, recent quotes.
- French/English interface (ngx-translate) and API messages (`Accept-Language`), sidebar or
  toolbar layout persisted per browser, responsive down to mobile.
- Docker Compose production stack (Caddy with automatic HTTPS → nginx → API → PostgreSQL).

## My Role

Full-stack developer of the project: product definition (PRD), data model, FastAPI backend,
Angular frontend, PDF template, OpenAI integration and the Docker/VPS deployment.

## Architecture

```
Browser (Angular 21, Signals stores)
   │  HTTPS
   ▼
Caddy (:80/:443, Let's Encrypt)
   ▼
nginx (frontend container): static SPA, /api/* → API (prefix stripped), /ws/* → API (WebSocket)
   ▼
FastAPI (uvicorn) ── OpenAI (chat completions + Whisper)
   │                ── Resend (email)
   │                ── WeasyPrint (PDF)
   ▼
PostgreSQL 16 (SQLAlchemy 2 async + asyncpg)
```

Backend feature modules (`backend/app/features/<name>/`) each contain `models.py`, `schemas.py`,
`service.py` and `router.py`; cross-cutting code lives in `backend/app/core/` (JWT, storage,
i18n, error envelope `{detail, code}`). Frontend features (`frontend/src/app/features/<name>/`)
follow the same split with `components/`, `models/`, `services/` and a signal-based `state/`
store.

Tables: `users`, `companies`, `banking`, `insurances`, `terms`, `quotes`, `line_items`. The
schema is created by `Base.metadata.create_all` at API startup; Alembic is configured but no
migration has been generated yet.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Angular 21, Angular Material 21, Angular Signals, ngx-translate, SCSS, Vitest |
| Backend | Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2 (async), asyncpg, Alembic |
| Auth | JWT HS256 (python-jose), bcrypt |
| AI | OpenAI `gpt-4o-mini` (function calling), `whisper-1` |
| PDF / email | WeasyPrint + Jinja2, Resend |
| Database | PostgreSQL 16 |
| Ops | Docker, Docker Compose, nginx, Caddy, ruff, pytest, httpx |

## Technical Highlights

- **Constrained LLM output**: the extraction uses a function-calling tool whose JSON schema
  encodes the domain (allowed units, VAT rates, nullable client fields) and a French system prompt
  with trade heuristics (tiling and painting in m², cabling in m, supply vs labour). Because the
  API does not enforce the schema, the output is sanitised before it reaches the client.
- **Money arithmetic**: line totals and VAT are rounded per line, then aggregated per VAT rate
  (`calculator.py`), which is what the PDF prints.
- **Error envelope and i18n**: business errors are raised as `AppException` and serialised as
  `{detail, code}`; OpenAI failures map to `503 AI_UNAVAILABLE` / `502 AI_ERROR` instead of a
  generic 500, in the language requested by the client.
- **Production hardening**: `APP_ENV=production` refuses an empty, short or placeholder
  `SECRET_KEY` at startup; Compose requires `DB_PASSWORD` and `SECRET_KEY`; the API has a Docker
  healthcheck and the frontend waits for it.
- **Input validation mirrors the database**: Pydantic schemas carry the `String(n)` limits,
  numeric bounds (quantity > 0, price ≥ 0, VAT ∈ {5.5, 10, 20}) and pagination bounds, so bad
  input returns 422 rather than a database error.
- **Uploads**: logos are validated with Pillow (real image, allowed format) and stored with an
  extension derived from the detected format; they are served under `/uploads` and embedded in
  the PDF as a `data:` URI so WeasyPrint never fetches a URL.

## Challenges & Solutions

- **LLM hallucinated values** (negative quantities, 33 % VAT, unknown units): a sanitisation step
  coerces values to the domain (quantity defaults to 1, price to 0, nearest legal VAT rate,
  fallback unit) and drops malformed client emails.
- **Upstream outages turned into 500s**: OpenAI calls now have a 30 s timeout and a single retry,
  and every client exception is mapped to a clear, translated 502/503 response.
- **Logo never rendered**: the stored path was relative to the storage folder, so neither the
  SPA nor WeasyPrint could load it. The API now serves `/uploads`, the SPA builds the URL from
  `environment.apiUrl`, nginx gives the `/api/` prefix priority over its static-asset regex, and
  the PDF embeds the image inline.
- **WebSocket channel without ownership check**: any authenticated user could join any quote's
  channel; the endpoint now verifies the quote belongs to the token's user and closes with code
  4003 otherwise. (The real-time channel is implemented server-side but not yet wired in the UI.)

## Installation

Prerequisites: Node.js 22, Python 3.11+, PostgreSQL 16, and the WeasyPrint system libraries
(Debian/Ubuntu: `libpango-1.0-0 libpangoft2-1.0-0 libpangocairo-1.0-0 libcairo2
libgdk-pixbuf-2.0-0 libffi-dev shared-mime-info fonts-dejavu`).

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env            # edit DATABASE_URL, SECRET_KEY, OPENAI_API_KEY
createdb devis_btp              # or any database matching DATABASE_URL

# Frontend
cd ../frontend
npm ci
```

With Docker instead: `docker compose up` starts PostgreSQL and the API (ports 5432 and 8000);
run the frontend with `npm start`.

## Environment Variables

Backend (`backend/.env`, see `backend/.env.example`):

| Variable | Description |
|---|---|
| `APP_ENV` | `development` (default) or `production`; production refuses a weak `SECRET_KEY` |
| `DATABASE_URL` | `postgresql+asyncpg://user:password@host:5432/devis_btp` |
| `SECRET_KEY` | JWT signing key, at least 32 characters (`openssl rand -hex 32`) |
| `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS` | JWT settings (HS256, 30 min, 7 days) |
| `OPENAI_API_KEY` | OpenAI key used for text parsing and Whisper transcription |
| `STORAGE_LOCAL_PATH` | Folder for uploaded logos, served under `/uploads` (default `./uploads`) |
| `RESEND_API_KEY`, `RESEND_FROM_EMAIL` | Email sending (optional; sending fails cleanly without a key) |
| `CORS_ORIGINS` | JSON array of allowed origins, e.g. `["http://localhost:4200"]` |

Production (`.env.prod`, see `.env.prod.example`): `DB_PASSWORD`, `SECRET_KEY` (both required by
Compose), `OPENAI_API_KEY`, `RESEND_API_KEY`, `RESEND_FROM_EMAIL`, `DOMAIN`, `CORS_ORIGINS`.

Frontend: `src/environments/environment.ts` targets `http://localhost:8000` in development;
the production build uses relative `/api` and `/ws` URLs proxied by nginx.

## Running the Project

```bash
# API on http://localhost:8000 (tables are created on first start)
cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000

# SPA on http://localhost:4200
cd frontend && npm start
```

Interactive API docs are available at `http://localhost:8000/docs`.

## Testing

Backend (from `backend/`):

```bash
ruff check . && ruff format --check .   # lint + formatting
pytest -q                               # calculator unit tests; API tests are skipped without a test database

# End-to-end API tests (auth, company, quotes, PDF, logo upload, AI parsing with a mocked
# OpenAI client) against a dedicated, disposable PostgreSQL database:
createdb devis_btp_test
TEST_DATABASE_URL=postgresql+asyncpg://postgres@127.0.0.1:5432/devis_btp_test pytest -q
```

Frontend (from `frontend/`):

```bash
npm test -- --watch=false   # Vitest (jsdom)
npx tsc -p tsconfig.app.json --noEmit
```

## Production Build

```bash
# Frontend: static bundle in frontend/dist/frontend/browser (needs access to fonts.googleapis.com
# because the production configuration inlines the Google Fonts CSS)
cd frontend && npx ng build --configuration production

# Full stack with Docker Compose (see DEPLOY.md for the VPS procedure)
cp .env.prod.example .env.prod   # fill DB_PASSWORD, SECRET_KEY, OPENAI_API_KEY, DOMAIN, CORS_ORIGINS
docker compose -f docker-compose.prod.yml --env-file .env.prod up --build -d
curl http://localhost/api/health
```

## Future Improvements

- Generate the initial Alembic migration and run `alembic upgrade head` at container start
  instead of `create_all`.
- Use the refresh token in the SPA (the interceptor currently logs out on the first 401).
- Wire the WebSocket collaboration channel into the editor or remove the unused service.
- Pin Python dependencies (lockfile) for reproducible images.
- Self-host the Inter and Material Icons fonts to remove the build-time dependency on Google Fonts.
- Rate-limit `/auth/login` and the paid `/quotes/parse-text` endpoint.
