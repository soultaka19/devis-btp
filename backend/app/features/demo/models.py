from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class DemoSandbox(Base):
    """A disposable demo user and its expiry date.

    A separate table rather than two columns on ``users``: the schema is created
    by ``Base.metadata.create_all`` at startup, which creates missing tables but
    **never adds a column** to an existing one. Two columns on ``users`` would
    therefore never have reached production, with no error to signal it.
    """

    __tablename__ = "demo_sandboxes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    # Visitor address, used to throttle burst creations. See app/core/client_ip.py:
    # this is not the connection address.
    creator_ip: Mapped[str] = mapped_column(String(64), index=True)

    # REAL model calls already consumed. A cache hit does not count.
    ai_calls_used: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
