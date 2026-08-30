"""Tests du service de transcription vocale.

Aucun appel réseau : le client du fournisseur est remplacé par une doublure.
"""

import os
from types import SimpleNamespace

import pytest

os.environ.setdefault("LLM_API_KEY", "test-key-not-used")

from app.core.exceptions import AppException  # noqa: E402
from app.features.quote import voice_service  # noqa: E402
from app.features.quote.voice_service import _audio_format, transcribe_audio  # noqa: E402


class FakeCompletions:
    """Doublure de client.chat.completions renvoyant un contenu et un finish_reason."""

    def __init__(self, content: str = "", finish_reason: str = "stop"):
        self.content = content
        self.finish_reason = finish_reason
        self.calls: list[dict] = []

    async def create(self, **kwargs):
        self.calls.append(kwargs)
        message = SimpleNamespace(content=self.content)
        choice = SimpleNamespace(message=message, finish_reason=self.finish_reason)
        return SimpleNamespace(choices=[choice])


def fake_client(completions: FakeCompletions):
    return SimpleNamespace(chat=SimpleNamespace(completions=completions))


@pytest.mark.parametrize(
    ("filename", "attendu"),
    [
        ("audio.webm", "webm"),
        ("dictee.mp3", "mp3"),
        ("memo.m4a", "m4a"),
        ("prise.wav", "wav"),
        ("bande.ogg", "ogg"),
        ("piste.flac", "flac"),
        # Inconnu ou sans extension : on retombe sur le format du navigateur,
        # seul chemin qui atteint réellement cette fonction depuis l'interface.
        ("enregistrement", "webm"),
        ("fichier.xyz", "webm"),
    ],
)
def test_audio_format_deduit_le_conteneur(filename, attendu):
    assert _audio_format(filename) == attendu


@pytest.mark.asyncio
async def test_transcription_renvoie_le_texte_et_la_duree(monkeypatch):
    completions = FakeCompletions(content="  Pose de carrelage 25 m2  ")
    monkeypatch.setattr(voice_service, "client", fake_client(completions))

    resultat = await transcribe_audio(b"donnees-audio", "audio.webm")

    assert resultat["text"] == "Pose de carrelage 25 m2"
    assert isinstance(resultat["duration_ms"], int)


@pytest.mark.asyncio
async def test_transcription_envoie_l_audio_en_ligne(monkeypatch):
    """L'audio part dans le message, encodé en base64 — et non vers
    /audio/transcriptions, que le fournisseur n'expose pas (vérifié : 404)."""
    completions = FakeCompletions(content="ok")
    monkeypatch.setattr(voice_service, "client", fake_client(completions))

    await transcribe_audio(b"abc", "memo.mp3")

    parts = completions.calls[0]["messages"][0]["content"]
    audio = next(p for p in parts if p["type"] == "input_audio")
    assert audio["input_audio"]["format"] == "mp3"
    # base64 de b"abc"
    assert audio["input_audio"]["data"] == "YWJj"


@pytest.mark.asyncio
async def test_transcription_tronquee_est_refusee(monkeypatch):
    """Une transcription coupée par max_tokens doit lever, pas être renvoyée.

    Elle serait sinon transformée en lignes de devis comme si elle était
    complète, en perdant silencieusement la fin de ce que l'artisan a dicté.
    """
    completions = FakeCompletions(content="Pose de carrelage 25 m2 dans la", finish_reason="length")
    monkeypatch.setattr(voice_service, "client", fake_client(completions))

    with pytest.raises(AppException) as exc:
        await transcribe_audio(b"donnees-audio", "audio.webm")

    assert exc.value.status_code == 502


@pytest.mark.asyncio
async def test_transcription_vide_est_acceptee(monkeypatch):
    """Un enregistrement sans parole rend une chaîne vide, pas une erreur."""
    completions = FakeCompletions(content="")
    monkeypatch.setattr(voice_service, "client", fake_client(completions))

    resultat = await transcribe_audio(b"silence", "audio.webm")

    assert resultat["text"] == ""
