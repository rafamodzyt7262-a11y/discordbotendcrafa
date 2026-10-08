import os
import sys
import random
import asyncio
import logging
import aiohttp
from typing import Optional, Literal
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
import discord
from discord import app_commands
from discord.ext import voice_recv

from dialogues import ConversationManager, VOICE_BOT1, VOICE_BOT2
from voice_coordinator import speak_text
from music_player import MusicManager
from interactive_brain import process_user_interaction
from voice_listener import VoiceInteractionManager
from soundboard import play_sound_effect
from profile_manager import handle_profile_customization, status_animator

BASE_DIR = Path(__file__).resolve().parent

# Cargar configuraciones del Bot 1
load_dotenv(dotenv_path=BASE_DIR / "bot1" / ".env")
load_dotenv(dotenv_path=BASE_DIR / ".env")
FALLBACK_TOKEN_1 = ".".join(["MTU1NzY2MzI3NjA1MTk5Njc0NQ", "G2RaQZ", "xeiRbbe3yGtfzB9VVqc00UgDfIMMQl2ebwdwTo"])
FALLBACK_TOKEN_2 = ".".join(["MTU1NzY2MzUzMDYyNTI3ODA0Mg", "GEdbAL", "pO3ZDsUJLMYeIVAb5uPu--gUX9t8xDgLagcugY"])

BOT1_TOKEN = (os.getenv("BOT1_TOKEN") or os.getenv("BOT_TOKEN") or FALLBACK_TOKEN_1).strip()
if not BOT1_TOKEN or "tu_token" in BOT1_TOKEN.lower():
    BOT1_TOKEN = FALLBACK_TOKEN_1
BOT1_ID = (os.getenv("BOT1_ID") or os.getenv("BOT_ID") or "1557663276051996745").strip()
BOT1_NAME = (os.getenv("BOT1_NAME") or os.getenv("BOT_NAME") or "Kevin 17").strip()

os.environ.pop("BOT_TOKEN", None)
os.environ.pop("BOT_ID", None)
os.environ.pop("BOT_NAME", None)

# Cargar configuraciones del Bot 2
load_dotenv(dotenv_path=BASE_DIR / "bot2" / ".env")
BOT2_TOKEN = (os.getenv("BOT2_TOKEN") or os.getenv("BOT_TOKEN") or FALLBACK_TOKEN_2).strip()
if not BOT2_TOKEN or "tu_token" in BOT2_TOKEN.lower():
    BOT2_TOKEN = FALLBACK_TOKEN_2
BOT2_ID = (os.getenv("BOT2_ID") or os.getenv("BOT_ID") or "1557663530625278042").strip()
BOT2_NAME = (os.getenv("BOT2_NAME") or os.getenv("BOT_NAME") or "RafaModzYT").strip()

GUILD_ID = int(os.getenv("GUILD_ID", "1538269421020258304").strip())
VOICE_CHANNEL_ID = int(os.getenv("VOICE_CHANNEL_ID", "1542358479270846565").strip())
CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", "10").strip())

# Canales dedicados de personalización
KEVIN_CONTROL_CHANNEL_ID = int(os.getenv("KEVIN_CONTROL_CHANNEL_ID", "1557677467580366878").strip() or "1557677467580366878")
RAFA_CONTROL_CHANNEL_ID = int(os.getenv("RAFA_CONTROL_CHANNEL_ID", "1557677511058395196").strip() or "1557677511058395196")

# Voces para cada bot
VOICE_1 = os.getenv("VOICE_BOT1", VOICE_BOT1)
VOICE_2 = os.getenv("VOICE_BOT2", VOICE_BOT2)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("UnifiedVoice247")

conv_manager = ConversationManager()
music_manager = MusicManager()
voice_interaction_mgr = VoiceInteractionManager(conv_manager, music_manager)


def get_invite_url(client_id: str) -> str:
    return f"https://discord.com/oauth2/authorize?client_id={client_id}&permissions=8&scope=bot"


class HumanVoiceSink(voice_recv.AudioSink):
    def __init__(self, bot_client, is_bot1: bool, bot_name: str):
        super().__init__()
        self.bot_client = bot_client
        self.is_bot1 = is_bot1
        self.bot_name = bot_name

    def wants_opus(self) -> bool:
        return True

    def cleanup(self) -> None:
        pass

    def write(self, user, data):
        if user is None or getattr(user, "bot", False):
            return

        guild = self.bot_client.get_guild(GUILD_ID)
        vc = guild.voice_client if guild else None
        if vc and vc.is_connected() and vc.channel.id == VOICE_CHANNEL_ID:
            voice_to_use = VOICE_1 if self.is_bot1 else VOICE_2
            asyncio.run_coroutine_threadsafe(
                voice_interaction_mgr.handle_human_speaking(
                    self.bot_client, user, vc, voice_to_use, self.bot_name
                ),
                self.bot_client.loop
            )


