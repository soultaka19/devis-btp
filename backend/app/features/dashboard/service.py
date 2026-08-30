from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.quote.models import Quote, QuoteStatus


async def get_dashboard_stats(db: AsyncSession, user_id: int) -> dict:
    # Total quotes
    total_result = await db.execute(select(func.count(Quote.id)).where(Quote.user_id == user_id))
    total_quotes = total_result.scalar() or 0

    # This month
    now = datetime.now(UTC)
    first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_result = await db.execute(
        select(func.count(Quote.id)).where(
            Quote.user_id == user_id,
            Quote.created_at >= first_of_month,
        )
    )
    quotes_this_month = month_result.scalar() or 0

    # Average value
    avg_result = await db.execute(select(func.avg(Quote.total_ttc)).where(Quote.user_id == user_id))
    avg_quote_value = round(avg_result.scalar() or 0.0, 2)

    # Status breakdown
    status_result = await db.execute(
        select(Quote.status, func.count(Quote.id))
        .where(Quote.user_id == user_id)
        .group_by(Quote.status)
    )
    status_breakdown = {row[0].value: row[1] for row in status_result.all()}

    # Fill missing statuses
    for s in QuoteStatus:
        if s.value not in status_breakdown:
            status_breakdown[s.value] = 0

    return {
        "total_quotes": total_quotes,
        "quotes_this_month": quotes_this_month,
        "avg_quote_value": avg_quote_value,
        "status_breakdown": status_breakdown,
    }


async def get_recent_quotes(db: AsyncSession, user_id: int, limit: int = 10) -> list[Quote]:
    result = await db.execute(
        select(Quote).where(Quote.user_id == user_id).order_by(Quote.created_at.desc()).limit(limit)
    )
    return list(result.scalars().all())
