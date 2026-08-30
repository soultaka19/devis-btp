import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.features.quote.calculator import calc_line_total, calc_quote_totals
from app.features.quote.models import LineItem, Quote, QuoteStatus
from app.features.quote.schemas import QuoteCreate, QuoteUpdate


def _generate_reference() -> str:
    now = datetime.now(UTC)
    short_id = uuid.uuid4().hex[:6].upper()
    return f"DEV-{now.strftime('%Y%m')}-{short_id}"


async def create_quote(db: AsyncSession, user_id: int, data: QuoteCreate) -> Quote:
    quote = Quote(
        user_id=user_id,
        reference=_generate_reference(),
        client_name=data.client_name,
        client_address=data.client_address,
        client_email=data.client_email,
        client_phone=data.client_phone,
        title=data.title,
        description=data.description,
    )
    db.add(quote)
    await db.flush()

    for i, item_data in enumerate(data.line_items):
        lt = calc_line_total(item_data.quantity, item_data.unit_price, item_data.vat_rate)
        item = LineItem(
            quote_id=quote.id,
            position=i,
            description=item_data.description,
            unit=item_data.unit,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            vat_rate=item_data.vat_rate,
            total_ht=lt.total_ht,
        )
        db.add(item)

    _recalc_totals(quote, data.line_items)
    await db.commit()
    return await get_quote(db, user_id, quote.id)


async def get_quote(db: AsyncSession, user_id: int, quote_id: int) -> Quote:
    result = await db.execute(
        select(Quote)
        .options(selectinload(Quote.line_items))
        .where(Quote.id == quote_id, Quote.user_id == user_id)
    )
    quote = result.scalar_one_or_none()
    if not quote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Devis introuvable")
    return quote


async def list_quotes(
    db: AsyncSession, user_id: int, skip: int = 0, limit: int = 20
) -> list[Quote]:
    result = await db.execute(
        select(Quote)
        .where(Quote.user_id == user_id)
        .order_by(Quote.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def update_quote(db: AsyncSession, user_id: int, quote_id: int, data: QuoteUpdate) -> Quote:
    quote = await get_quote(db, user_id, quote_id)

    for field in [
        "client_name",
        "client_address",
        "client_email",
        "client_phone",
        "title",
        "description",
        "status",
    ]:
        value = getattr(data, field, None)
        if value is not None:
            setattr(quote, field, value)

    if data.line_items is not None:
        # Replace all line items
        for item in quote.line_items:
            await db.delete(item)
        await db.flush()

        for i, item_data in enumerate(data.line_items):
            lt = calc_line_total(item_data.quantity, item_data.unit_price, item_data.vat_rate)
            item = LineItem(
                quote_id=quote.id,
                position=i,
                description=item_data.description,
                unit=item_data.unit,
                quantity=item_data.quantity,
                unit_price=item_data.unit_price,
                vat_rate=item_data.vat_rate,
                total_ht=lt.total_ht,
            )
            db.add(item)

        _recalc_totals(quote, data.line_items)

    await db.commit()
    return await get_quote(db, user_id, quote_id)


async def delete_quote(db: AsyncSession, user_id: int, quote_id: int) -> None:
    quote = await get_quote(db, user_id, quote_id)
    await db.delete(quote)
    await db.commit()


async def duplicate_quote(db: AsyncSession, user_id: int, quote_id: int) -> Quote:
    original = await get_quote(db, user_id, quote_id)
    new_quote = Quote(
        user_id=user_id,
        reference=_generate_reference(),
        status=QuoteStatus.DRAFT,
        client_name=original.client_name,
        client_address=original.client_address,
        client_email=original.client_email,
        client_phone=original.client_phone,
        title=f"{original.title} (copie)",
        description=original.description,
        subtotal_ht=original.subtotal_ht,
        total_vat=original.total_vat,
        total_ttc=original.total_ttc,
    )
    db.add(new_quote)
    await db.flush()

    for item in original.line_items:
        new_item = LineItem(
            quote_id=new_quote.id,
            position=item.position,
            description=item.description,
            unit=item.unit,
            quantity=item.quantity,
            unit_price=item.unit_price,
            vat_rate=item.vat_rate,
            total_ht=item.total_ht,
        )
        db.add(new_item)

    await db.commit()
    return await get_quote(db, user_id, new_quote.id)


def _recalc_totals(quote: Quote, line_items) -> None:
    lines = [
        {"quantity": li.quantity, "unit_price": li.unit_price, "vat_rate": li.vat_rate}
        for li in line_items
    ]
    totals = calc_quote_totals(lines)
    quote.subtotal_ht = totals.subtotal_ht
    quote.total_vat = totals.total_vat
    quote.total_ttc = totals.total_ttc
