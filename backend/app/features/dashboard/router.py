from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database import get_db
from app.features.auth.models import User
from app.features.dashboard.schemas import DashboardStats, RecentQuote
from app.features.dashboard.service import get_dashboard_stats, get_recent_quotes

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def stats(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_dashboard_stats(db, user.id)


@router.get("/recent", response_model=list[RecentQuote])
async def recent(
    limit: int = Query(10, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_recent_quotes(db, user.id, limit)
