import time

from openai import AsyncOpenAI

from app.config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def transcribe_audio(audio_data: bytes, filename: str = "audio.webm") -> dict:
    """Transcribe audio using OpenAI Whisper API.

    Returns dict with 'text' and 'duration_ms'.
    """
    start = time.time()

    transcript = await client.audio.transcriptions.create(
        model="whisper-1",
        file=(filename, audio_data),
        language="fr",
        response_format="text",
    )

    duration_ms = int((time.time() - start) * 1000)

    return {
        "text": transcript.strip() if isinstance(transcript, str) else transcript.text.strip(),
        "duration_ms": duration_ms,
    }