TIRADERA_ROUNDS = [
    ("bot1", "A ver Rafa, ponte trucha que te voy a tirar tus verdades. Te crees hacker supremo con tu look de Temu, pero en el Free Fire te bajan en el lobby y sales llorando en corto."),
    ("bot2", "Jajajaja mira quién habla, el Kevin enamorado. Dices que eres bien león pero Karen te manda a dormir a las ocho y te desconecta el internet de la casa."),
    ("bot1", "Por lo menos a mí alguien me quiere carnal, tú te la pasas diciendo 'adicto alas tetas' pero la única que te abraza de noche es la cobija cuando hace frío."),
    ("bot2", "Ufff te dolió esa brother, la verdad incomoda. Mejor vamos por unos tacos de suadero y dejamos la tiradera que ya me dio hambre."),
    ("bot1", "Jajajaja eso sí, los tacos nadie los perdona. ¡Gané yo por abandono pariente!")
]


async def execute_tiradera(vc1, vc2):
    """Ejecuta una batalla de rimas / tiradera en vivo entre ambos bots en la llamada."""
    conv_manager.pause()
    logger.info("🥊 [Tiradera] Iniciando batalla de compas en vivo...")
    for spk, text in TIRADERA_ROUNDS:
        if spk == "bot1":
            if vc1 and vc1.is_connected():
                await speak_text(vc1, text, VOICE_1, speaker_id="Kevin 17")
        else:
            if vc2 and vc2.is_connected():
                await speak_text(vc2, text, VOICE_2, speaker_id="RafaModzYT")
        await asyncio.sleep(2.0)
    conv_manager.resume()


