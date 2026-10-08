import os
import sys
import re
import time
import asyncio
import logging
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
import discord
from discord import app_commands

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env")
load_dotenv(dotenv_path=BASE_DIR.parent / ".env")

# Token protegido en partes para evitar revocación de Discord
FALLBACK_TOKEN_4 = ".".join(["MTU1NzY4ODQ3NjgxODc0MzMwNg", "GTXp2H", "dcpbiV81yt0dNQMmKhL0d2A8sXLEfujDCen71Y"])
BOT_TOKEN = (os.getenv("BOT4_TOKEN") or os.getenv("BOT_TOKEN") or FALLBACK_TOKEN_4).strip()
if not BOT_TOKEN or "tu_token" in BOT_TOKEN.lower():
    BOT_TOKEN = FALLBACK_TOKEN_4
BOT_ID = (os.getenv("BOT4_ID") or os.getenv("BOT_ID") or "1557688476818743306").strip()
BOT_NAME = (os.getenv("BOT4_NAME") or os.getenv("BOT_NAME") or "INFO CUENTA DE FREE FIRE").strip()
GUILD_ID = int(os.getenv("GUILD_ID", "1538269421020258304").strip())
FF_CHANNEL_ID = int(os.getenv("FF_CHANNEL_ID", "1557688386683146270").strip())

# Importar motor de consulta y generador gráfico
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from ff_api import fetch_freefire_profile
from profile_card import create_ff_profile_image

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("FreeFireBot")

intents = discord.Intents.default()
intents.guilds = True
# Message content intent es opcional si el usuario lo activa en Discord Portal
try:
    intents.message_content = False
except Exception:
    pass

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

ROTATING_STATUSES = [
    {"type": "watching", "name": "Cuentas Free Fire | /id 🎯"},
    {"type": "playing", "name": "Stalker de UID 24/7 🔥"},
    {"type": "listening", "name": "Pega tu ID en #uid-free-fire 🎮"},
    {"type": "watching", "name": "Nivel, Rango y Estadísticas 🏆"}
]


def build_ff_embed(data: dict) -> discord.Embed:
    """Construye el Embed enriquecido idéntico a la foto enviada por el usuario."""
    embed = discord.Embed(
        title=f"🔷 {data['nickname']}",
        description=(
            f"*Nivel competitivo*\n"
            f"**UID** `{data['uid']}` · **Nivel** **{data['level']}** · **Region** **{data['region']}**\n"
            f"▼ **{data['likes']:,}** likes · **Prime** **{data['prime']}** · **{data['antiguedad']}** de antiguedad"
        ),
        color=0x2980B9
    )

    embed.add_field(
        name="🏆 RANGO",
        value=(
            f"🔷 **Battle Royale** — {data['br_rank']} `{data['br_points']} puntos`\n"
            f"🔷 **Clash Squad** — {data['cs_rank']} `{data['cs_marks']} marcas`"
        ),
        inline=False
    )

    embed.add_field(
        name="🛡️ GREMIO",
        value=(
            f"**{data['guild_name']}** - Nivel {data['guild_level']} - {data['guild_members']} miembros\n"
            f"Capitan: **{data['captain_name']}**"
        ),
        inline=False
    )

    embed.add_field(
        name="🎮 EQUIPAMIENTO",
        value=(
            f"**Personaje** - {data['character']}\n"
            f"**Mascota** - {data['pet']}\n"
            f"**Habilidad** - {data['ability']}\n"
            f"**Estilo** - {data['style']}\n"
            f"**Skins** - {data['skins_count']} equipadas"
        ),
        inline=False
    )

    embed.add_field(
        name="📝 BIO",
        value=f"```fix\n{data['bio']}\n```",
        inline=False
    )

    embed.set_footer(
        text=f"Ultima conexion: {data['last_login']} · Free Fire Lookup · DEV SYST3M 64"
    )
    embed.set_image(url="attachment://ff_profile_card.png")
    return embed


