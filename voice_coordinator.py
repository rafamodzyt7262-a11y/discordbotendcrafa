import os
import time
import asyncio
import logging
from pathlib import Path
import edge_tts
import discord

logger = logging.getLogger("VoiceCoordinator")

TEMP_AUDIO_DIR = Path(__file__).resolve().parent / "temp_audio"
TEMP_AUDIO_DIR.mkdir(parents=True, exist_ok=True)


async def speak_text(voice_client: discord.VoiceClient, text: str, voice_name: str, speaker_id: str = "bot") -> bool:
    """Genera audio con Edge-TTS y lo reproduce en el canal de voz de Discord."""
    if voice_client is None or not voice_client.is_connected():
        logger.warning(f"[{speaker_id}] No se puede reproducir audio: voice_client no está conectado.")
        return False

    temp_file = TEMP_AUDIO_DIR / f"{speaker_id}_{int(time.time() * 1000)}.mp3"
    try:
        logger.info(f"\033[95m🗣️ [{speaker_id}] Diciendo:\033[0m \"{text}\"")

        # Generar archivo de audio con voz neuronal realista
        communicate = edge_tts.Communicate(text, voice_name)
        await communicate.save(str(temp_file))

        if not temp_file.exists():
            return False

        # Si había otro audio en reproducción, detenerlo
        if voice_client.is_playing():
            voice_client.stop()

        # Reproducir a través de Discord
        audio_source = discord.FFmpegPCMAudio(str(temp_file))
        voice_client.play(audio_source)

        # Esperar activamente a que termine de hablar
        while voice_client.is_playing():
            await asyncio.sleep(0.3)

        return True

    except Exception as e:
        logger.error(f"[{speaker_id}] Error reproduciendo voz: {e}")
        return False
    finally:
        # Limpieza de archivo temporal
        try:
            if temp_file.exists():
                temp_file.unlink()
        except Exception:
            pass
