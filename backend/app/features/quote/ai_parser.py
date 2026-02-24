import json

from openai import AsyncOpenAI

from app.config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

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
- Si aucune info client n'est détectée, mets null pour tout l'objet client"""

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
                        "description": "Titre court du devis résumant les travaux (ex: 'Travaux de carrelage', 'Rénovation cuisine')",
                    },
                    "line_items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "description": {"type": "string"},
                                "unit": {"type": "string", "enum": ["u", "m²", "m", "h", "kg", "forfait"]},
                                "quantity": {"type": "number"},
                                "unit_price": {"type": "number"},
                                "vat_rate": {"type": "number", "enum": [5.5, 10.0, 20.0]},
                            },
                            "required": ["description", "unit", "quantity", "unit_price", "vat_rate"],
                        },
                    },
                    "client": {
                        "type": ["object", "null"],
                        "description": "Informations client extraites du texte, null si aucune info détectée",
                        "properties": {
                            "name": {"type": ["string", "null"], "description": "Nom complet du client"},
                            "address": {"type": ["string", "null"], "description": "Adresse complète"},
                            "email": {"type": ["string", "null"], "description": "Adresse email"},
                            "phone": {"type": ["string", "null"], "description": "Numéro de téléphone"},
                        },
                    },
                },
                "required": ["title", "line_items", "client"],
            },
        },
    }
]


async def parse_text_to_line_items(text: str) -> dict:
    """Parse French BTP text into structured line items and client info using OpenAI function calling."""
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        tools=TOOLS,
        tool_choice={"type": "function", "function": {"name": "create_quote_data"}},
        temperature=0.1,
    )

    tool_call = response.choices[0].message.tool_calls
    if not tool_call:
        return {"line_items": [], "client": None}

    args = json.loads(tool_call[0].function.arguments)
    return {
        "title": args.get("title", ""),
        "line_items": args.get("line_items", []),
        "client": args.get("client"),
    }