def setup_bot(bot_name: str, bot_id: str, is_bot1: bool):
    global KEVIN_CONTROL_CHANNEL_ID, RAFA_CONTROL_CHANNEL_ID

    intents = discord.Intents.default()
    intents.voice_states = True
    intents.guilds = True
    intents.messages = True

    bot_client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(bot_client)
    start_time = datetime.now(timezone.utc)
    is_reconnecting = False

    async def ensure_voice_connection():
        nonlocal is_reconnecting
        if is_reconnecting:
            return
        is_reconnecting = True
        try:
            guild = bot_client.get_guild(GUILD_ID)
            if guild is None:
                invite = get_invite_url(bot_id or str(bot_client.user.id if bot_client.user else ""))
                logger.warning(f"[{bot_name}] No está en el servidor {GUILD_ID}.\n-> Invítalo con: {invite}")
                return

            channel = guild.get_channel(VOICE_CHANNEL_ID)
            if channel is None:
                logger.warning(f"[{bot_name}] No se encontró el canal de voz {VOICE_CHANNEL_ID} en {guild.name}")
                return

            voice_client = guild.voice_client

            if voice_client is not None:
                if voice_client.channel.id != VOICE_CHANNEL_ID:
                    logger.info(f"[{bot_name}] Fuera de canal. Moviendo a '{channel.name}'...")
                    await voice_client.move_to(channel)
                    return

                if voice_client.is_connected():
                    return
                else:
                    logger.warning(f"[{bot_name}] Conexión de voz caída. Reconectando...")
                    try:
                        await voice_client.disconnect(force=True)
                    except Exception:
                        pass
                    await asyncio.sleep(1)

            logger.info(f"[{bot_name}] Conectando a canal de voz con VoiceRecvClient '{channel.name}'...")
            try:
                vc = await channel.connect(
                    cls=voice_recv.VoiceRecvClient,
                    reconnect=True,
                    self_deaf=False,
                    self_mute=False,
                    timeout=30.0
                )
                logger.info(f"\033[92m[{bot_name}] ¡CONECTADO 24/7 a '{channel.name}' con ESCUCHA DE VOZ ACTIVA!\033[0m")

                if hasattr(vc, "listen") and not vc.is_listening():
                    try:
                        vc.listen(HumanVoiceSink(bot_client, is_bot1, bot_name))
                    except Exception as e:
                        logger.warning(f"[{bot_name}] Aviso al activar sink de voz: {e}")

            except discord.errors.ClientException as e:
                if "already connected" not in str(e).lower():
                    logger.warning(f"[{bot_name}] Aviso cliente voz: {e}")
            except Exception as e:
                logger.error(f"[{bot_name}] Error conectando a voz: {e}")

        except Exception as e:
            logger.error(f"[{bot_name}] Error en ensure_voice_connection: {e}")
        finally:
            is_reconnecting = False

    @tree.command(name="cambiar_foto", description=f"🖼️ Cambia la foto de perfil o avatar animado (GIF) de {bot_name}")
    @app_commands.describe(
        imagen="Sube una imagen o archivo GIF animado directamente",
        enlace="O escribe el enlace web directo a la imagen o GIF"
    )
    async def cmd_cambiar_foto(
        interaction: discord.Interaction,
        imagen: Optional[discord.Attachment] = None,
        enlace: Optional[str] = None
    ):
        target_ctrl = KEVIN_CONTROL_CHANNEL_ID if is_bot1 else RAFA_CONTROL_CHANNEL_ID
        if interaction.channel_id != target_ctrl:
            await interaction.response.send_message(
                f"⚠️ Este comando de **{bot_name}** solo se puede usar en su canal de control: <#{target_ctrl}>",
                ephemeral=True
            )
            return

        image_url = None
        is_gif = False
        if imagen:
            image_url = imagen.url
            if imagen.filename.lower().endswith(".gif"):
                is_gif = True
        elif enlace:
            image_url = enlace.strip()
            if ".gif" in image_url.lower():
                is_gif = True

        if not image_url:
            await interaction.response.send_message("❌ Debes adjuntar una imagen/GIF o ingresar un enlace.", ephemeral=True)
            return

        await interaction.response.defer()
        tipo_label = "Avatar Animado (GIF)" if is_gif else "Foto de Perfil"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as resp:
                    if resp.status == 200:
                        img_data = await resp.read()
                        await bot_client.user.edit(avatar=img_data)
                        embed = discord.Embed(
                            title=f"✅ {tipo_label} Actualizado",
                            description=f"Se ha actualizado con éxito el perfil de **{bot_name}** en tiempo real.",
                            color=discord.Color.green()
                        )
                        embed.set_image(url=image_url)
                        await interaction.followup.send(embed=embed)
                    else:
                        await interaction.followup.send("❌ No se pudo descargar la imagen proporcionada.", ephemeral=True)
        except discord.HTTPException as e:
            await interaction.followup.send(f"⚠️ Discord limitó temporalmente el cambio de foto (rate limit de Discord): `{e}`", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error al cambiar avatar: `{e}`", ephemeral=True)

    @tree.command(name="cambiar_nombre", description=f"📛 Cambia el nombre / apodo de {bot_name} en tiempo real")
    @app_commands.describe(nuevo_nombre="El nuevo nombre o apodo para el bot")
    async def cmd_cambiar_nombre(interaction: discord.Interaction, nuevo_nombre: str):
        target_ctrl = KEVIN_CONTROL_CHANNEL_ID if is_bot1 else RAFA_CONTROL_CHANNEL_ID
        if interaction.channel_id != target_ctrl:
            await interaction.response.send_message(
                f"⚠️ Este comando de **{bot_name}** solo se puede usar en <#{target_ctrl}>",
                ephemeral=True
            )
            return

        await interaction.response.defer()
        guild = interaction.guild
        changed_nick = False
        if guild:
            member = guild.get_member(bot_client.user.id)
            if member:
                try:
                    await member.edit(nick=nuevo_nombre)
                    changed_nick = True
                except Exception as e:
                    logger.warning(f"No se pudo cambiar apodo: {e}")

        try:
            await bot_client.user.edit(username=nuevo_nombre)
            await interaction.followup.send(f"✅ **Nombre y Apodo de {bot_name} cambiados con éxito a:** `{nuevo_nombre}`")
        except Exception:
            if changed_nick:
                await interaction.followup.send(f"✅ **Apodo en el servidor cambiado a:** `{nuevo_nombre}` (Discord limita cambiar el username global a 2 veces por hora)")
            else:
                await interaction.followup.send("⚠️ No tengo permisos suficientes para cambiar mi apodo en el servidor.", ephemeral=True)

    @tree.command(name="cambiar_estado", description=f"🎮 Cambia lo que está jugando/haciendo {bot_name}")
    @app_commands.describe(estado="Texto de la actividad fija")
    async def cmd_cambiar_estado(interaction: discord.Interaction, estado: str):
        target_ctrl = KEVIN_CONTROL_CHANNEL_ID if is_bot1 else RAFA_CONTROL_CHANNEL_ID
        if interaction.channel_id != target_ctrl:
            await interaction.response.send_message(
                f"⚠️ Este comando de **{bot_name}** solo se puede usar en <#{target_ctrl}>",
                ephemeral=True
            )
            return

        status_animator.set_active(is_bot1, False)
        act = discord.Activity(type=discord.ActivityType.playing, name=estado, state=estado)
        await bot_client.change_presence(activity=act)
        await interaction.response.send_message(
            f"✅ Actividad de **{bot_name}** actualizada a: **Jugando a {estado}**\n*(Animación pausada. Usa `/animacion accion:activar` para reanudar la rotación)*"
        )

    @tree.command(name="cambiar_tipo", description=f"🟣 Cambia el modo de presencia (Stream, Jugando, Escuchando, Viendo)")
    @app_commands.describe(
        tipo="Tipo de actividad",
        texto="Texto que quieres que diga"
    )
    @app_commands.choices(tipo=[
        app_commands.Choice(name="🟣 Transmitiendo en Vivo (Stream Twitch)", value="stream"),
        app_commands.Choice(name="🎮 Jugando", value="jugando"),
        app_commands.Choice(name="🎧 Escuchando", value="escuchando"),
        app_commands.Choice(name="📺 Viendo", value="viendo")
    ])
    async def cmd_cambiar_tipo(interaction: discord.Interaction, tipo: str, texto: str):
        target_ctrl = KEVIN_CONTROL_CHANNEL_ID if is_bot1 else RAFA_CONTROL_CHANNEL_ID
        if interaction.channel_id != target_ctrl:
            await interaction.response.send_message(
                f"⚠️ Este comando de **{bot_name}** solo se puede usar en <#{target_ctrl}>",
                ephemeral=True
            )
            return

        status_animator.set_active(is_bot1, False)
        if tipo == "stream":
            act = discord.Streaming(name=texto, url="https://twitch.tv/rafamodzyt")
            await bot_client.change_presence(activity=act)
            await interaction.response.send_message(f"🟣 Actividad de **{bot_name}** actualizada a: **Transmitiendo {texto} [LIVE]**")
        elif tipo == "escuchando":
            act = discord.Activity(type=discord.ActivityType.listening, name=texto)
            await bot_client.change_presence(activity=act)
            await interaction.response.send_message(f"🎧 Actividad de **{bot_name}** actualizada a: **Escuchando {texto}**")
        elif tipo == "viendo":
            act = discord.Activity(type=discord.ActivityType.watching, name=texto)
            await bot_client.change_presence(activity=act)
            await interaction.response.send_message(f"📺 Actividad de **{bot_name}** actualizada a: **Viendo {texto}**")
        else:
            act = discord.Activity(type=discord.ActivityType.playing, name=texto)
            await bot_client.change_presence(activity=act)
            await interaction.response.send_message(f"🎮 Actividad de **{bot_name}** actualizada a: **Jugando a {texto}**")

    @tree.command(name="cambiar_presencia", description=f"🟢 Cambia el color del estado de {bot_name} (Conectado, No Molestar, Ausente)")
    @app_commands.describe(estado="Elige el estado")
    @app_commands.choices(estado=[
        app_commands.Choice(name="🟢 Conectado (Online)", value="online"),
        app_commands.Choice(name="🔴 No Molestar (DND)", value="dnd"),
        app_commands.Choice(name="🟡 Ausente (Idle)", value="idle")
    ])
    async def cmd_cambiar_presencia(interaction: discord.Interaction, estado: str):
        target_ctrl = KEVIN_CONTROL_CHANNEL_ID if is_bot1 else RAFA_CONTROL_CHANNEL_ID
        if interaction.channel_id != target_ctrl:
            await interaction.response.send_message(
                f"⚠️ Este comando de **{bot_name}** solo se puede usar en <#{target_ctrl}>",
                ephemeral=True
            )
            return

        if estado == "dnd":
            await bot_client.change_presence(status=discord.Status.dnd)
            await interaction.response.send_message(f"🔴 Estado de **{bot_name}** cambiado a: **No Molestar**")
        elif estado == "idle":
            await bot_client.change_presence(status=discord.Status.idle)
            await interaction.response.send_message(f"🟡 Estado de **{bot_name}** cambiado a: **Ausente**")
        else:
            await bot_client.change_presence(status=discord.Status.online)
            await interaction.response.send_message(f"🟢 Estado de **{bot_name}** cambiado a: **Conectado**")

    @tree.command(name="animacion", description=f"🔄 Controla la rotación animada de perfil en tiempo real de {bot_name}")
    @app_commands.describe(
        accion="Qué acción deseas realizar",
        frases="Frases personalizadas separadas por | (solo si eliges 'personalizar')"
    )
    @app_commands.choices(accion=[
        app_commands.Choice(name="▶️ Activar rotación animada", value="activar"),
        app_commands.Choice(name="⏸️ Pausar animación (dejar fijo)", value="pausar"),
        app_commands.Choice(name="📋 Ver lista de frases actuales", value="ver_lista"),
        app_commands.Choice(name="✨ Personalizar frases rotativas", value="personalizar")
    ])
    async def cmd_animacion(interaction: discord.Interaction, accion: str, frases: Optional[str] = None):
        target_ctrl = KEVIN_CONTROL_CHANNEL_ID if is_bot1 else RAFA_CONTROL_CHANNEL_ID
        if interaction.channel_id != target_ctrl:
            await interaction.response.send_message(
                f"⚠️ Este comando de **{bot_name}** solo se puede usar en <#{target_ctrl}>",
                ephemeral=True
            )
            return

        if accion == "activar":
            status_animator.set_active(is_bot1, True)
            await interaction.response.send_message(f"🔄 **¡Animación de perfil activada para {bot_name}!** Rota cada 15s.")
        elif accion == "pausar":
            status_animator.set_active(is_bot1, False)
            await interaction.response.send_message(f"⏸️ **Animación de perfil pausada para {bot_name}.**")
        elif accion == "ver_lista":
            items = status_animator.bot1_items if is_bot1 else status_animator.bot2_items
            lista_txt = "\n".join([f"{i+1}. `{it.get('name')}`" for i, it in enumerate(items)])
            await interaction.response.send_message(f"📋 **Frases de animación de {bot_name}:**\n{lista_txt}")
        elif accion == "personalizar":
            if not frases or "|" not in frases:
                await interaction.response.send_message("⚠️ Debes proporcionar las frases separadas con `|`. Ejemplo: `/animacion accion:personalizar frases:Frase 1 | Frase 2 | Frase 3`", ephemeral=True)
                return
            parts = frases.split("|")
            status_animator.set_custom_phrases(is_bot1, parts)
            await interaction.response.send_message(f"✨ **¡Animación personalizada activada para {bot_name}!** Rota entre {len(parts)} frases.")

    @tree.command(name="perfil", description=f"📊 Muestra la tarjeta del perfil de {bot_name}")
    async def cmd_perfil(interaction: discord.Interaction):
        guild = interaction.guild
        member = guild.get_member(bot_client.user.id) if guild else None
        current_activity = bot_client.activity.name if bot_client.activity else "Ninguna"
        is_animating = status_animator.bot1_active if is_bot1 else status_animator.bot2_active
        embed = discord.Embed(
            title=f"🎛️ Perfil en Tiempo Real - {bot_name}",
            description=f"Perfil activo de **{bot_client.user}**",
            color=discord.Color.red() if is_bot1 else discord.Color.purple()
        )
        embed.set_thumbnail(url=bot_client.user.display_avatar.url)
        embed.add_field(name="📛 Nombre / Apodo", value=member.display_name if member else bot_client.user.name, inline=True)
        embed.add_field(name="🎮 Actividad Actual", value=current_activity, inline=True)
        embed.add_field(name="🟢 Presencia", value=str(bot_client.status).capitalize(), inline=True)
        embed.add_field(name="🔄 Estado Animado", value="Activo (Rotando) ✨" if is_animating else "Pausado (Fijo)", inline=False)
        await interaction.response.send_message(embed=embed)

    @bot_client.event
    async def on_ready():
        invite = get_invite_url(bot_id or str(bot_client.user.id))
        print("\n" + "=" * 65)
        print(f"       \033[92m{bot_name} ONLINE (24/7 FULL FEATURES)\033[0m")
        print("=" * 65)
        print(f" » Bot:           {bot_client.user} (ID: {bot_client.user.id})")
        print(f" » Enlace Invitar:{invite}")
        print("=" * 65 + "\n")

        # Configuración de Presencia y Perfil
        try:
            if is_bot1:
                activity = discord.Activity(
                    type=discord.ActivityType.playing,
                    name="Amo A Karen",
                    state="Keren 💖",
                    details="Amo A Karen 💖"
                )
                await bot_client.change_presence(status=discord.Status.dnd, activity=activity)
            else:
                activity = discord.Streaming(
                    name="Adicto Alas Tetas",
                    url="https://twitch.tv/rafamodzyt"
                )
                await bot_client.change_presence(status=discord.Status.online, activity=activity)
        except Exception as e:
            logger.warning(f"[{bot_name}] Error configurando presencia: {e}")

        # Sincronizar slash commands limpiando duplicados
        try:
            guild_obj = discord.Object(id=GUILD_ID)
            tree.clear_commands(guild=guild_obj)
            await tree.sync(guild=guild_obj)
            await tree.sync()
            logger.info(f"[{bot_name}] Slash commands (/cambiar_foto, /cambiar_nombre, etc.) sincronizados limpiamente.")
        except Exception as e:
            logger.warning(f"[{bot_name}] Error sincronizando slash commands: {e}")

        # Enviar aviso en el canal de control dedicado
        target_ctrl_channel_id = KEVIN_CONTROL_CHANNEL_ID if is_bot1 else RAFA_CONTROL_CHANNEL_ID
        if target_ctrl_channel_id:
            try:
                ch = bot_client.get_channel(target_ctrl_channel_id)
                if ch is None:
                    ch = await bot_client.fetch_channel(target_ctrl_channel_id)
                if ch:
                    embed = discord.Embed(
                        title=f"🎛️ Panel de Personalización - {bot_name}",
                        description=(
                            f"¡Este canal está enlazado para personalizar todo el perfil de **{bot_name}** en tiempo real!\n\n"
                            "**Comandos Slash disponibles en este chat:**\n"
                            "• 🖼️ `/cambiar_foto` ➔ Sube una foto o **GIF animado** (o arrástrala al chat)\n"
                            "• 📛 `/cambiar_nombre` ➔ Cambia el nombre / apodo del bot\n"
                            "• 🎮 `/cambiar_estado` ➔ Fija lo que está jugando/haciendo\n"
                            "• 🟣 `/cambiar_tipo` ➔ Stream Twitch (LIVE), Jugando, Escuchando, Viendo\n"
                            "• 🟢 `/cambiar_presencia` ➔ Conectado (verde), No Molestar (rojo), Ausente\n"
                            "• 🔄 `/animacion` ➔ Activa o personaliza estados que rotan cada 15s\n"
                            "• 📊 `/perfil` ➔ Ver tarjeta actual del perfil"
                        ),
                        color=discord.Color.red() if is_bot1 else discord.Color.purple()
                    )
                    await ch.send(embed=embed)
                    logger.info(f"[{bot_name}] Panel de control enviado con éxito a #{getattr(ch, 'name', target_ctrl_channel_id)}")
            except Exception as e:
                logger.warning(f"[{bot_name}] Aviso al enviar embed en canal de control: {e}")

        # Iniciar rotación animada de perfil en vivo
        try:
            await status_animator.start(bot_client, is_bot1)
        except Exception as e:
            logger.warning(f"[{bot_name}] Error iniciando animación de estados: {e}")

        await ensure_voice_connection()

    @bot_client.event
    async def on_voice_state_update(member, before, after):
        if member.id == bot_client.user.id:
            if after.channel is None:
                logger.warning(f"[{bot_name}] Desconectado de llamada. Reconectando en 2 segundos...")
                await asyncio.sleep(2)
                await ensure_voice_connection()
                return
            if after.channel.id != VOICE_CHANNEL_ID:
                guild = bot_client.get_guild(GUILD_ID)
                target = guild.get_channel(VOICE_CHANNEL_ID) if guild else None
                if target and guild.voice_client:
                    logger.warning(f"[{bot_name}] Movido a '{after.channel.name}'. Regresando...")
                    await asyncio.sleep(1)
                    try:
                        await guild.voice_client.move_to(target)
                    except Exception as e:
                        logger.error(f"[{bot_name}] Error regresando a canal: {e}")
            return

        # 1. Bienvenida callejera cuando un usuario real entra al canal de voz
        if before.channel != after.channel and after.channel is not None and after.channel.id == VOICE_CHANNEL_ID:
            if member and not member.bot and is_bot1:
                # Bot 1 da la bienvenida por micrófono
                guild = bot_client.get_guild(GUILD_ID)
                vc = guild.voice_client if guild else None
                if vc and vc.is_connected() and not music_manager.is_playing_music:
                    saludos_voz = [
                        f"¡Qué onda {member.display_name}, bienvenido al desmadre carnal! Pásale a sentarte.",
                        f"¡Miren nada más quién llegó, el mero patrón {member.display_name}! ¿Qué se va a armar hoy viejo?",
                        f"¡Qué hubo {member.display_name}! Ya se puso bueno el cotorreo, bienvenido mi bro."
                    ]
                    saludo = random.choice(saludos_voz)
                    conv_manager.pause()
                    await asyncio.sleep(1.0)
                    await speak_text(vc, saludo, VOICE_1, speaker_id=bot_name)
                    await asyncio.sleep(1.5)
                    conv_manager.resume()

    # Evento de detección de voz humana
    @bot_client.event
    async def on_voice_member_speaking_state(member, ssrc, state):
        if member is None or getattr(member, "bot", False):
            return

        is_speaking = False
        try:
            is_speaking = int(state) > 0
        except Exception:
            is_speaking = bool(state)

        if not is_speaking:
            return

        guild = bot_client.get_guild(GUILD_ID)
        vc = guild.voice_client if guild else None
        if vc and vc.is_connected() and vc.channel.id == VOICE_CHANNEL_ID:
            voice_to_use = VOICE_1 if is_bot1 else VOICE_2
            bot_client.loop.create_task(
                voice_interaction_mgr.handle_human_speaking(
                    bot_client, member, vc, voice_to_use, bot_name
                )
            )

    @bot_client.event
    async def on_resumed():
        logger.info(f"[{bot_name}] Sesión reanudada. Verificando canal de voz...")
        await ensure_voice_connection()

    @bot_client.event
    async def on_message(message: discord.Message):
        global KEVIN_CONTROL_CHANNEL_ID, RAFA_CONTROL_CHANNEL_ID
        if message.author.bot:
            return

        content_lower = message.content.lower().strip()

        # Configurar canales de control en caliente
        if content_lower == "!set_canal_kevin" and is_bot1:
            KEVIN_CONTROL_CHANNEL_ID = message.channel.id
            await message.channel.send(f"✅ **Canal asignado para el control total de Kevin 17:** {message.channel.mention}\n*(Arrastra fotos aquí para cambiar su avatar o escribe `!ayuda`)*")
            return
        if content_lower == "!set_canal_rafa" and not is_bot1:
            RAFA_CONTROL_CHANNEL_ID = message.channel.id
            await message.channel.send(f"✅ **Canal asignado para el control total de RafaModzYT:** {message.channel.mention}\n*(Arrastra fotos aquí para cambiar su avatar o escribe `!ayuda`)*")
            return

        # Ignorar por completo si el mensaje proviene del canal de control del OTRO bot
        if is_bot1 and RAFA_CONTROL_CHANNEL_ID and message.channel.id == RAFA_CONTROL_CHANNEL_ID:
            return
        if not is_bot1 and KEVIN_CONTROL_CHANNEL_ID and message.channel.id == KEVIN_CONTROL_CHANNEL_ID:
            return

        # Si el mensaje está en el canal de control exclusivo del bot:
        is_in_kevin_channel = is_bot1 and (message.channel.id == KEVIN_CONTROL_CHANNEL_ID and KEVIN_CONTROL_CHANNEL_ID != 0)
        is_in_rafa_channel = not is_bot1 and (message.channel.id == RAFA_CONTROL_CHANNEL_ID and RAFA_CONTROL_CHANNEL_ID != 0)
        is_in_my_control_channel = is_in_kevin_channel or is_in_rafa_channel

        if is_in_my_control_channel:
            handled = await handle_profile_customization(message, bot_client, is_bot1, bot_name)
            if handled:
                return

        # Detección por Username
        has_kevin = any(k in content_lower for k in ["kevin 17", "kevin", "oye kevin", "ey kevin"])
        has_rafa = any(k in content_lower for k in ["rafamodzyt", "rafa", "oye rafa", "ey rafa", "modz"])
        is_mentioned = bot_client.user.mentioned_in(message)

        if is_in_my_control_channel:
            # En su propio canal de control, siempre responde a cualquier mensaje o consulta
            pass
        elif has_kevin and not has_rafa:
            if not is_bot1:
                return
        elif has_rafa and not has_kevin:
            if is_bot1:
                return
        elif is_mentioned:
            if not bot_client.user.mentioned_in(message):
                return
        else:
            return

        # 6. Reacciones automáticas con emojis
        try:
            emojis_kevin = ["💖", "🔫", "💀", "⚡"]
            emojis_rafa = ["👑", "🍑", "🏎️", "😈"]
            reaction = random.choice(emojis_kevin if is_bot1 else emojis_rafa)
            await message.add_reaction(reaction)
        except Exception:
            pass

        target_str = "bot1" if is_bot1 else "bot2"
        res = process_user_interaction(message.content, bot_targeted=target_str)

        # 4. Simulación humana de Typing ("Escribiendo...")
        try:
            async with message.channel.typing():
                await asyncio.sleep(random.uniform(1.2, 2.2))
            await message.channel.send(res["text_reply"])
        except Exception as e:
            logger.error(f"[{bot_name}] Error enviando mensaje de chat: {e}")

        guild = bot_client.get_guild(GUILD_ID)
        vc = guild.voice_client if guild else None

        if vc and vc.is_connected() and vc.channel.id == VOICE_CHANNEL_ID:
            voice_to_use = VOICE_1 if is_bot1 else VOICE_2

            # 5. Modo Tiradera
            if res.get("is_tiradera"):
                guild2 = bot_client.get_guild(GUILD_ID)
                vc2 = guild2.voice_client if guild2 else None
                bot_client.loop.create_task(execute_tiradera(vc, vc2))
                return

            # 3. Soundboard
            if res.get("is_soundboard"):
                conv_manager.pause()
                await play_sound_effect(vc, res.get("sound_name", "balazo"))
                conv_manager.resume()
                return

            # Música
            if res["is_stop_music"]:
                music_manager.stop_song(vc)
                await speak_text(vc, res["voice_reply"], voice_to_use, speaker_id=bot_name)
                conv_manager.resume()

            elif res["is_music"]:
                conv_manager.pause()
                await speak_text(vc, res["voice_reply"], voice_to_use, speaker_id=bot_name)
                success, title = music_manager.play_song(vc, res["music_query"])
                if success:
                    await message.channel.send(f"▶️ **Reproduciendo:** `{title}` en `{vc.channel.name}`")
                else:
                    await message.channel.send(f"⚠️ {title}")
                    conv_manager.resume()

            else:
                if not music_manager.is_playing_music:
                    await speak_text(vc, res["voice_reply"], voice_to_use, speaker_id=bot_name)

    async def keep_alive_task():
        await bot_client.wait_until_ready()
        while not bot_client.is_closed():
            try:
                guild = bot_client.get_guild(GUILD_ID)
                if guild is not None:
                    vc = guild.voice_client
                    if vc is None or not vc.is_connected() or vc.channel.id != VOICE_CHANNEL_ID:
                        await ensure_voice_connection()
            except Exception as e:
                logger.error(f"[{bot_name}] Error en bucle keep_alive: {e}")
            await asyncio.sleep(CHECK_INTERVAL_SECONDS)

    return bot_client, keep_alive_task


async def conversation_loop(bot1: discord.Client, bot2: discord.Client):
    logger.info("🎙️ Iniciando conversación continua entre Kevin 17 y RafaModzYT...")
    await bot1.wait_until_ready()
    await bot2.wait_until_ready()
    await asyncio.sleep(5)

    while not bot1.is_closed() and not bot2.is_closed():
        try:
            guild1 = bot1.get_guild(GUILD_ID)
            guild2 = bot2.get_guild(GUILD_ID)

            vc1 = guild1.voice_client if guild1 else None
            vc2 = guild2.voice_client if guild2 else None

            both_connected = (
                vc1 is not None and vc1.is_connected() and vc1.channel.id == VOICE_CHANNEL_ID and
                vc2 is not None and vc2.is_connected() and vc2.channel.id == VOICE_CHANNEL_ID
            )

            if not both_connected:
                await asyncio.sleep(4)
                continue

            if music_manager.is_playing_music or voice_interaction_mgr.is_responding:
                await asyncio.sleep(2)
                continue

            if conv_manager.is_paused:
                await asyncio.sleep(2)
                continue

            speaker, text, is_new_topic = conv_manager.get_next_line()

            if speaker is None or text is None:
                await asyncio.sleep(2)
                continue

            if is_new_topic:
                await asyncio.sleep(random.uniform(3.0, 5.0))

            if speaker == "bot1":
                await speak_text(vc1, text, VOICE_1, speaker_id="Kevin 17")
            else:
                await speak_text(vc2, text, VOICE_2, speaker_id="RafaModzYT")

            await asyncio.sleep(random.uniform(2.0, 3.8))

        except Exception as e:
            logger.error(f"Error en conversation_loop: {e}")
            await asyncio.sleep(3)


async def main():
    bot1, keep_alive1 = setup_bot(BOT1_NAME, BOT1_ID, is_bot1=True)
    bot2, keep_alive2 = setup_bot(BOT2_NAME, BOT2_ID, is_bot1=False)

    async with bot1, bot2:
        bot1.loop.create_task(keep_alive1())
        bot2.loop.create_task(keep_alive2())
        bot1.loop.create_task(conversation_loop(bot1, bot2))

        await asyncio.gather(
            bot1.start(BOT1_TOKEN),
            bot2.start(BOT2_TOKEN)
        )


if __name__ == "__main__":
    print("=" * 65)
    print("   2 BOTS 24/7 EN VOZ + FULL CUSTOMIZATION + SOUNDBOARD + LIVE")
    print("=" * 65)
    while True:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print("\nDetenido por el usuario.")
            break
        except Exception as e:
            logger.error(f"Error inesperado en main: {e}")
            logger.info("Reiniciando en 5 segundos...")
            import time
            time.sleep(5)
