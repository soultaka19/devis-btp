from fastapi import Request

TRANSLATIONS: dict[str, dict[str, str]] = {
    # Auth
    "auth.email_taken": {
        "fr": "Email déjà utilisé",
        "en": "Email already in use",
    },
    "auth.invalid_credentials": {
        "fr": "Identifiants invalides",
        "en": "Invalid credentials",
    },
    "auth.invalid_refresh_token": {
        "fr": "Refresh token invalide",
        "en": "Invalid refresh token",
    },
    "auth.user_not_found": {
        "fr": "Utilisateur introuvable",
        "en": "User not found",
    },
    "auth.invalid_token": {
        "fr": "Token invalide",
        "en": "Invalid token",
    },
    # Email
    "email.no_recipient": {
        "fr": "Aucune adresse email destinataire. Renseignez l'email du client.",
        "en": "No recipient email address. Please provide the client's email.",
    },
    "email.api_key_missing": {
        "fr": "Clé API Resend non configurée.",
        "en": "Resend API key not configured.",
    },
    "email.send_error": {
        "fr": "Erreur lors de l'envoi de l'email: {error}",
        "en": "Error sending email: {error}",
    },
    "email.subject": {
        "fr": "Devis {reference} - {company}",
        "en": "Quote {reference} - {company}",
    },
    "email.greeting": {
        "fr": "Bonjour {name},",
        "en": "Hello {name},",
    },
    "email.body": {
        "fr": "Veuillez trouver ci-joint le devis <strong>{reference}</strong>.",
        "en": "Please find attached the quote <strong>{reference}</strong>.",
    },
    "email.closing": {
        "fr": "Cordialement,<br>{company}",
        "en": "Best regards,<br>{company}",
    },
    "email.success": {
        "fr": "Devis {reference} envoyé par email à {email}",
        "en": "Quote {reference} sent by email to {email}",
    },
    "email.default_company": {
        "fr": "Votre artisan",
        "en": "Your contractor",
    },
    # General
    "error.internal": {
        "fr": "Erreur interne du serveur",
        "en": "Internal server error",
    },
}


def get_lang(request: Request) -> str:
    accept = request.headers.get("Accept-Language", "fr")
    lang = accept.split(",")[0].split("-")[0].strip().lower()
    return lang if lang in ("fr", "en") else "fr"


def t(key: str, lang: str = "fr", **kwargs: object) -> str:
    entry = TRANSLATIONS.get(key)
    if not entry:
        return key
    text = entry.get(lang, entry.get("fr", key))
    if kwargs:
        text = text.format(**kwargs)
    return text
