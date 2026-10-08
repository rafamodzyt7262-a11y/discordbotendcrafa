import time
import asyncio
import logging
import discord
from discord.enums import SpeakingState
from voice_coordinator import speak_text

logger = logging.getLogger("VoiceListener")


class VoiceInteractionManager:
    """Detecta cuando un usuario real habla por micrófono en el canal de voz y responde."""

    def __init__(self, conv_manager, music_manager):
        self.conv_manager = conv_manager
        self.music_manager = music_manager
        self.last_triggered_time = 0
        self.cooldown_seconds = 18.0  # Cooldown para no saturar al usuario
        self.is_responding = False

    async def handle_human_speaking(self, bot_client, member: discord.Member, vc, voice_name: str, bot_name: str):
        if member is None or getattr(member, "bot", False):
            return

        now = time.time()
        # Verificar cooldown
        if (now - self.last_triggered_time) < self.cooldown_seconds:
            return

        # Si ya está respondiendo o hay música sonando, no interrumpir
        if self.is_responding or self.music_manager.is_playing_music:
            return

        self.last_triggered_time = now
        self.is_responding = True
        logger.info(f"\033[93m🎙️ [Detector de Voz] ¡Usuario real hablando ({member.display_name})!\033[0m")

        try:
            # Pausar la conversación automática entre los bots
            self.conv_manager.pause()

            # Detener si un bot estaba hablando en ese milisegundo
            if vc.is_playing():
                vc.stop()

            await asyncio.sleep(0.5)

            # Responder con la voz en el canal: "Dime, ¿qué quieres que ponga?"
            frase_voz = "Dime, ¿qué quieres que ponga?"
            await speak_text(vc, frase_voz, voice_name, speaker_id=bot_name)

            # Notificar en el canal de texto para guiar al usuario
            guild = vc.guild
            text_channel = None
            for ch in guild.text_channels:
                if ch.permissions_for(guild.me).send_messages:
                    text_channel = ch
                    break

            if text_channel:
                await text_channel.send(
                    f"🎙️ **[{bot_name}]:** ¡Te escuché {member.mention}! **Dime, ¿qué quieres que ponga?**\n"
                    f"*(Pídeme: 'pon makabelico', 'pon musica random', o la canción que quieras)*"
                )

        except Exception as e:
            logger.error(f"Error al responder a voz humana: {e}")
        finally:
            self.is_responding = False
