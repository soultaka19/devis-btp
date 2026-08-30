import logging
import time

import openai
from openai import AsyncOpenAI

from app.config import settings
from app.features.quote.ai_parser import openai_error

logger = logging.getLogger(__name__)

# Bounded wait: the default client waits up to 600 s with 2 retries
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY, timeout=30, max_retries=1)

# Whisper API limit
MAX_AUDIO_SIZE = 25 * 1024 * 1024


async def transcribe_audio(
    audio_data: bytes, filename: str = "audio.webm", lang: str = "fr"
) -> dict:
    """Transcribe audio using OpenAI Whisper API.

    Returns dict with 'text' and 'duration_ms'.
    """
    start = time.time()

    try:
        transcript = await client.audio.transcriptions.create(
            model="whisper-1",
            file=(filename, audio_data),
            language="fr",
            response_format="text",
        )
    except openai.APIError as exc:
        logger.warning("OpenAI transcription call failed: %s: %s", type(exc).__name__, exc)
        raise openai_error(exc, lang) from exc

    duration_ms = int((time.time() - start) * 1000)

    return {
        "text": transcript.strip() if isinstance(transcript, str) else transcript.text.strip(),
        "duration_ms": duration_ms,
    }
