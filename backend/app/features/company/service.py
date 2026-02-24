from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.company.models import Banking, Company, Insurance, Terms
from app.features.company.schemas import (
    BankingCreate,
    CompanyCreate,
    InsuranceCreate,
    TermsCreate,
)


async def get_or_create_company(db: AsyncSession, user_id: int, data: CompanyCreate) -> Company:
    result = await db.execute(select(Company).where(Company.user_id == user_id))
    company = result.scalar_one_or_none()
    if company:
        for key, value in data.model_dump().items():
            setattr(company, key, value)
    else:
        company = Company(user_id=user_id, **data.model_dump())
        db.add(company)
    await db.commit()
    await db.refresh(company)
    return company


async def get_company(db: AsyncSession, user_id: int) -> Company | None:
    result = await db.execute(select(Company).where(Company.user_id == user_id))
    return result.scalar_one_or_none()


async def get_or_create_banking(db: AsyncSession, user_id: int, data: BankingCreate) -> Banking:
    result = await db.execute(select(Banking).where(Banking.user_id == user_id))
    banking = result.scalar_one_or_none()
    if banking:
        for key, value in data.model_dump().items():
            setattr(banking, key, value)
    else:
        banking = Banking(user_id=user_id, **data.model_dump())
        db.add(banking)
    await db.commit()
    await db.refresh(banking)
    return banking


async def get_banking(db: AsyncSession, user_id: int) -> Banking | None:
    result = await db.execute(select(Banking).where(Banking.user_id == user_id))
    return result.scalar_one_or_none()


async def get_or_create_insurance(db: AsyncSession, user_id: int, data: InsuranceCreate) -> Insurance:
    result = await db.execute(select(Insurance).where(Insurance.user_id == user_id))
    insurance = result.scalar_one_or_none()
    if insurance:
        for key, value in data.model_dump().items():
            setattr(insurance, key, value)
    else:
        insurance = Insurance(user_id=user_id, **data.model_dump())
        db.add(insurance)
    await db.commit()
    await db.refresh(insurance)
    return insurance


async def get_insurance(db: AsyncSession, user_id: int) -> Insurance | None:
    result = await db.execute(select(Insurance).where(Insurance.user_id == user_id))
    return result.scalar_one_or_none()


async def get_or_create_terms(db: AsyncSession, user_id: int, data: TermsCreate) -> Terms:
    result = await db.execute(select(Terms).where(Terms.user_id == user_id))
    terms = result.scalar_one_or_none()
    if terms:
        for key, value in data.model_dump().items():
            setattr(terms, key, value)
    else:
        terms = Terms(user_id=user_id, **data.model_dump())
        db.add(terms)
    await db.commit()
    await db.refresh(terms)
    return terms


async def get_terms(db: AsyncSession, user_id: int) -> Terms | None:
    result = await db.execute(select(Terms).where(Terms.user_id == user_id))
    return result.scalar_one_or_none()


async def update_logo_path(db: AsyncSession, user_id: int, path: str) -> Company | None:
    result = await db.execute(select(Company).where(Company.user_id == user_id))
    company = result.scalar_one_or_none()
    if company:
        company.logo_path = path
        await db.commit()
        await db.refresh(company)
    return company