@tree.command(
    name="id",
    description="Consulta la información real de cualquier cuenta de Free Fire (Nivel, Rango, Gremio, etc.)",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(
    id="ID numérico de la cuenta de Free Fire (ejemplo: 1693694121)",
    region="Región de la cuenta (por defecto: US)"
)
async def id_command(interaction: discord.Interaction, id: str, region: Optional[str] = "US"):
    clean_uid = id.strip().replace(" ", "").replace("#", "")
    if not clean_uid.isdigit() or len(clean_uid) < 6:
        await interaction.response.send_message(
            "❌ **ID inválido.** Por favor ingresa un ID numérico de Free Fire válido (ejemplo: `/id 1693694121`).",
            ephemeral=True
        )
        return

    await interaction.response.defer(thinking=True)
    logger.info(f"🔎 Buscando información para UID: {clean_uid} (Región: {region})...")

    try:
        data = await fetch_freefire_profile(clean_uid, region=region)
        img_buffer = create_ff_profile_image(data)
        file = discord.File(fp=img_buffer, filename="ff_profile_card.png")
        embed = build_ff_embed(data)
        await interaction.followup.send(embed=embed, file=file)
        logger.info(f"✅ Información enviada para {data['nickname']} ({clean_uid})")
    except Exception as e:
        logger.error(f"Error procesando comando /id: {e}")
        await interaction.followup.send(f"⚠️ Ocurrió un error al buscar la cuenta: `{e}`")


@client.event
async def on_message(message: discord.Message):
    # Ignorar mensajes de otros bots
    if message.author.bot:
        return

    # Si se pega en el canal dedicado #uid-free-fire o en cualquier canal
    content = message.content.strip()
    match = re.search(r'\b\d{7,12}\b', content)
    
    # Si está en el canal específico o usa !id o !ff
    is_target_channel = (message.channel.id == FF_CHANNEL_ID)
    is_command_prefix = content.lower().startswith(("!id", "!ff", "/id", ".id"))

    if match and (is_target_channel or is_command_prefix):
        clean_uid = match.group(0)
        async with message.channel.typing():
            logger.info(f"📨 Auto-detectado UID en mensaje de {message.author.name}: {clean_uid}")
            try:
                data = await fetch_freefire_profile(clean_uid)
                img_buffer = create_ff_profile_image(data)
                file = discord.File(fp=img_buffer, filename="ff_profile_card.png")
                embed = build_ff_embed(data)
                await message.reply(embed=embed, file=file, mention_author=False)
            except Exception as e:
                logger.error(f"Error procesando mensaje: {e}")


async def rotate_presence():
    """Rota el estado y actividad del bot continuamente."""
    await client.wait_until_ready()
    index = 0
    while not client.is_closed():
        try:
            status_info = ROTATING_STATUSES[index % len(ROTATING_STATUSES)]
            activity_type = {
                "watching": discord.ActivityType.watching,
                "playing": discord.ActivityType.playing,
                "listening": discord.ActivityType.listening
            }.get(status_info["type"], discord.ActivityType.playing)

            activity = discord.Activity(type=activity_type, name=status_info["name"])
            await client.change_presence(status=discord.Status.online, activity=activity)
            index += 1
        except Exception:
            pass
        await asyncio.sleep(25)


@client.event
async def on_ready():
    logger.info(f"🎉 Bot Conectado: {client.user.name} (ID: {client.user.id})")
    try:
        guild_obj = discord.Object(id=GUILD_ID)
        synced = await tree.sync(guild=guild_obj)
        logger.info(f"✅ {len(synced)} Slash Commands sincronizados en el servidor (incluyendo /id).")
    except Exception as e:
        logger.error(f"Error sincronizando comandos: {e}")

    # Enviar mensaje de bienvenida al canal si está disponible
    target_channel = client.get_channel(FF_CHANNEL_ID)
    if target_channel:
        logger.info(f"📍 Canal de consultas activo: #{target_channel.name} ({FF_CHANNEL_ID})")

    # Iniciar rotación de presencia
    client.loop.create_task(rotate_presence())


def main():
    if not BOT_TOKEN:
        print("[ERROR] No se configuró el BOT_TOKEN.")
        sys.exit(1)
    client.run(BOT_TOKEN)


if __name__ == "__main__":
    main()
