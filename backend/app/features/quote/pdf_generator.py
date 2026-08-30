import base64
import mimetypes
from io import BytesIO
from pathlib import Path

from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy.ext.asyncio import AsyncSession

try:
    from weasyprint import HTML

    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False

from app.core.storage import storage
from app.features.company.service import get_banking, get_company, get_insurance, get_terms
from app.features.quote.calculator import calc_quote_totals
from app.features.quote.service import get_quote

TEMPLATE_DIR = Path(__file__).parent.parent.parent / "templates"
# autoescape: user-provided values (client name, descriptions...) are rendered as text, not HTML
jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
)


async def logo_data_uri(logo_path: str | None) -> str | None:
    """Embed the stored logo as a data: URI so WeasyPrint renders it without any base URL."""
    if not logo_path:
        return None
    data = await storage.get(logo_path)
    if not data:
        return None
    mime_type = mimetypes.guess_type(logo_path)[0] or "image/png"
    return f"data:{mime_type};base64,{base64.b64encode(data).decode('ascii')}"


async def generate_pdf_bytes(db: AsyncSession, user_id: int, quote_id: int) -> bytes:
    quote = await get_quote(db, user_id, quote_id)
    company = await get_company(db, user_id)
    banking = await get_banking(db, user_id)
    insurance = await get_insurance(db, user_id)
    terms = await get_terms(db, user_id)

    if not company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Veuillez d'abord configurer les informations de votre entreprise",
        )

    lines_data = [
        {"quantity": li.quantity, "unit_price": li.unit_price, "vat_rate": li.vat_rate}
        for li in quote.line_items
    ]
    totals = calc_quote_totals(lines_data)

    template = jinja_env.get_template("quote_pdf.html")
    html_content = template.render(
        quote=quote,
        company=company,
        banking=banking,
        insurance=insurance,
        terms=terms,
        totals=totals,
        logo_src=await logo_data_uri(company.logo_path),
    )

    if not WEASYPRINT_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="WeasyPrint non disponible. Installez-le pour générer des PDF.",
        )

    return HTML(string=html_content).write_pdf()


async def generate_quote_pdf(db: AsyncSession, user_id: int, quote_id: int) -> StreamingResponse:
    pdf_bytes = await generate_pdf_bytes(db, user_id, quote_id)
    buffer = BytesIO(pdf_bytes)

    quote = await get_quote(db, user_id, quote_id)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="devis-{quote.reference}.pdf"'},
    )
