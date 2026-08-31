"""Create and purge demo sandboxes.

Devis BTP scopes by ``user_id``: every business record — company, banking,
insurance, terms, quotes — hangs off a user. A sandbox is therefore simply a
**disposable user**, and the isolation is the product's own.
"""

from __future__ import annotations

import logging
import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import AppException
from app.core.i18n import t
from app.core.security import create_access_token, hash_password
from app.features.auth.models import User
from app.features.company.models import Banking, Company, Insurance, Terms
from app.features.demo.models import DemoSandbox
from app.features.quote.models import LineItem, Quote, QuoteStatus

logger = logging.getLogger(__name__)


async def create_sandbox(db: AsyncSession, visitor_address: str, lang: str = "fr") -> dict:
    now = datetime.now(UTC)

    await _check_ceilings(db, visitor_address, now, lang)

    suffix = secrets.token_hex(4)
    password = f"Demo-{secrets.token_hex(6).upper()}"
    expires_at = now + timedelta(minutes=settings.DEMO_LIFETIME_MINUTES)

    user = User(
        email=f"demo-{suffix}@demo.test",
        hashed_password=hash_password(password),
        full_name="Sonia Bélanger",
        is_active=True,
    )
    db.add(user)
    await db.flush()

    # ai_calls_used is set explicitly: ``default=0`` only applies at INSERT, and
    # the counter is incremented later on an object that may still be in session.
    db.add(
        DemoSandbox(
            user_id=user.id,
            expires_at=expires_at,
            creator_ip=visitor_address,
            ai_calls_used=0,
        )
    )
    _seed(db, user.id, now)
    await db.commit()

    logger.info("Sandbox %s created, expires at %s", user.id, expires_at.isoformat())

    return {
        "access_token": create_access_token(str(user.id)),
        "token_type": "bearer",
        "user": {"id": user.id, "email": user.email, "full_name": user.full_name},
        "sandbox_expires_at": expires_at.isoformat(),
        "ai_calls_total": settings.DEMO_AI_CALLS,
        "ai_calls_remaining": settings.DEMO_AI_CALLS,
    }


async def _check_ceilings(db: AsyncSession, address: str, now: datetime, lang: str = "fr") -> None:
    live = (
        await db.execute(
            select(func.count()).select_from(DemoSandbox).where(DemoSandbox.expires_at > now)
        )
    ).scalar_one()

    if live >= settings.DEMO_MAX_LIVE_SANDBOXES:
        logger.warning("Live sandbox ceiling reached (%s)", live)
        raise AppException(t("demo.saturated", lang), code="DEMO_SATURATED", status_code=503)

    # Per-visitor throttle. It lives in the database rather than in memory: a
    # container restart must not reset the counter.
    window_start = now - timedelta(minutes=settings.DEMO_RATE_WINDOW_MINUTES)
    recent = (
        await db.execute(
            select(func.count())
            .select_from(DemoSandbox)
            .where(DemoSandbox.creator_ip == address, DemoSandbox.created_at > window_start)
        )
    ).scalar_one()

    if recent >= settings.DEMO_RATE_LIMIT:
        raise AppException(t("demo.rate_limited", lang), code="DEMO_RATE_LIMITED", status_code=429)


def _seed(db: AsyncSession, user_id: int, now: datetime) -> None:
    """A contractor profile and three quotes, so that nothing is empty."""
    db.add(
        Company(
            user_id=user_id,
            name="Bélanger Rénovation",
            siret="80295478100017",
            address="14 rue des Lilas",
            city="Nantes",
            postal_code="44000",
            phone="02 40 12 34 56",
            email="contact@belanger-renovation.demo",
        )
    )
    db.add(
        Banking(
            user_id=user_id,
            bank_name="Crédit Mutuel",
            iban="FR7630003011200005001234567",
            bic="CMCIFRPP",
        )
    )
    db.add(
        Insurance(
            user_id=user_id,
            provider="MAAF Pro",
            policy_number="RCD-2026-778411",
            coverage_zone="France métropolitaine",
        )
    )
    db.add(
        Terms(
            user_id=user_id,
            payment_terms="Acompte de 30 % à la commande, solde à la livraison",
            validity_days=30,
            late_penalty_rate=3.0,
            general_conditions="Devis valable un mois. Travaux exécutés selon les DTU en vigueur.",
        )
    )

    for quote in _DEMO_QUOTES:
        _add_quote(db, user_id, now, quote)


def _add_quote(db: AsyncSession, user_id: int, now: datetime, data: dict) -> None:
    items = data["items"]
    subtotal = sum(x["quantity"] * x["price"] for x in items)
    vat = sum(x["quantity"] * x["price"] * x["vat"] / 100 for x in items)

    quote = Quote(
        user_id=user_id,
        reference=f"DEV-{now.year}-{secrets.token_hex(3).upper()}",
        status=data["status"],
        client_name=data["client"],
        client_address=data["address"],
        client_email=data["email"],
        client_phone=data["phone"],
        title=data["title"],
        description=data["description"],
        subtotal_ht=round(subtotal, 2),
        total_vat=round(vat, 2),
        total_ttc=round(subtotal + vat, 2),
    )
    db.add(quote)
    quote.line_items = [
        LineItem(
            position=position,
            description=item["label"],
            unit=item["unit"],
            quantity=item["quantity"],
            unit_price=item["price"],
            vat_rate=item["vat"],
            total_ht=round(item["quantity"] * item["price"], 2),
        )
        for position, item in enumerate(items)
    ]


