"""End-to-end API tests against a dedicated PostgreSQL database.

Run with (the database must exist and be empty or disposable):

    TEST_DATABASE_URL=postgresql+asyncpg://postgres@127.0.0.1:5432/devis_btp_test pytest -q

The whole module is skipped when TEST_DATABASE_URL is not set. The LLM provider is
never called: the parse-text tests monkeypatch the client.
"""

import io
import json
import os
import shutil
import sys
import tempfile
import uuid
from types import SimpleNamespace

import httpx
import openai
import pytest
import pytest_asyncio
from PIL import Image

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")
if not TEST_DATABASE_URL:
    pytest.skip("TEST_DATABASE_URL non défini", allow_module_level=True)

# The settings are read once at import time: point the app at the test database
# and at a temporary upload folder before importing it.
if "app.config" in sys.modules:  # pragma: no cover - defensive
    raise RuntimeError("app.config was imported before test_api.py configured the environment")
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
UPLOAD_DIR = tempfile.mkdtemp(prefix="devis-test-uploads-")
os.environ["STORAGE_LOCAL_PATH"] = UPLOAD_DIR
os.environ.setdefault("LLM_API_KEY", "test-key-not-used")

from app.config import settings  # noqa: E402
from app.database import Base, engine  # noqa: E402
from app.features.quote import ai_parser  # noqa: E402
from app.main import app  # noqa: E402

pytestmark = pytest.mark.asyncio(loop_scope="module")

PASSWORD = "Test-Password-123"


def unique_email(prefix: str = "user") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:10]}@example.com"


def png_bytes() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (32, 20), (21, 101, 192)).save(buffer, format="PNG")
    return buffer.getvalue()


class FakeCompletions:
    """Stand-in for client.chat.completions returning a canned tool call (or raising)."""

    def __init__(self, arguments: str | None = None, error: Exception | None = None):
        self.arguments = arguments
        self.error = error
        self.calls: list[dict] = []

    async def create(self, **kwargs):
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        tool_call = SimpleNamespace(function=SimpleNamespace(arguments=self.arguments))
        message = SimpleNamespace(tool_calls=[tool_call])
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def fake_openai_client(completions: FakeCompletions):
    return SimpleNamespace(chat=SimpleNamespace(completions=completions))


@pytest_asyncio.fixture(loop_scope="module", scope="module")
async def client():
    # httpx's ASGITransport does not run the lifespan: create the schema here
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    await engine.dispose()
    shutil.rmtree(UPLOAD_DIR, ignore_errors=True)


async def register_and_login(client: httpx.AsyncClient, email: str) -> dict:
    r = await client.post(
        "/auth/register", json={"email": email, "password": PASSWORD, "full_name": "Test User"}
    )
    assert r.status_code == 201, r.text
    r = await client.post("/auth/login", json={"email": email, "password": PASSWORD})
    assert r.status_code == 200, r.text
    tokens = r.json()
    return {"tokens": tokens, "headers": {"Authorization": f"Bearer {tokens['access_token']}"}}


@pytest_asyncio.fixture(loop_scope="module", scope="module")
async def user_a(client):
    return await register_and_login(client, unique_email("alice"))


@pytest_asyncio.fixture(loop_scope="module", scope="module")
async def user_b(client):
    return await register_and_login(client, unique_email("bob"))


# --- Auth -----------------------------------------------------------------------------------


