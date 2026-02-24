from fastapi import APIRouter, Depends, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.i18n import get_lang
from app.database import get_db
from app.features.auth.models import User
from app.features.quote.ai_parser import parse_text_to_line_items
from app.features.quote.email_service import send_quote_email
from app.features.quote.pdf_generator import generate_quote_pdf
from app.features.quote.schemas import (
    ParseTextRequest,
    ParseTextResponse,
    QuoteCreate,
    QuoteListResponse,
    QuoteResponse,
    QuoteUpdate,
    SendEmailRequest,
    SendEmailResponse,
    VoiceToTextResponse,
)
from app.features.quote.service import (
    create_quote,
    delete_quote,
    duplicate_quote,
    get_quote,
    list_quotes,
    update_quote,
)
from app.features.quote.voice_service import transcribe_audio

router = APIRouter()


@router.post("", response_model=QuoteResponse, status_code=201)
async def create(
    data: QuoteCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_quote(db, user.id, data)


@router.get("", response_model=list[QuoteListResponse])
async def list_all(
    skip: int = 0,
    limit: int = 20,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await list_quotes(db, user.id, skip, limit)


@router.get("/{quote_id}", response_model=QuoteResponse)
async def get_one(
    quote_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_quote(db, user.id, quote_id)


@router.put("/{quote_id}", response_model=QuoteResponse)
async def update(
    quote_id: int,
    data: QuoteUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await update_quote(db, user.id, quote_id, data)


@router.delete("/{quote_id}", status_code=204)
async def delete(
    quote_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await delete_quote(db, user.id, quote_id)


@router.post("/{quote_id}/duplicate", response_model=QuoteResponse, status_code=201)
async def duplicate(
    quote_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await duplicate_quote(db, user.id, quote_id)


@router.post("/parse-text", response_model=ParseTextResponse)
async def parse_text(
    data: ParseTextRequest,
    _user: User = Depends(get_current_user),
):
    return await parse_text_to_line_items(data.text)


@router.post("/voice-to-text", response_model=VoiceToTextResponse)
async def voice_to_text(
    file: UploadFile,
    _user: User = Depends(get_current_user),
):
    audio_data = await file.read()
    result = await transcribe_audio(audio_data, file.filename or "audio.webm")
    return VoiceToTextResponse(**result)


@router.post("/{quote_id}/send-email", response_model=SendEmailResponse)
async def send_email(
    request: Request,
    quote_id: int,
    data: SendEmailRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    lang = get_lang(request)
    message = await send_quote_email(db, user.id, quote_id, data.recipient_email, lang=lang)
    return SendEmailResponse(message=message)


@router.post("/{quote_id}/generate-pdf")
async def generate_pdf(
    quote_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await generate_quote_pdf(db, user.id, quote_id)
