"""Gate around model calls: cache first, budget second.

The order matters. The cache is consulted **before** any quota check, because an
input already seen costs nothing: refusing it in the name of the budget would be
absurd. A visitor only spends their quota when they submit something new — that
is, when they actually test the product.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import AppException
from app.core.i18n import t
from app.core.llm_budget import (
    Usage,
    check_global_budget,
    fingerprint,
    read_cache,
    record,
    write_cache,
)
from app.features.auth.models import User
from app.features.demo.service import sandbox_of


async def guarded_call(
    db: AsyncSession,
    user: User,
    kind: str,
    payload: str,
    real_call: Callable[[], Awaitable[dict]],
    lang: str = "fr",
) -> dict:
    """Serve from cache when possible, otherwise call the model and bill the budget.

    The result carries two extra fields meant to be displayed: ``from_cache`` and
    ``ai_calls_remaining``. A visitor should know what is left, and know when they
    are looking at an already-computed result.
    """
    key = fingerprint(kind, payload)
    sandbox = await sandbox_of(db, user.id)

    def remaining() -> int | None:
        if sandbox is None:
            return None
        return max(0, settings.DEMO_AI_CALLS - sandbox.ai_calls_used)

    # The cache serves DEMO sandboxes only. A real account always gets a live
    # call: the cache exists to make the demonstration cheap, not to change the
    # product's behaviour for someone using it for real — who would otherwise
    # never be able to re-run a parse, and whose provider errors would be
    # masked by an older successful answer.
    if sandbox is not None:
        cached = await read_cache(db, key)
        if cached is not None:
            return cached | {"from_cache": True, "ai_calls_remaining": remaining()}

    if sandbox is not None:
        if sandbox.ai_calls_used >= settings.DEMO_AI_CALLS:
            raise AppException(
                t("demo.quota_exhausted", lang).format(n=settings.DEMO_AI_CALLS),
                code="AI_QUOTA_EXHAUSTED",
                status_code=429,
            )
        # Global ceilings apply to visitors only: the account holder pays their
        # own bill and has no reason to be throttled.
        await check_global_budget(db, lang)

    result = await real_call()
    usage = result.pop("usage", None)
    await record(db, usage if isinstance(usage, Usage) else Usage(0, 0))

    if sandbox is not None:
        sandbox.ai_calls_used += 1
        await db.commit()
        await write_cache(db, key, kind, result)

    return result | {"from_cache": False, "ai_calls_remaining": remaining()}