async def test_register_login_me(client):
    email = unique_email("reg")
    r = await client.post(
        "/auth/register", json={"email": email, "password": PASSWORD, "full_name": "Reg User"}
    )
    assert r.status_code == 201
    assert r.json()["email"] == email

    r = await client.post(
        "/auth/register", json={"email": email, "password": PASSWORD, "full_name": "X"}
    )
    assert r.status_code == 409

    r = await client.post("/auth/login", json={"email": email, "password": PASSWORD})
    assert r.status_code == 200
    tokens = r.json()
    assert tokens["token_type"] == "bearer"

    r = await client.get("/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert r.status_code == 200
    assert r.json() == {"id": r.json()["id"], "email": email, "full_name": "Reg User"}

    r = await client.get("/auth/me")
    assert r.status_code == 401
    r = await client.post("/auth/login", json={"email": email, "password": "wrong-password"})
    assert r.status_code == 401


async def test_refresh_token(client, user_a):
    r = await client.post(
        "/auth/refresh", json={"refresh_token": user_a["tokens"]["refresh_token"]}
    )
    assert r.status_code == 200
    new_access = r.json()["access_token"]
    r = await client.get("/auth/me", headers={"Authorization": f"Bearer {new_access}"})
    assert r.status_code == 200

    # An access token is not accepted as a refresh token
    r = await client.post("/auth/refresh", json={"refresh_token": user_a["tokens"]["access_token"]})
    assert r.status_code == 401


@pytest.mark.parametrize(
    "password",
    ["", "short", "a" * 80, "é" * 40],  # empty, < 8 chars, > 72 chars, > 72 bytes (bcrypt limit)
)
async def test_register_rejects_invalid_password(client, password):
    r = await client.post(
        "/auth/register", json={"email": unique_email("pw"), "password": password, "full_name": "X"}
    )
    assert r.status_code == 422


# --- Company --------------------------------------------------------------------------------


async def test_company_info_round_trip(client, user_a, user_b):
    r = await client.get("/company/info", headers=user_a["headers"])
    assert r.status_code == 200
    assert r.json() is None

    payload = {
        "name": "Dupont BTP",
        "siret": "123 456 789 01234",
        "address": "15 rue des Artisans",
        "city": "Lyon",
        "postal_code": "69003",
        "phone": "0472334455",
        "email": "contact@example.com",
    }
    r = await client.put("/company/info", headers=user_a["headers"], json=payload)
    assert r.status_code == 200, r.text
    assert r.json()["siret"] == "12345678901234"

    r = await client.get("/company/info", headers=user_a["headers"])
    assert r.status_code == 200
    body = r.json()
    assert {k: body[k] for k in payload if k != "siret"} == {
        k: v for k, v in payload.items() if k != "siret"
    }
    assert body["logo_path"] is None

    # Company info is per user: another user has none, and a corrupted token is rejected
    r = await client.get("/company/info", headers=user_b["headers"])
    assert r.status_code == 200
    assert r.json() is None
    corrupted = {"Authorization": "Bearer " + user_a["tokens"]["access_token"][:-4] + "abcd"}
    r = await client.get("/company/info", headers=corrupted)
    assert r.status_code == 401


async def test_company_validation_matches_db_columns(client, user_a):
    base = {
        "name": "X",
        "siret": "12345678901234",
        "address": "a",
        "city": "b",
        "postal_code": "69003",
        "phone": "01",
        "email": "x@example.com",
    }
    r = await client.put(
        "/company/info", headers=user_a["headers"], json={**base, "postal_code": "1" * 15}
    )
    assert r.status_code == 422
    r = await client.put("/company/info", headers=user_a["headers"], json={**base, "siret": "123"})
    assert r.status_code == 422


async def test_logo_upload_validates_real_image(client, user_a):
    html = b"<html><script>alert(1)</script></html>"
    r = await client.post(
        "/company/logo", headers=user_a["headers"], files={"file": ("evil.png", html, "image/png")}
    )
    assert r.status_code == 400

    r = await client.post(
        "/company/logo",
        headers=user_a["headers"],
        files={"file": ("logo.html", png_bytes(), "image/png")},
    )
    assert r.status_code == 200, r.text
    logo_path = r.json()["logo_path"]
    assert logo_path.startswith("logos/") and logo_path.endswith(".png")

    # Served by the API under /uploads
    r = await client.get(f"/uploads/{logo_path}")
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"


# --- Quotes ---------------------------------------------------------------------------------


async def test_create_quote_computes_totals(client, user_a):
    payload = {
        "client_name": "M. Martin",
        "client_email": "martin@example.com",
        "title": "Rénovation salle de bain",
        "line_items": [
            {
                "description": "Carrelage",
                "unit": "m²",
                "quantity": 20,
                "unit_price": 45.5,
                "vat_rate": 10,
            },
            {
                "description": "Main d'oeuvre",
                "unit": "h",
                "quantity": 3,
                "unit_price": 50,
                "vat_rate": 20,
            },
        ],
    }
    r = await client.post("/quotes", headers=user_a["headers"], json=payload)
    assert r.status_code == 201, r.text
    quote = r.json()
    assert quote["reference"].startswith("DEV-")
    assert quote["status"] == "draft"
    assert [li["total_ht"] for li in quote["line_items"]] == [910.0, 150.0]
    assert quote["subtotal_ht"] == 1060.0
    assert quote["total_vat"] == 121.0  # 91 (10 %) + 30 (20 %)
    assert quote["total_ttc"] == 1181.0

    r = await client.get(f"/quotes/{quote['id']}", headers=user_a["headers"])
    assert r.status_code == 200
    assert r.json()["total_ttc"] == 1181.0

    r = await client.get("/quotes", headers=user_a["headers"])
    assert r.status_code == 200
    assert any(q["id"] == quote["id"] for q in r.json())


async def test_quote_validation(client, user_a):
    bad_line = {"description": "x", "quantity": -5, "unit_price": -10, "vat_rate": 99}
    r = await client.post("/quotes", headers=user_a["headers"], json={"line_items": [bad_line]})
    assert r.status_code == 422
    errors = {tuple(e["loc"][-1:]) for e in r.json()["detail"]}
    assert {("quantity",), ("unit_price",), ("vat_rate",)} <= errors

    r = await client.post("/quotes", headers=user_a["headers"], json={"client_phone": "0" * 25})
    assert r.status_code == 422
    r = await client.post(
        "/quotes", headers=user_a["headers"], json={"client_email": "not-an-email"}
    )
    assert r.status_code == 422
    r = await client.post("/quotes", headers=user_a["headers"], json={"client_email": ""})
    assert r.status_code == 201
    r = await client.get("/quotes?limit=-1&skip=-5", headers=user_a["headers"])
    assert r.status_code == 422


async def test_get_quote_of_another_user_is_404(client, user_a, user_b):
    r = await client.post("/quotes", headers=user_a["headers"], json={"title": "Privé"})
    assert r.status_code == 201
    quote_id = r.json()["id"]

    r = await client.get(f"/quotes/{quote_id}", headers=user_b["headers"])
    assert r.status_code == 404
    r = await client.put(f"/quotes/{quote_id}", headers=user_b["headers"], json={"title": "hack"})
    assert r.status_code == 404
    r = await client.delete(f"/quotes/{quote_id}", headers=user_b["headers"])
    assert r.status_code == 404


async def test_generate_pdf(client, user_a):
    r = await client.post(
        "/quotes",
        headers=user_a["headers"],
        json={
            "client_name": "<b>Mme</b> Durand",
            "title": "Peinture",
            "line_items": [
                {"description": "Peinture murs", "unit": "m²", "quantity": 40, "unit_price": 12}
            ],
        },
    )
    assert r.status_code == 201
    quote_id = r.json()["id"]

    r = await client.post(f"/quotes/{quote_id}/generate-pdf", headers=user_a["headers"])
    assert r.status_code == 200, r.text
    assert r.headers["content-type"] == "application/pdf"
    assert r.content.startswith(b"%PDF")
    assert len(r.content) > 1000
    assert "attachment" in r.headers["content-disposition"]


async def test_pdf_template_escapes_html():
    # autoescape: user-provided values must not be interpreted as HTML by WeasyPrint
    from app.features.quote.pdf_generator import jinja_env

    rendered = jinja_env.from_string("{{ value }}").render(value="<b>x</b>")
    assert rendered == "&lt;b&gt;x&lt;/b&gt;"
    assert jinja_env.get_template("quote_pdf.html").environment.autoescape


# --- AI parsing (OpenAI monkeypatched) ------------------------------------------------------


async def test_parse_text_sanitizes_model_output(client, user_a, monkeypatch):
    garbage = {
        "title": "  Rénovation cuisine ",
        "line_items": [
            {
                "description": "Carrelage",
                "unit": "m²",
                "quantity": -3,
                "unit_price": -20,
                "vat_rate": 33,
            },
            {
                "description": "Pose",
                "unit": "jour",
                "quantity": "abc",
                "unit_price": 100,
                "vat_rate": 8,
            },
            {
                "description": "Robinet",
                "unit": "M2",
                "quantity": 2,
                "unit_price": 45,
                "vat_rate": 5.5,
            },
            "not-an-object",
        ],
        "client": {
            "name": " M. Martin ",
            "email": "pas-un-email",
            "phone": None,
            "extra": "ignored",
        },
    }
    completions = FakeCompletions(arguments=json.dumps(garbage))
    monkeypatch.setattr(ai_parser, "client", fake_openai_client(completions))

    r = await client.post(
        "/quotes/parse-text", headers=user_a["headers"], json={"text": "carrelage 20 m2"}
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["title"] == "Rénovation cuisine"
    assert body["line_items"] == [
        {
            "description": "Carrelage",
            "unit": "m²",
            "quantity": 1.0,
            "unit_price": 0.0,
            "vat_rate": 20.0,
        },
        {
            "description": "Pose",
            "unit": "u",
            "quantity": 1.0,
            "unit_price": 100.0,
            "vat_rate": 10.0,
        },
        {
            "description": "Robinet",
            "unit": "m2",
            "quantity": 2.0,
            "unit_price": 45.0,
            "vat_rate": 5.5,
        },
    ]
    assert body["client"] == {"name": "M. Martin", "address": None, "email": None, "phone": None}

    # Cost controls on the completion call. Both values come from configuration
    # rather than being repeated here: the model is provider-dependent, and the
    # token ceiling has to grow when the provider is a reasoning model, which
    # charges its hidden reasoning to the same budget.
    call = completions.calls[0]
    assert call["max_tokens"] == ai_parser.MAX_COMPLETION_TOKENS
    assert call["model"] == settings.LLM_MODEL


async def test_parse_text_openai_connection_error_is_503(client, user_a, monkeypatch):
    error = openai.APIConnectionError(
        request=httpx.Request("POST", "https://api.openai.com/v1/chat")
    )
    monkeypatch.setattr(ai_parser, "client", fake_openai_client(FakeCompletions(error=error)))

    r = await client.post(
        "/quotes/parse-text", headers=user_a["headers"], json={"text": "carrelage 20 m2"}
    )
    assert r.status_code == 503
    assert r.json() == {
        "detail": (
            "Service d'analyse IA temporairement indisponible, réessayez dans quelques instants."
        ),
        "code": "AI_UNAVAILABLE",
    }

    r = await client.post(
        "/quotes/parse-text",
        headers={**user_a["headers"], "Accept-Language": "en"},
        json={"text": "carrelage 20 m2"},
    )
    assert r.status_code == 503
    assert r.json()["code"] == "AI_UNAVAILABLE"
    assert r.json()["detail"].startswith("AI parsing service temporarily unavailable")


async def test_parse_text_openai_auth_error_is_502(client, user_a, monkeypatch):
    response = httpx.Response(401, request=httpx.Request("POST", "https://api.openai.com/v1/chat"))
    error = openai.AuthenticationError("Incorrect API key", response=response, body=None)
    monkeypatch.setattr(ai_parser, "client", fake_openai_client(FakeCompletions(error=error)))

    r = await client.post(
        "/quotes/parse-text", headers=user_a["headers"], json={"text": "carrelage 20 m2"}
    )
    assert r.status_code == 502
    assert r.json()["code"] == "AI_ERROR"


async def test_parse_text_invalid_tool_json_is_502(client, user_a, monkeypatch):
    monkeypatch.setattr(
        ai_parser, "client", fake_openai_client(FakeCompletions(arguments='{"title": "tronq'))
    )
    r = await client.post(
        "/quotes/parse-text", headers=user_a["headers"], json={"text": "carrelage 20 m2"}
    )
    assert r.status_code == 502
    assert r.json()["code"] == "AI_ERROR"


@pytest.mark.parametrize("text", ["", "   \n", "x" * 5001])
async def test_parse_text_rejects_empty_or_too_long_text(client, user_a, monkeypatch, text):
    completions = FakeCompletions(arguments="{}")
    monkeypatch.setattr(ai_parser, "client", fake_openai_client(completions))
    r = await client.post("/quotes/parse-text", headers=user_a["headers"], json={"text": text})
    assert r.status_code == 422
    assert completions.calls == []  # OpenAI is never called for invalid input


async def test_voice_to_text_rejects_non_audio_and_empty(client, user_a):
    r = await client.post(
        "/quotes/voice-to-text",
        headers=user_a["headers"],
        files={"file": ("a.txt", b"hello", "text/plain")},
    )
    assert r.status_code == 415
    r = await client.post(
        "/quotes/voice-to-text",
        headers=user_a["headers"],
        files={"file": ("a.webm", b"", "audio/webm")},
    )
    assert r.status_code == 422
