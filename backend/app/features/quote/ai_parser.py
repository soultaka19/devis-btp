import json
import logging
import math

import openai
from email_validator import EmailNotValidError, validate_email
from openai import AsyncOpenAI

from app.config import settings
from app.core.exceptions import AppException
from app.core.i18n import t
from app.features.quote.calculator import VALID_VAT_RATES

logger = logging.getLogger(__name__)

# Bounded wait: the default client waits up to 600 s with 2 retries
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY, timeout=30, max_retries=1)

MAX_COMPLETION_TOKENS = 2000

# Units accepted by the tool schema, plus the "m2" spelling used by the frontend selector
ALLOWED_UNITS = ("u", "m²", "m2", "m", "h", "kg", "forfait")
DEFAULT_UNIT = "u"
DEFAULT_VAT_RATE = 20.0
CLIENT_FIELDS = ("name", "address", "email", "phone")

SYSTEM_PROMPT = """Tu es un assistant spécialisé dans l'extraction de devis BTP à partir de texte en français.

À partir du texte fourni, extrais :
1. Un **titre court** pour le devis (ex: "Travaux de carrelage", "Rénovation salle de bain", "Peinture appartement")
2. Les **lignes de devis** (postes de travail)
3. Les **informations client** si elles sont mentionnées (nom, adresse, email, téléphone)

Pour chaque ligne de devis :
- description: description du poste de travail
- unit: unité (u, m², m, h, kg, forfait)
- quantity: quantité (nombre)
- unit_price: prix unitaire HT en euros
- vat_rate: taux de TVA (5.5, 10.0, ou 20.0). Par défaut 10.0 pour la rénovation, 20.0 pour le neuf.

Règles lignes de devis :
- Si le prix n'est pas précisé, mets 0
- Si la quantité n'est pas précisée, mets 1
- Interprète le français approximatif (oral, abréviations artisans)
- "robinet" = fourniture + pose, "carrelage" = m², "peinture" = m², "câblage" = m
- Sépare fourniture et main d'œuvre quand c'est clair

Règles informations client :
- Extrais le nom complet (M., Mme, etc. + nom de famille)
- Extrais l'adresse complète si mentionnée (numéro, rue, ville, code postal, province/pays)
- Extrais l'email si mentionné — cherche tout texte qui ressemble à une adresse email (contient @)
- Extrais le téléphone si mentionné
- IMPORTANT : si le texte contient une adresse email (avec @), tu DOIS l'extraire dans le champ client.email
- Si une info client n'est pas présente dans le texte, mets null pour ce champ
- Si aucune info client n'est détectée, mets null pour tout l'objet client"""  # noqa: E501

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_quote_data",
            "description": "Crée les lignes de devis et les informations client extraites du texte",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": (
                            "Titre court du devis résumant les travaux "
                            "(ex: 'Travaux de carrelage', 'Rénovation cuisine')"
                        ),
                    },
                    "line_items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "description": {"type": "string"},
                                "unit": {
                                    "type": "string",
                                    "enum": ["u", "m²", "m", "h", "kg", "forfait"],
                                },
                                "quantity": {"type": "number"},
                                "unit_price": {"type": "number"},
                                "vat_rate": {"type": "number", "enum": [5.5, 10.0, 20.0]},
                            },
                            "required": [
                                "description",
                                "unit",
                                "quantity",
                                "unit_price",
                                "vat_rate",
                            ],
                        },
                    },
                    "client": {
                        "type": ["object", "null"],
                        "description": (
                            "Informations client extraites du texte, null si aucune info détectée"
                        ),
                        "properties": {
                            "name": {
                                "type": ["string", "null"],
                                "description": "Nom complet du client",
                            },
                            "address": {
                                "type": ["string", "null"],
                                "description": "Adresse complète",
                            },
                            "email": {"type": ["string", "null"], "description": "Adresse email"},
                            "phone": {
                                "type": ["string", "null"],
                                "description": "Numéro de téléphone",
                            },
                        },
                    },
                },
                "required": ["title", "line_items", "client"],
            },
        },
    }
]


