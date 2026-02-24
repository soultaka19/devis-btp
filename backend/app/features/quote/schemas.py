from datetime import datetime

from pydantic import BaseModel

from app.features.quote.models import QuoteStatus


class LineItemCreate(BaseModel):
    description: str
    unit: str = "u"
    quantity: float = 1.0
    unit_price: float = 0.0
    vat_rate: float = 20.0


class LineItemResponse(LineItemCreate):
    id: int
    position: int
    total_ht: float
    model_config = {"from_attributes": True}


class QuoteCreate(BaseModel):
    client_name: str = ""
    client_address: str = ""
    client_email: str = ""
    client_phone: str = ""
    title: str = ""
    description: str = ""
    line_items: list[LineItemCreate] = []


class QuoteUpdate(BaseModel):
    client_name: str | None = None
    client_address: str | None = None
    client_email: str | None = None
    client_phone: str | None = None
    title: str | None = None
    description: str | None = None
    status: QuoteStatus | None = None
    line_items: list[LineItemCreate] | None = None


class QuoteResponse(BaseModel):
    id: int
    reference: str
    status: QuoteStatus
    client_name: str
    client_address: str
    client_email: str
    client_phone: str
    title: str
    description: str
    subtotal_ht: float
    total_vat: float
    total_ttc: float
    line_items: list[LineItemResponse]
    model_config = {"from_attributes": True}


class QuoteListResponse(BaseModel):
    id: int
    reference: str
    status: QuoteStatus
    client_name: str
    title: str
    total_ttc: float
    created_at: datetime
    model_config = {"from_attributes": True}


class ParsedClientInfo(BaseModel):
    name: str | None = None
    address: str | None = None
    email: str | None = None
    phone: str | None = None


class ParseTextRequest(BaseModel):
    text: str


class ParseTextResponse(BaseModel):
    title: str = ""
    line_items: list[LineItemCreate] = []
    client: ParsedClientInfo | None = None


class VoiceToTextResponse(BaseModel):
    text: str
    duration_ms: int


class SendEmailRequest(BaseModel):
    recipient_email: str | None = None


class SendEmailResponse(BaseModel):
    message: str
