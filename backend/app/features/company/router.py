from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
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
@router.post("/logo", response_model=CompanyResponse)
async def upload_logo(
    file: UploadFile,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Le fichier doit être une image")

    content = await file.read()
    if len(content) > 2 * 1024 * 1024:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image trop volumineuse (max 2 Mo)")

    path = await storage.save(content, file.filename or "logo.png", folder="logos")
    company = await update_logo_path(db, user.id, path)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Créez d'abord les informations entreprise")
    return company
