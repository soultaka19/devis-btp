from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    siret: Mapped[str] = mapped_column(String(14))
    address: Mapped[str] = mapped_column(Text)
    city: Mapped[str] = mapped_column(String(255))
    postal_code: Mapped[str] = mapped_column(String(10))
    phone: Mapped[str] = mapped_column(String(20))
    email: Mapped[str] = mapped_column(String(255))
    logo_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )


class Banking(Base):
    __tablename__ = "banking"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    bank_name: Mapped[str] = mapped_column(String(255))
    iban: Mapped[str] = mapped_column(String(34))
    bic: Mapped[str] = mapped_column(String(11))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )


class Insurance(Base):
    __tablename__ = "insurances"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    provider: Mapped[str] = mapped_column(String(255))
    policy_number: Mapped[str] = mapped_column(String(100))
    coverage_zone: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )


class Terms(Base):
    __tablename__ = "terms"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    payment_terms: Mapped[str] = mapped_column(Text, default="Paiement à 30 jours")
    validity_days: Mapped[int] = mapped_column(default=30)
    late_penalty_rate: Mapped[float] = mapped_column(default=3.0)
    general_conditions: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
