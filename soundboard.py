import os
import asyncio
import logging
from pathlib import Path
import discord

logger = logging.getLogger("Soundboard")

SOUNDS_DIR = Path(__file__).resolve().parent / "assets" / "sounds"
SOUNDS_DIR.mkdir(parents=True, exist_ok=True)


async def play_sound_effect(voice_client: discord.VoiceClient, sound_name: str) -> bool:
    """Reproduce un efecto de sonido (nextel, balazo, fierro, risas, booyah) en el canal de voz."""
    if voice_client is None or not voice_client.is_connected():
        return False

    sound_name = sound_name.lower().strip()
    sound_file = None

    if "nextel" in sound_name or "radio" in sound_name:
        sound_file = SOUNDS_DIR / "nextel.wav"
    elif "balazo" in sound_name or "disparo" in sound_name or "tiro" in sound_name or "ak" in sound_name:
        sound_file = SOUNDS_DIR / "balazo.mp3"
    elif "fierro" in sound_name or "belico" in sound_name:
        sound_file = SOUNDS_DIR / "fierro.mp3"
    elif "risa" in sound_name or "jaja" in sound_name:
        sound_file = SOUNDS_DIR / "risas.mp3"
    elif "booyah" in sound_name or "victoria" in sound_name:
        sound_file = SOUNDS_DIR / "booyah.mp3"

    if not sound_file or not sound_file.exists():
        logger.warning(f"Efecto de sonido no encontrado: {sound_name}")
        return False

    try:
        if voice_client.is_playing():
            voice_client.stop()

        source = discord.FFmpegPCMAudio(str(sound_file))
        voice_client.play(source)

        while voice_client.is_playing():
            await asyncio.sleep(0.1)

        return True
    except Exception as e:
        logger.error(f"Error reproduciendo efecto de sonido '{sound_name}': {e}")
        return False
