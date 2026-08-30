from fastapi import APIRouter, Depends, Query, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.exceptions import AppException
from app.core.i18n import get_lang, t
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
from app.features.quote.voice_service import MAX_AUDIO_SIZE, transcribe_audio

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
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
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
    request: Request,
    data: ParseTextRequest,
    _user: User = Depends(get_current_user),
):
    return await parse_text_to_line_items(data.text, lang=get_lang(request))


@router.post("/voice-to-text", response_model=VoiceToTextResponse)
async def voice_to_text(
    request: Request,
    file: UploadFile,
    _user: User = Depends(get_current_user),
):
    lang = get_lang(request)
    if not file.content_type or not file.content_type.startswith("audio/"):
        raise AppException(
            t("voice.unsupported_type", lang), code="UNSUPPORTED_MEDIA_TYPE", status_code=415
        )

    # Reject oversized uploads before reading them into memory (Whisper limit: 25 MB)
    content_length = request.headers.get("content-length", "")
    if content_length.isdigit() and int(content_length) > MAX_AUDIO_SIZE + 64 * 1024:
        raise AppException(t("voice.file_too_large", lang), code="FILE_TOO_LARGE", status_code=413)
    audio_data = await file.read(MAX_AUDIO_SIZE + 1)
    if len(audio_data) > MAX_AUDIO_SIZE:
        raise AppException(t("voice.file_too_large", lang), code="FILE_TOO_LARGE", status_code=413)
    if not audio_data:
        raise AppException(t("voice.empty_file", lang), code="VALIDATION_ERROR", status_code=422)

    result = await transcribe_audio(audio_data, file.filename or "audio.webm", lang=lang)
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
