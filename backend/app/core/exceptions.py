from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.core.i18n import get_lang, t


class AppException(Exception):
    def __init__(self, detail: str, code: str = "APP_ERROR", status_code: int = 400):
        self.detail = detail
        self.code = code
        self.status_code = status_code


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(_request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "code": exc.code},
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "code": "HTTP_ERROR"},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, _exc: Exception):
        lang = get_lang(request)
        return JSONResponse(
            status_code=500,
            content={"detail": t("error.internal", lang), "code": "INTERNAL_ERROR"},
        )
