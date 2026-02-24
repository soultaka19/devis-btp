# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Devis BTP** — AI-powered quote generation SaaS for French building contractors. Users dictate or type construction work descriptions, AI parses them into structured line items, and the app generates professional PDF quotes.

## Architecture

Monorepo with two independent stacks:

- **Frontend** (`frontend/`): Angular 21 + Angular Material 21 + SCSS
- **Backend** (`backend/`): FastAPI + SQLAlchemy 2 (async) + PostgreSQL 16
- **AI**: OpenAI GPT-4o-mini for parsing French BTP text into line items
- **PDF**: WeasyPrint + Jinja2 templates
- **Auth**: JWT (HS256) with access/refresh tokens

## Common Commands

### Frontend (from `frontend/`)
```bash
npm start          # Dev server on :4200
npm run build      # Production build
npm test           # Unit tests (Vitest)
```

### Backend (from `backend/`)
```bash
uvicorn app.main:app --reload --port 8000   # Dev server
pytest                                       # Tests
pytest -k "test_name"                        # Single test
ruff check .                                 # Lint
alembic upgrade head                         # Run migrations
```

### Docker (from root)
```bash
docker-compose up      # PostgreSQL + Backend (ports 5432, 8000)
```

## Frontend Architecture

**State management**: Angular Signals (no NgRx). Each feature has a `state/` folder with a store class using `signal()` and `computed()`.

**Layout system** (`app.ts`): Configurable layout with signals persisted in localStorage:
- `layoutMode` (`'sidebar' | 'toolbar'`) — key: `btp_layout_mode`
- `sidebarCollapsed` (`boolean`) — key: `btp_sidebar_collapsed`
- `isMobile` — auto-detected at 768px breakpoint
- Single `mat-sidenav-container` always in DOM; toolbar shown/hidden via `showToolbar()` computed signal

**Feature modules** follow the pattern:
```
features/{name}/
  components/    # UI components (inline styles/templates)
  models/        # TypeScript interfaces
  state/         # Signal-based store
  services/      # API service (optional)
  {name}.routes.ts
```

**Key files**:
- `core/api/api.service.ts` — HTTP client wrapper (base URL from environment)
- `core/auth/auth.interceptor.ts` — Injects Bearer token, handles 401
- `core/auth/auth.guard.ts` — Route protection
- `environments/environment.ts` — `apiUrl: http://localhost:8000`

**Component naming**: Files use `.component.ts` suffix but some root-level use short names (`app.ts`, `app.html`, `app.scss`).

## Backend Architecture

**Feature modules** follow the pattern:
```
app/features/{name}/
  models.py      # SQLAlchemy models
  schemas.py     # Pydantic validation
  service.py     # Business logic
  router.py      # FastAPI endpoints
```

**API routes**: `/auth`, `/quotes`, `/company`, `/dashboard`, `/ws`, `/health`

**AI parsing** (`features/quote/ai_parser.py`): Uses GPT-4o-mini function calling to extract line items from French BTP text. Auto-assigns units (m², u, h, forfait) and VAT rates (10% renovation, 20% new).

**Config** (`app/config.py`): All settings via environment variables. Key: `DATABASE_URL`, `SECRET_KEY`, `OPENAI_API_KEY`.

## Database

PostgreSQL 16. Models: `users`, `quotes`, `line_items`, `company_info`, `banking`, `insurance`, `terms`. Migrations via Alembic.

Default dev credentials: `postgres/postgres` on `localhost:5432/devis_btp`.

## Style Conventions

- **Frontend**: SCSS with CSS custom properties (`--primary`, `--accent`, `--surface`, etc.) defined in `styles.scss`. Mobile-first breakpoints: base (<768px), tablet (768px+), desktop (1024px+).
- **Backend**: Ruff linter, line length 100, Python 3.11+.
- **Language**: UI text is in French. Code (variables, comments) in English.
