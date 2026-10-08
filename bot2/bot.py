import os
import sys
import random
import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
import discord
from discord import app_commands

# Asegurar importación de módulos superiores
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from dialogues import CONVERSATION_TOPICS, VOICE_BOT2
from voice_coordinator import speak_text
from state_manager import get_conversation_state, update_conversation_state

# Cargar variables locales
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
BOT_ID = os.getenv("BOT_ID", "1557663530625278042").strip()
BOT_NAME = os.getenv("BOT_NAME", "RafaModzYT").strip()
GUILD_ID = int(os.getenv("GUILD_ID", "1538269421020258304").strip())
VOICE_CHANNEL_ID = int(os.getenv("VOICE_CHANNEL_ID", "1542358479270846565").strip())
CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", "10").strip())
VOICE_NAME = os.getenv("VOICE_NAME", VOICE_BOT2)

if not BOT_TOKEN:
    print(f"\033[91m[ERROR] No se encontró el BOT_TOKEN en {env_path}\033[0m")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("VoiceBot2")

intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

is_reconnecting = False
start_time = datetime.now(timezone.utc)


def get_invite_url(client_id: str) -> str:
    return f"https://discord.com/oauth2/authorize?client_id={client_id}&permissions=8&scope=bot"


async def ensure_voice_connection():
    global is_reconnecting
    if is_reconnecting:
        return

    is_reconnecting = True
    try:
        guild = client.get_guild(GUILD_ID)
        if guild is None:
            invite = get_invite_url(BOT_ID or str(client.user.id if client.user else ""))
            logger.warning(
                f"\033[93m[{BOT_NAME}] El bot no se encuentra en el servidor {GUILD_ID}.\n"
                f"-> Enlace para agregarlo: {invite}\033[0m"
            )
            return

        channel = guild.get_channel(VOICE_CHANNEL_ID)
        if channel is None:
            logger.warning(f"[{BOT_NAME}] No se encontró el canal de voz {VOICE_CHANNEL_ID} en '{guild.name}'")
            return

        voice_client = guild.voice_client

        if voice_client is not None:
            if voice_client.channel.id != VOICE_CHANNEL_ID:
                logger.info(f"[{BOT_NAME}] En canal incorrecto. Moviendo a '{channel.name}'...")
                await voice_client.move_to(channel)
                return

            if voice_client.is_connected():
                return
            else:
                logger.warning(f"[{BOT_NAME}] Conexión de voz caída. Limpiando...")
                try:
                    await voice_client.disconnect(force=True)
                except Exception:
                    pass
                await asyncio.sleep(1)

        logger.info(f"\033[96m[{BOT_NAME}] Conectando al canal de voz '{channel.name}' ({channel.id})...\033[0m")
        try:
            # self_deaf=False y self_mute=False para hablar y escuchar
            await channel.connect(reconnect=True, self_deaf=False, self_mute=False, timeout=30.0)
            logger.info(f"\033[92m[{BOT_NAME}] ¡CONECTADO 24/7 a '{channel.name}'!\033[0m")
        except discord.errors.ClientException as e:
            if "already connected" not in str(e).lower():
                logger.warning(f"[{BOT_NAME}] Aviso de cliente: {e}")
        except Exception as e:
            logger.error(f"[{BOT_NAME}] Error al conectar a la voz: {e}")

    except Exception as e:
        logger.error(f"[{BOT_NAME}] Error en ensure_voice_connection: {e}")
    finally:
        is_reconnecting = False


@client.event
async def on_ready():
    invite = get_invite_url(BOT_ID or str(client.user.id))
    print("\n" + "=" * 65)
    print(f"       \033[92m{BOT_NAME} - 24/7 VOICE BOT ONLINE\033[0m")
    print("=" * 65)
    print(f" » Bot:           {client.user} (ID: {client.user.id})")
    print(f" » Servidor ID:   {GUILD_ID}")
    print(f" » Canal Voz ID:  {VOICE_CHANNEL_ID}")
    print(f" » Enlace Invitar:{invite}")
    print("=" * 65 + "\n")

    try:
        activity = discord.Activity(type=discord.ActivityType.listening, name="Charlando 24/7 🎙️")
        await client.change_presence(status=discord.Status.online, activity=activity)
    except Exception:
        pass

    try:
        await tree.sync()
    except Exception:
        pass

    await ensure_voice_connection()


@client.event
async def on_voice_state_update(member, before, after):
    if member.id != client.user.id:
        return

    if after.channel is None:
        logger.warning(f"\033[93m[{BOT_NAME}] Bot desconectado de llamada. Reconectando en 2 segundos...\033[0m")
        await asyncio.sleep(2)
        await ensure_voice_connection()
        return

    if after.channel.id != VOICE_CHANNEL_ID:
        guild = client.get_guild(GUILD_ID)
        target = guild.get_channel(VOICE_CHANNEL_ID) if guild else None
        if target:
            logger.warning(f"[{BOT_NAME}] Movido a '{after.channel.name}'. Regresando a '{target.name}'...")
            await asyncio.sleep(1)
            try:
                if guild.voice_client:
                    await guild.voice_client.move_to(target)
                else:
                    await ensure_voice_connection()
            except Exception as e:
                logger.error(f"[{BOT_NAME}] Error al mover de regreso: {e}")


