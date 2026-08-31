"""LLM spend control: an input cache first, dollar ceilings second.

Three ideas, in order of importance.

1. **The cache is the real lever.** Demo inputs form a finite set — they are the
   provided examples. A cache keyed on the input fingerprint makes the first
   visitor pay and nobody else. The next one sees the **real** model output,
   instantly, at zero cost. That is neither a fake nor a disguised pre-computation:
   it is the same result.

2. **A visitor's budget is only spent on something new.** A cache hit decrements
   nothing. The quota is consumed exactly when the visitor tests the product for
   real, by editing an example or dictating their own text.

3. **Global ceilings protect the bill.** They are expressed in dollars and computed
   from the tokens the API actually reports in ``usage``, never from an estimate:
   reasoning tokens are invisible in the response yet billed at the output rate,
   and they dominate the cost of a small call. They depend on no header, so they
   hold even if the per-IP limit is bypassed.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import UTC, date, datetime

from sqlalchemy import DateTime, Float, Integer, String, Text, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.config import settings
from app.core.exceptions import AppException
from app.core.i18n import t
from app.database import Base

logger = logging.getLogger(__name__)


class LlmCache(Base):
    """A model response for a given input, reusable as-is."""

    __tablename__ = "llm_cache"

    # sha256 of (kind + model + input). The model is part of the key: otherwise
    # switching models would silently serve answers from the previous one.
    cache_key: Mapped[str] = mapped_column(String(64), primary_key=True)
    kind: Mapped[str] = mapped_column(String(32), index=True)
    response_json: Mapped[str] = mapped_column(Text)
    hits: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


class LlmSpend(Base):
    """Cumulated spend over a period (``2026-08-31`` or ``2026-08``)."""

    __tablename__ = "llm_spend"

    period: Mapped[str] = mapped_column(String(10), primary_key=True)
    calls: Mapped[int] = mapped_column(Integer, default=0)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    usd: Mapped[float] = mapped_column(Float, default=0.0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )


@dataclass(frozen=True)
class Usage:
    input_tokens: int
    output_tokens: int

    @property
    def usd(self) -> float:
        return (
            self.input_tokens * settings.LLM_PRICE_INPUT_PER_M
            + self.output_tokens * settings.LLM_PRICE_OUTPUT_PER_M
        ) / 1_000_000


def usage_from_response(response: object) -> Usage:
    """Extract ``usage`` from an OpenAI-shaped response, tolerating its absence.

    ``total_tokens`` includes reasoning tokens, which ``completion_tokens`` does
    not count. The gap is therefore taken as the real output: on a trivial call
    measured on 2026-08-31, 6 input and 1 output tokens reported billed 88 to 143.
    """
    usage = getattr(response, "usage", None)
    if usage is None:
        return Usage(0, 0)

    prompt = int(getattr(usage, "prompt_tokens", 0) or 0)
    total = int(getattr(usage, "total_tokens", 0) or 0)
    completion = int(getattr(usage, "completion_tokens", 0) or 0)

    return Usage(prompt, max(completion, total - prompt))


def fingerprint(kind: str, payload: str) -> str:
    raw = f"{kind}\x00{settings.LLM_MODEL}\x00{payload}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


async def read_cache(db: AsyncSession, key: str) -> dict | None:
    entry = await db.get(LlmCache, key)
    if entry is None:
        return None

    entry.hits += 1
    await db.commit()
    logger.info("LLM cache hit (%s, %d times)", entry.kind, entry.hits)
    return json.loads(entry.response_json)


async def write_cache(db: AsyncSession, key: str, kind: str, response: dict) -> None:
    if await db.get(LlmCache, key) is not None:
        return
    db.add(LlmCache(cache_key=key, kind=kind, response_json=json.dumps(response), hits=0))
    await db.commit()


def _periods(today: date | None = None) -> tuple[str, str]:
    day = today or datetime.now(UTC).date()
    return day.isoformat(), day.strftime("%Y-%m")


async def spend(db: AsyncSession, period: str) -> float:
    row = await db.get(LlmSpend, period)
    return row.usd if row else 0.0


async def check_global_budget(db: AsyncSession, lang: str = "fr") -> None:
    """Refuse the call when a ceiling is reached, with a clear message, not a 500."""
    day, month = _periods()

    if await spend(db, day) >= settings.LLM_DAILY_BUDGET_USD:
        raise AppException(
            t("demo.budget_daily", lang), code="AI_BUDGET_EXHAUSTED", status_code=429
        )

    if await spend(db, month) >= settings.LLM_MONTHLY_BUDGET_USD:
        raise AppException(
            t("demo.budget_monthly", lang), code="AI_BUDGET_EXHAUSTED", status_code=429
        )


async def record(db: AsyncSession, usage: Usage) -> None:
    """Add the consumption to both the daily and the monthly counters."""
    cost = usage.usd

    for period in _periods():
        row = await db.get(LlmSpend, period)
        if row is None:
            # The zeros are explicit: ``default=0`` is applied by SQLAlchemy at
            # INSERT time, so the attributes are still None on a freshly built
            # object — and `+=` below would fail on None.
            row = LlmSpend(period=period, calls=0, input_tokens=0, output_tokens=0, usd=0.0)
            db.add(row)
        row.calls += 1
        row.input_tokens += usage.input_tokens
        row.output_tokens += usage.output_tokens
        row.usd += cost

    await db.commit()
    logger.info(
        "LLM call: %d input tokens, %d output, $%.5f",
        usage.input_tokens,
        usage.output_tokens,
        cost,
    )


async def cache_size(db: AsyncSession) -> int:
    return int((await db.execute(select(func.count()).select_from(LlmCache))).scalar_one())
