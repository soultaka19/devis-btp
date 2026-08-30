from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, status
from PIL import Image, UnidentifiedImageError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.storage import storage
from app.database import get_db
from app.features.auth.models import User
from app.features.company.schemas import (
    BankingCreate,
    BankingResponse,
    CompanyCreate,
    CompanyResponse,
    InsuranceCreate,
    InsuranceResponse,
    TermsCreate,
    TermsResponse,
)
from app.features.company.service import (
    get_banking,
    get_company,
    get_insurance,
    get_or_create_banking,
    get_or_create_company,
    get_or_create_insurance,
    get_or_create_terms,
    get_terms,
    update_logo_path,
)

router = APIRouter()

MAX_LOGO_SIZE = 2 * 1024 * 1024
# Pillow format name -> stored extension (only raster formats WeasyPrint/browsers render safely)
ALLOWED_LOGO_FORMATS = {"PNG": "png", "JPEG": "jpg", "WEBP": "webp"}


# --- Company Info ---
@router.get("/info", response_model=CompanyResponse | None)
async def get_company_info(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_company(db, user.id)


@router.put("/info", response_model=CompanyResponse)
async def upsert_company_info(
    data: CompanyCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_or_create_company(db, user.id, data)


# --- Banking ---
@router.get("/banking", response_model=BankingResponse | None)
async def get_banking_info(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_banking(db, user.id)


@router.put("/banking", response_model=BankingResponse)
async def upsert_banking(
    data: BankingCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_or_create_banking(db, user.id, data)


# --- Insurance ---
@router.get("/insurance", response_model=InsuranceResponse | None)
async def get_insurance_info(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_insurance(db, user.id)


@router.put("/insurance", response_model=InsuranceResponse)
async def upsert_insurance(
    data: InsuranceCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_or_create_insurance(db, user.id, data)


# --- Terms ---
@router.get("/terms", response_model=TermsResponse | None)
async def get_terms_info(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_terms(db, user.id)


@router.put("/terms", response_model=TermsResponse)
async def upsert_terms(
    data: TermsCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_or_create_terms(db, user.id, data)


# --- Logo ---
def _detect_image_format(content: bytes) -> str | None:
    """Return the Pillow format name of a valid image, or None if the bytes are not an image."""
    try:
        with Image.open(BytesIO(content)) as image:
            image.verify()
        # verify() invalidates the image object: reopen to read the format
        with Image.open(BytesIO(content)) as image:
            return image.format
    except (UnidentifiedImageError, Image.DecompressionBombError, OSError, ValueError):
        return None


@router.post("/logo", response_model=CompanyResponse)
async def upload_logo(
    request: Request,
    file: UploadFile,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Le fichier doit être une image"
        )

    # Reject oversized uploads before reading them fully into memory
    content_length = request.headers.get("content-length", "")
    if content_length.isdigit() and int(content_length) > MAX_LOGO_SIZE + 64 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="Image trop volumineuse (max 2 Mo)",
        )
    content = await file.read(MAX_LOGO_SIZE + 1)
    if len(content) > MAX_LOGO_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="Image trop volumineuse (max 2 Mo)",
        )

    # The declared content type can be spoofed: validate the actual bytes with Pillow
    image_format = _detect_image_format(content)
    extension = ALLOWED_LOGO_FORMATS.get(image_format or "")
    if not extension:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le fichier doit être une image PNG, JPEG ou WEBP valide",
        )

    # Store with the extension derived from the detected format, never from the client filename
    path = await storage.save(content, f"logo.{extension}", folder="logos")
    company = await update_logo_path(db, user.id, path)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Créez d'abord les informations entreprise",
        )
    return company