@client.event
async def on_resumed():
    logger.info(f"[{BOT_NAME}] Sesión reanudada. Verificando canal de voz...")
    await ensure_voice_connection()


async def keep_alive_loop():
    await client.wait_until_ready()
    while not client.is_closed():
        try:
            guild = client.get_guild(GUILD_ID)
            if guild is not None:
                vc = guild.voice_client
                if vc is None or not vc.is_connected() or vc.channel.id != VOICE_CHANNEL_ID:
                    logger.info(f"[{BOT_NAME}] [Keep-Alive] Bot fuera de la voz. Restaurando conexión...")
                    await ensure_voice_connection()
            else:
                invite = get_invite_url(BOT_ID or str(client.user.id))
                logger.warning(f"[{BOT_NAME}] Esperando a que el bot sea agregado: {invite}")
        except Exception as e:
            logger.error(f"[{BOT_NAME}] Error en keep_alive: {e}")

        await asyncio.sleep(CHECK_INTERVAL_SECONDS)


async def talk_coordinator_loop():
    """Monitorea el turno compartido y reproduce la voz cuando le toca a Bot 2."""
    await client.wait_until_ready()
    await asyncio.sleep(7)

    while not client.is_closed():
        try:
            guild = client.get_guild(GUILD_ID)
            vc = guild.voice_client if guild else None

            if vc is None or not vc.is_connected() or vc.channel.id != VOICE_CHANNEL_ID:
                await asyncio.sleep(3)
                continue

            state = get_conversation_state()
            if state.get("is_paused", False):
                await asyncio.sleep(2)
                continue

            if state.get("turn") == "bot2":
                topic_idx = state.get("topic_index", 0) % len(CONVERSATION_TOPICS)
                step_idx = state.get("step_index", 0)
                topic = CONVERSATION_TOPICS[topic_idx]

                if step_idx >= len(topic):
                    topic_idx = (topic_idx + 1) % len(CONVERSATION_TOPICS)
                    step_idx = 0
                    topic = CONVERSATION_TOPICS[topic_idx]
                    await asyncio.sleep(random.uniform(3.0, 5.0))

                speaker, text = topic[step_idx]

                if speaker == "bot2":
                    await speak_text(vc, text, VOICE_NAME, speaker_id=BOT_NAME)
                    step_idx += 1
                    update_conversation_state(turn="bot1", topic_index=topic_idx, step_index=step_idx)
                    await asyncio.sleep(random.uniform(2.0, 3.5))
                else:
                    # Le tocaba a bot1 en este paso
                    update_conversation_state(turn="bot1", topic_index=topic_idx, step_index=step_idx)

        except Exception as e:
            logger.error(f"[{BOT_NAME}] Error en talk_coordinator: {e}")
            await asyncio.sleep(3)

        await asyncio.sleep(1.0)


@tree.command(name="status_bot2", description="Verifica el estado 24/7 de Bot 2 (RafaModzYT)")
async def slash_status(interaction: discord.Interaction):
    guild = client.get_guild(GUILD_ID)
    vc = guild.voice_client if guild else None
    connected = vc is not None and vc.is_connected()
    uptime = str(datetime.now(timezone.utc) - start_time).split(".")[0]
    state = get_conversation_state()
    msg = (
        f"📊 **Estado de {BOT_NAME}:**\n"
        f"• Conectado en Voz: `{'🟢 Sí (24/7 Activo)' if connected else '🔴 Desconectado'}`\n"
        f"• Estado Conversación: `{'⏸️ Pausada' if state.get('is_paused') else '🗣️ Platicando'}`\n"
        f"• Latencia: `{round(client.latency * 1000)}ms` | Uptime: `{uptime}`"
    )
    await interaction.response.send_message(msg)


async def main():
    async with client:
        client.loop.create_task(keep_alive_loop())
        client.loop.create_task(talk_coordinator_loop())
        await client.start(BOT_TOKEN)


if __name__ == "__main__":
    while True:
        try:
            asyncio.run(main())
        except discord.errors.LoginFailure:
            logger.critical(f"\033[91m[{BOT_NAME}] TOKEN INVÁLIDO. Revisa el archivo .env\033[0m")
            break
        except KeyboardInterrupt:
            logger.info(f"[{BOT_NAME}] Bot detenido manualmente por el usuario.")
            break
        except Exception as e:
            logger.error(f"[{BOT_NAME}] Excepción en ciclo principal: {e}")
            logger.info(f"[{BOT_NAME}] Reiniciando automáticamente en 5 segundos...")
            import time
            time.sleep(5)
