from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.i18n import get_lang
from app.database import get_db
from app.features.auth.models import User
from app.features.auth.schemas import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.features.auth.service import authenticate_user, refresh_tokens, register_user

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(request: Request, data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user = await register_user(db, data, lang=get_lang(request))
    return user


@router.post("/login", response_model=TokenResponse)
async def login(request: Request, data: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await authenticate_user(db, data, lang=get_lang(request))


@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: Request, data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    return await refresh_tokens(db, data.refresh_token, lang=get_lang(request))


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)):
    return user