def openai_error(exc: openai.APIError, lang: str = "fr") -> AppException:
    """Map an OpenAI client error to a clean 502/503 AppException (never a generic 500)."""
    if isinstance(
        exc, openai.APIConnectionError | openai.RateLimitError | openai.InternalServerError
    ):
        # Network / timeout / quota / OpenAI-side outage: temporary, retryable
        return AppException(t("ai.unavailable", lang), code="AI_UNAVAILABLE", status_code=503)
    # Any other upstream error (invalid API key, bad request, ...)
    return AppException(t("ai.error", lang), code="AI_ERROR", status_code=502)


def _to_float(value: object, default: float) -> float:
    try:
        number = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default
    if math.isnan(number) or math.isinf(number):
        return default
    return number


def _sanitize_line_item(raw: object) -> dict | None:
    """Coerce a tool-call line item into values accepted by LineItemCreate."""
    if not isinstance(raw, dict):
        return None

    quantity = _to_float(raw.get("quantity"), 1.0)
    if quantity <= 0:
        quantity = 1.0

    unit_price = _to_float(raw.get("unit_price"), 0.0)
    if unit_price < 0:
        unit_price = 0.0

    vat_rate = _to_float(raw.get("vat_rate"), DEFAULT_VAT_RATE)
    vat_rate = min(VALID_VAT_RATES, key=lambda rate: abs(rate - vat_rate))

    unit = str(raw.get("unit") or "").strip().lower()
    if unit not in ALLOWED_UNITS:
        unit = DEFAULT_UNIT

    return {
        "description": str(raw.get("description") or "").strip(),
        "unit": unit,
        "quantity": quantity,
        "unit_price": unit_price,
        "vat_rate": vat_rate,
    }


def _sanitize_client(raw: object) -> dict | None:
    """Keep only the known client fields as non-empty strings; drop an invalid email."""
    if not isinstance(raw, dict):
        return None
    client_info: dict[str, str | None] = {}
    for field in CLIENT_FIELDS:
        value = raw.get(field)
        text = str(value).strip() if value is not None else ""
        client_info[field] = text or None
    if client_info["email"]:
        try:
            client_info["email"] = validate_email(
                client_info["email"], check_deliverability=False
            ).normalized
        except EmailNotValidError:
            client_info["email"] = None
    if not any(client_info.values()):
        return None
    return client_info


def sanitize_parsed_data(args: dict) -> dict:
    """Validate the model output: the tool schema is not enforced by the API (no strict mode)."""
    raw_items = args.get("line_items")
    line_items = []
    if isinstance(raw_items, list):
        for raw in raw_items:
            item = _sanitize_line_item(raw)
            if item is not None:
                line_items.append(item)
    title = args.get("title")
    return {
        "title": str(title).strip() if isinstance(title, str) else "",
        "line_items": line_items,
        "client": _sanitize_client(args.get("client")),
    }


async def parse_text_to_line_items(text: str, lang: str = "fr") -> dict:
    """Parse French BTP text into line items and client info (OpenAI function calling)."""
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            tools=TOOLS,
            tool_choice={"type": "function", "function": {"name": "create_quote_data"}},
            temperature=0.1,
            max_tokens=MAX_COMPLETION_TOKENS,
        )
    except openai.APIError as exc:
        logger.warning("OpenAI parse-text call failed: %s: %s", type(exc).__name__, exc)
        raise openai_error(exc, lang) from exc

    tool_call = response.choices[0].message.tool_calls
    if not tool_call:
        return {"title": "", "line_items": [], "client": None}

    try:
        args = json.loads(tool_call[0].function.arguments)
    except (json.JSONDecodeError, TypeError) as exc:
        logger.warning("OpenAI tool call returned invalid JSON: %s", exc)
        raise AppException(
            t("ai.invalid_response", lang), code="AI_ERROR", status_code=502
        ) from exc
    if not isinstance(args, dict):
        raise AppException(t("ai.invalid_response", lang), code="AI_ERROR", status_code=502)

    return sanitize_parsed_data(args)
