from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.client_ip import visitor_address
from app.core.dependencies import get_current_user
from app.core.i18n import get_lang
from app.database import get_db
from app.features.auth.models import User
from app.features.demo.service import create_sandbox, sandbox_of

router = APIRouter()


@router.post("/sandbox", status_code=status.HTTP_201_CREATED)
async def create(request: Request, db: AsyncSession = Depends(get_db)) -> dict:
    """Create a disposable sandbox.

    No guard: this is precisely the entry point for someone with no account.
    Nothing is asked of them - no email address, no password.
    """
    return await create_sandbox(db, visitor_address(request), get_lang(request))


@router.get("/status")
async def sandbox_status(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Current sandbox state: expiry and remaining AI attempts.

    Returns ``is_demo: false`` for a real account, which is under no budget:
    the bill is its owner's.
    """
    sandbox = await sandbox_of(db, user.id)
    if sandbox is None:
        return {"is_demo": False}

    return {
        "is_demo": True,
        "sandbox_expires_at": sandbox.expires_at.isoformat(),
        "ai_calls_total": settings.DEMO_AI_CALLS,
        "ai_calls_remaining": max(0, settings.DEMO_AI_CALLS - sandbox.ai_calls_used),
    }