# Three quotes across three statuses: enough to fill the list, the dashboard and
# the totals from the very first second.
_DEMO_QUOTES: list[dict] = [
    {
        "status": QuoteStatus.SENT,
        "client": "Mme Christine Lemoine",
        "address": "8 allée des Cèdres, 44300 Nantes",
        "email": "c.lemoine@exemple.fr",
        "phone": "06 12 34 56 78",
        "title": "Réfection complète de salle de bain",
        "description": "Dépose de l'existant, plomberie, faïence, douche à l'italienne.",
        "items": [
            {
                "label": "Dépose de l'ancienne salle de bain",
                "unit": "forfait",
                "quantity": 1,
                "price": 780.0,
                "vat": 10.0,
            },
            {
                "label": "Fourniture et pose de faïence murale",
                "unit": "m²",
                "quantity": 18.5,
                "price": 62.0,
                "vat": 10.0,
            },
            {
                "label": "Douche à l'italienne, receveur et paroi",
                "unit": "u",
                "quantity": 1,
                "price": 1490.0,
                "vat": 10.0,
            },
            {
                "label": "Main-d'œuvre plomberie",
                "unit": "h",
                "quantity": 22,
                "price": 48.0,
                "vat": 10.0,
            },
        ],
    },
    {
        "status": QuoteStatus.DRAFT,
        "client": "SCI Les Tilleuls",
        "address": "22 boulevard Gabriel Guist'hau, 44000 Nantes",
        "email": "gestion@sci-tilleuls.exemple.fr",
        "phone": "02 40 98 76 54",
        "title": "Isolation des combles perdus",
        "description": "Soufflage de laine de roche sur 120 m², pose d'un pare-vapeur.",
        "items": [
            {
                "label": "Soufflage laine de roche 320 mm",
                "unit": "m²",
                "quantity": 120,
                "price": 27.5,
                "vat": 5.5,
            },
            {
                "label": "Pare-vapeur et calfeutrement",
                "unit": "m²",
                "quantity": 120,
                "price": 8.0,
                "vat": 5.5,
            },
            {
                "label": "Protection des spots et trappe d'accès",
                "unit": "forfait",
                "quantity": 1,
                "price": 240.0,
                "vat": 5.5,
            },
        ],
    },
    {
        "status": QuoteStatus.ACCEPTED,
        "client": "M. Patrick Rousseau",
        "address": "5 rue du Moulin, 44120 Vertou",
        "email": "p.rousseau@exemple.fr",
        "phone": "06 87 65 43 21",
        "title": "Remplacement de menuiseries extérieures",
        "description": "Six fenêtres PVC double vitrage, dépose et évacuation comprises.",
        "items": [
            {
                "label": "Fenêtre PVC 2 vantaux 120×115",
                "unit": "u",
                "quantity": 4,
                "price": 645.0,
                "vat": 10.0,
            },
            {
                "label": "Fenêtre PVC 1 vantail 60×95",
                "unit": "u",
                "quantity": 2,
                "price": 410.0,
                "vat": 10.0,
            },
            {
                "label": "Dépose et évacuation en déchetterie",
                "unit": "forfait",
                "quantity": 1,
                "price": 520.0,
                "vat": 10.0,
            },
        ],
    },
]


async def purge_expired(db: AsyncSession) -> int:
    """Delete sandboxes past their expiry.

    Order follows the foreign keys: ``line_items`` cascade with their quote, and
    everything else hangs off the user, which can therefore only go last.
    """
    now = datetime.now(UTC)

    user_ids = list(
        (
            await db.execute(select(DemoSandbox.user_id).where(DemoSandbox.expires_at < now))
        ).scalars()
    )
    if not user_ids:
        return 0

    quote_ids = list(
        (await db.execute(select(Quote.id).where(Quote.user_id.in_(user_ids)))).scalars()
    )
    if quote_ids:
        await db.execute(delete(LineItem).where(LineItem.quote_id.in_(quote_ids)))
        await db.execute(delete(Quote).where(Quote.id.in_(quote_ids)))

    for model in (Company, Banking, Insurance, Terms):
        await db.execute(delete(model).where(model.user_id.in_(user_ids)))

    await db.execute(delete(DemoSandbox).where(DemoSandbox.user_id.in_(user_ids)))
    await db.execute(delete(User).where(User.id.in_(user_ids)))
    await db.commit()

    logger.info("%d expired sandbox(es) deleted", len(user_ids))
    return len(user_ids)


async def sandbox_of(db: AsyncSession, user_id: int) -> DemoSandbox | None:
    return (
        await db.execute(select(DemoSandbox).where(DemoSandbox.user_id == user_id))
    ).scalar_one_or_none()
