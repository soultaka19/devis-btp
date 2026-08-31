from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.features.quote.calculator import VALID_VAT_RATES
from app.features.quote.models import QuoteStatus

# Length limits mirror the String(n) columns in models.py
# (a longer value made PostgreSQL fail with a 500)
CLIENT_NAME_MAX = 255
CLIENT_EMAIL_MAX = 255
CLIENT_PHONE_MAX = 20
TITLE_MAX = 255
UNIT_MAX = 20
PARSE_TEXT_MAX = 5000


class LineItemCreate(BaseModel):
    description: str
    unit: str = Field(default="u", max_length=UNIT_MAX)
    quantity: float = Field(default=1.0, gt=0)
    unit_price: float = Field(default=0.0, ge=0)
    vat_rate: float = 20.0

    @field_validator("vat_rate")
    @classmethod
    def validate_vat_rate(cls, v: float) -> float:
        if v not in VALID_VAT_RATES:
            raise ValueError("Le taux de TVA doit être 5.5, 10 ou 20")
        return v


class LineItemResponse(LineItemCreate):
    id: int
    position: int
    total_ht: float
    model_config = {"from_attributes": True}


class QuoteCreate(BaseModel):
    client_name: str = Field(default="", max_length=CLIENT_NAME_MAX)
    client_address: str = ""
    # Either a valid email address or empty (the form sends "" when not filled)
    client_email: EmailStr | Literal[""] = Field(default="", max_length=CLIENT_EMAIL_MAX)
    client_phone: str = Field(default="", max_length=CLIENT_PHONE_MAX)
    title: str = Field(default="", max_length=TITLE_MAX)
    description: str = ""
    line_items: list[LineItemCreate] = []


class QuoteUpdate(BaseModel):
    client_name: str | None = Field(default=None, max_length=CLIENT_NAME_MAX)
    client_address: str | None = None
    client_email: EmailStr | Literal[""] | None = Field(default=None, max_length=CLIENT_EMAIL_MAX)
    client_phone: str | None = Field(default=None, max_length=CLIENT_PHONE_MAX)
    title: str | None = Field(default=None, max_length=TITLE_MAX)
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
    # Bounded input: the text is sent to a paid API
    text: str = Field(min_length=1, max_length=PARSE_TEXT_MAX)

    @field_validator("text")
    @classmethod
    def text_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Le texte est vide")
        return v


class ParseTextResponse(BaseModel):
    title: str = ""
    line_items: list[LineItemCreate] = []
    client: ParsedClientInfo | None = None
    # Served from cache: the same model output, without a new call.
    from_cache: bool = False
    # Attempts left for a demo sandbox; None for a real account, under no quota.
    ai_calls_remaining: int | None = None


class VoiceToTextResponse(BaseModel):
    text: str
    duration_ms: int
    from_cache: bool = False
    ai_calls_remaining: int | None = None


class SendEmailRequest(BaseModel):
    recipient_email: EmailStr | None = None


class SendEmailResponse(BaseModel):
    message: str
