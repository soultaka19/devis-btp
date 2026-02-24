from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.exceptions import register_exception_handlers
from app.database import Base, engine
from app.features.auth.router import router as auth_router
from app.features.company.router import router as company_router
from app.features.dashboard.router import router as dashboard_router
from app.features.quote.router import router as quote_router
from app.features.quote.ws_router import router as quote_ws_router

# Import all models so they register with Base.metadata
import app.features.auth.models  # noqa: F401
import app.features.company.models  # noqa: F401
import app.features.quote.models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Devis BTP API",
    version="0.1.0",
    description="API SaaS pour devis BTP avec commande vocale",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(company_router, prefix="/company", tags=["Company"])
app.include_router(quote_router, prefix="/quotes", tags=["Quotes"])
app.include_router(quote_ws_router, prefix="/ws", tags=["WebSocket"])
app.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])


@app.get("/health")
async def health():
    return {"status": "ok"}
