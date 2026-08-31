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
    # Demo sandbox
    "demo.saturated": {
        "fr": (
            "Trop d'espaces de démonstration sont ouverts en ce moment. "
            "Chacun expire au bout d'une heure ; réessayez dans quelques minutes."
        ),
        "en": (
            "Too many demo spaces are open right now. "
            "Each one expires after an hour; try again in a few minutes."
        ),
    },
    "demo.rate_limited": {
        "fr": (
            "Vous avez ouvert plusieurs espaces de démonstration coup sur coup. "
            "Patientez quelques minutes avant d'en créer un nouveau."
        ),
        "en": (
            "You opened several demo spaces in a row. "
            "Please wait a few minutes before creating another one."
        ),
    },
    "demo.quota_exhausted": {
        "fr": (
            "Vous avez utilisé vos {n} essais de l'assistant. Les exemples fournis "
            "restent utilisables, et un nouvel espace de démonstration vous en "
            "redonnera autant."
        ),
        "en": (
            "You have used your {n} assistant attempts. The provided examples remain "
            "usable, and a new demo space will grant you as many again."
        ),
    },
    "demo.budget_daily": {
        "fr": (
            "Le budget quotidien de la démonstration est atteint. Les exemples déjà "
            "générés restent consultables ; réessayez demain."
        ),
        "en": (
            "The daily demo budget has been reached. Already generated examples remain "
            "available; try again tomorrow."
        ),
    },
    "demo.budget_monthly": {
        "fr": (
            "Le budget mensuel de la démonstration est atteint. Les exemples déjà "
            "générés restent consultables."
        ),
        "en": (
            "The monthly demo budget has been reached. Already generated examples remain available."
        ),
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
    # AI (OpenAI parsing / Whisper)
    "ai.unavailable": {
        "fr": "Service d'analyse IA temporairement indisponible, réessayez dans quelques instants.",
        "en": "AI parsing service temporarily unavailable, please try again in a moment.",
    },
    "ai.error": {
        "fr": "Erreur du service d'analyse IA.",
        "en": "AI parsing service error.",
    },
    "ai.invalid_response": {
        "fr": "Réponse invalide du service d'analyse IA.",
        "en": "Invalid response from the AI parsing service.",
    },
    "voice.empty_file": {
        "fr": "Le fichier audio est vide.",
        "en": "The audio file is empty.",
    },
    "voice.file_too_large": {
        "fr": "Fichier audio trop volumineux (max 25 Mo).",
        "en": "Audio file too large (max 25 MB).",
    },
    "voice.unsupported_type": {
        "fr": "Le fichier doit être un fichier audio.",
        "en": "The file must be an audio file.",
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
