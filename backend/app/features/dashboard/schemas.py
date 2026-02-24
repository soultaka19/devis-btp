from datetime import datetime

from pydantic import BaseModel

from app.features.quote.models import QuoteStatus


class DashboardStats(BaseModel):
    total_quotes: int
    quotes_this_month: int
    avg_quote_value: float
    status_breakdown: dict[str, int]


class RecentQuote(BaseModel):
    id: int
    reference: str
    client_name: str
    title: str
    total_ttc: float
    status: QuoteStatus
    created_at: datetime
    model_config = {"from_attributes": True}
