import base64
import logging
import time

import openai
from openai import AsyncOpenAI

from app.config import settings
from app.core.exceptions import AppException
from app.core.i18n import t
from app.features.quote.ai_parser import openai_error

logger = logging.getLogger(__name__)

# Bounded wait: the default client waits up to 600 s with 2 retries
client = AsyncOpenAI(
    api_key=settings.llm_api_key,
    base_url=settings.LLM_API_URL,
    timeout=30,
    max_retries=1,
)

# Inline audio is base64-encoded in the request body, which inflates it by ~33 %.
# 20 MB of source audio stays under the provider's 25 MB request ceiling once encoded.
MAX_AUDIO_SIZE = 20 * 1024 * 1024

# File extension -> `format` tag expected by the OpenAI-compatible
# `input_audio` part.
#
# Deliberately NOT derived from `mimetypes.guess_type`: that module reads the
# system MIME registry, so the same file name resolves differently per platform.
# It cost a CI failure — `memo.m4a` mapped to `m4a` on Windows but to `mp4` on
# Ubuntu, where /etc/mime.types declares `audio/mp4` for that extension. An
# explicit table is deterministic everywhere.
AUDIO_FORMATS = {
    "webm": "webm",
    "ogg": "ogg",
    "oga": "ogg",
    "opus": "ogg",
    "mp3": "mp3",
    "mpga": "mp3",
    "mp4": "mp4",
    "m4a": "m4a",
    "wav": "wav",
    "flac": "flac",
    "aac": "aac",
}
# What the browser's MediaRecorder produces in Chrome and Firefox, and the only
# path that reaches this function from the UI.
DEFAULT_AUDIO_FORMAT = "webm"

TRANSCRIPTION_PROMPT = (
    "Transcris fidèlement cet enregistrement en français. "
    "Ne renvoie que la transcription, sans commentaire, sans guillemets, "
    "sans préambule. Si l'enregistrement ne contient aucune parole, "
    "renvoie une chaîne vide."
)

# The transcription is dictated job descriptions, not an essay: a few hundred
# tokens is plenty, and the ceiling also covers the model's internal reasoning.
MAX_TRANSCRIPTION_TOKENS = 2000


def _audio_format(filename: str) -> str:
    """Derive the `input_audio` format tag from the uploaded file name.

    Extension-driven and case-insensitive; anything unknown falls back to webm.
    """
    suffix = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return AUDIO_FORMATS.get(suffix, DEFAULT_AUDIO_FORMAT)


async def transcribe_audio(
    audio_data: bytes, filename: str = "audio.webm", lang: str = "fr"
) -> dict:
    """Transcribe audio with the configured provider.

    Goes through `chat/completions` with an `input_audio` content part rather
    than `/audio/transcriptions`: Google's OpenAI-compatible layer does not
    expose that endpoint (verified — it answers 404), while the same model
    transcribes correctly when the audio is passed inline.

    Returns dict with 'text' and 'duration_ms'.
    """
    start = time.time()
    encoded = base64.b64encode(audio_data).decode("ascii")

    try:
        response = await client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": TRANSCRIPTION_PROMPT},
                        {
                            "type": "input_audio",
                            "input_audio": {
                                "data": encoded,
                                "format": _audio_format(filename),
                            },
                        },
                    ],
                }
            ],
            temperature=0,
            max_tokens=MAX_TRANSCRIPTION_TOKENS,
        )
    except openai.APIError as exc:
        logger.warning("Transcription call failed: %s: %s", type(exc).__name__, exc)
        raise openai_error(exc, lang) from exc

    choice = response.choices[0]
    text = (choice.message.content or "").strip()

    # A truncated transcription is worse than none: it would be parsed into quote
    # lines as if it were the whole dictation, silently dropping what the user said.
    if choice.finish_reason == "length":
        logger.warning("Transcription truncated by max_tokens (finish_reason=length)")
        raise AppException(t("ai.invalid_response", lang), code="AI_ERROR", status_code=502)

    duration_ms = int((time.time() - start) * 1000)

    return {"text": text, "duration_ms": duration_ms}
