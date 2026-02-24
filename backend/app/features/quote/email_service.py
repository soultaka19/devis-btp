import base64
import logging

import resend
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.i18n import t
from app.features.company.service import get_company
from app.features.quote.models import QuoteStatus
from app.features.quote.pdf_generator import generate_pdf_bytes
from app.features.quote.service import get_quote

logger = logging.getLogger(__name__)


async def send_quote_email(
    db: AsyncSession,
    user_id: int,
    quote_id: int,
    recipient_email: str | None = None,
    lang: str = "fr",
) -> str:
    quote = await get_quote(db, user_id, quote_id)
    company = await get_company(db, user_id)

    email = recipient_email or quote.client_email
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=t("email.no_recipient", lang),
        )

    company_name = company.name if company else t("email.default_company", lang)

    pdf_bytes = await generate_pdf_bytes(db, user_id, quote_id)

    if not settings.RESEND_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=t("email.api_key_missing", lang),
        )

    resend.api_key = settings.RESEND_API_KEY

    params = {
        "from": f"{company_name} <{settings.RESEND_FROM_EMAIL}>",
        "to": [email],
        "subject": t("email.subject", lang, reference=quote.reference, company=company_name),
        "html": (
            f"<p>{t('email.greeting', lang, name=quote.client_name or '')}</p>"
            f"<p>{t('email.body', lang, reference=quote.reference)}</p>"
            f"<p>{t('email.closing', lang, company=company_name)}</p>"
        ),
        "attachments": [
            {
                "filename": f"devis-{quote.reference}.pdf",
                "content": base64.b64encode(pdf_bytes).decode("utf-8"),
                "content_type": "application/pdf",
            }
        ],
    }

    try:
        resend.Emails.send(params)
    except Exception as e:
        logger.error("Failed to send email via Resend: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=t("email.send_error", lang, error=str(e)),
        )

    quote.status = QuoteStatus.SENT
    await db.commit()

    return t("email.success", lang, reference=quote.reference, email=email)
