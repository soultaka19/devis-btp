from datetime import UTC, datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class QuoteStatus(str, PyEnum):
    DRAFT = "draft"
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class Quote(Base):
    __tablename__ = "quotes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    reference: Mapped[str] = mapped_column(String(50), unique=True)
    status: Mapped[QuoteStatus] = mapped_column(Enum(QuoteStatus), default=QuoteStatus.DRAFT)

    # Client info
    client_name: Mapped[str] = mapped_column(String(255), default="")
    client_address: Mapped[str] = mapped_column(Text, default="")
    client_email: Mapped[str] = mapped_column(String(255), default="")
    client_phone: Mapped[str] = mapped_column(String(20), default="")

    # Description
    title: Mapped[str] = mapped_column(String(255), default="")
    description: Mapped[str] = mapped_column(Text, default="")

    # Totals (computed)
    subtotal_ht: Mapped[float] = mapped_column(Float, default=0.0)
    total_vat: Mapped[float] = mapped_column(Float, default=0.0)
    total_ttc: Mapped[float] = mapped_column(Float, default=0.0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    line_items: Mapped[list["LineItem"]] = relationship(
        back_populates="quote", cascade="all, delete-orphan", order_by="LineItem.position"
    )


class LineItem(Base):
    __tablename__ = "line_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    quote_id: Mapped[int] = mapped_column(ForeignKey("quotes.id", ondelete="CASCADE"), index=True)
    position: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[str] = mapped_column(Text)
    unit: Mapped[str] = mapped_column(String(20), default="u")  # u, m², m, h, kg, forfait
    quantity: Mapped[float] = mapped_column(Float, default=1.0)
    unit_price: Mapped[float] = mapped_column(Float, default=0.0)
    vat_rate: Mapped[float] = mapped_column(Float, default=20.0)  # 5.5, 10.0, 20.0
    total_ht: Mapped[float] = mapped_column(Float, default=0.0)

    quote: Mapped["Quote"] = relationship(back_populates="line_items")
