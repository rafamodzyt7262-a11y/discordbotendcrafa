import os
import sys
import time
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, List, Dict

from dotenv import load_dotenv
import aiohttp
import discord
from discord import app_commands
import yt_dlp

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env")
load_dotenv(dotenv_path=BASE_DIR.parent / ".env")

FALLBACK_TOKEN_3 = ".".join(["MTU1NzY4MTQxOTg3MzE2NTQwMw", "GhiSRj", "7hfSledLg23MagU9mitr4X-_VzNY1b1sh7dwQ4"])
BOT_TOKEN = (os.getenv("BOT3_TOKEN") or os.getenv("BOT_TOKEN") or FALLBACK_TOKEN_3).strip()
BOT_ID = (os.getenv("BOT3_ID") or os.getenv("BOT_ID") or "1557681419873165403").strip()
BOT_NAME = (os.getenv("BOT3_NAME") or os.getenv("BOT_NAME") or "MusicBot 24/7").strip()
GUILD_ID = int(os.getenv("GUILD_ID", "1538269421020258304").strip())
VOICE_CHANNEL_ID = int(os.getenv("MUSIC_VOICE_CHANNEL_ID") or os.getenv("VOICE_CHANNEL_ID", "1557674216340586507").strip())
CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", "10").strip())

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("MusicBot247")

YDL_OPTS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'default_search': 'ytsearch1',
    'extract_flat': False,
    'source_address': '0.0.0.0',
    'socket_timeout': 10
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ROTATING_STATUSES = [
    {"type": "stream", "name": "Música 24/7 🎵 [Meta: 1M Horas]"},
    {"type": "listening", "name": "Usa /play para poner rolitas 🎧"},
    {"type": "playing", "name": "DJ Beats & Corridos Bélicos 🔥"},
    {"type": "listening", "name": "Sonando en 🎵・Música 24/7 📻"},
    {"type": "watching", "name": "1,000,000 de Horas en Vivo 🏆"}
]


class MusicQueueManager:
    def __init__(self):
        self.queue: List[Dict] = []
        self.current_song: Optional[Dict] = None
        self.current_volume: float = 0.8
        self.is_paused: bool = False

    def add(self, song: Dict):
        self.queue.append(song)

    def next_song(self) -> Optional[Dict]:
        if self.queue:
            self.current_song = self.queue.pop(0)
            return self.current_song
        self.current_song = None
        return None

    def clear(self):
        self.queue.clear()
        self.current_song = None


def get_invite_url(client_id: str) -> str:
    return f"https://discord.com/oauth2/authorize?client_id={client_id}&permissions=8&scope=bot%20applications.commands"


def search_audio_track(query: str) -> Optional[Dict]:
    """Extrae metadatos y stream de audio con yt-dlp."""
    logger.info(f"🔎 Buscando audio para: '{query}'...")
    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            if not query.startswith("http://") and not query.startswith("https://"):
                query = f"ytsearch1:{query}"
            info = ydl.extract_info(query, download=False)
            if 'entries' in info and len(info['entries']) > 0:
                entry = info['entries'][0]
            else:
                entry = info

            duration = entry.get('duration', 0)
            mins, secs = divmod(duration, 60)
            dur_str = f"{int(mins):02d}:{int(secs):02d}" if duration else "En Vivo"

            return {
                'url': entry['url'],
                'webpage_url': entry.get('webpage_url', ''),
                'title': entry.get('title', 'Canción sin título'),
                'duration': dur_str,
                'thumbnail': entry.get('thumbnail', ''),
                'uploader': entry.get('uploader', 'Desconocido')
            }
    except Exception as e:
        logger.error(f"Error extrayendo audio con yt-dlp: {e}")
        return None


# Cliente Discord principal
intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True

bot_client = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot_client)

music_mgr = MusicQueueManager()
start_time = datetime.now(timezone.utc)
voice_client_ref: Optional[discord.VoiceClient] = None
is_connecting_lock = asyncio.Lock()


def get_uptime_str() -> str:
    delta = datetime.now(timezone.utc) - start_time
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    if days > 0:
        return f"{days}d {hours}h {minutes}m {seconds}s"
    return f"{hours}h {minutes}m {seconds}s"


async def update_bot_profile():
    """Configura el avatar futurista de DJ y el apodo del bot."""
    avatar_path = BASE_DIR.parent / "assets" / "music_bot_avatar.jpg"
    if avatar_path.exists():
        try:
            with open(avatar_path, "rb") as f:
                img_data = f.read()
            await bot_client.user.edit(avatar=img_data)
            logger.info("✅ Avatar del Music Bot actualizado con éxito (Cyber DJ Neón).")
        except discord.HTTPException as e:
            logger.info(f"Aviso de avatar (en cooldown o ya actualizado): {e}")
        except Exception as e:
            logger.warning(f"Error configurando avatar: {e}")

    guild = bot_client.get_guild(GUILD_ID)
    if guild:
        member = guild.get_member(bot_client.user.id)
        if member:
            try:
                await member.edit(nick="🎧 Music 24/7 [1M Horas]")
                logger.info("✅ Apodo del bot actualizado a '🎧 Music 24/7 [1M Horas]'")
            except Exception as e:
                logger.warning(f"Aviso al actualizar apodo: {e}")


async def presence_rotator_loop():
    """Rota estados dinámicos cuando no esté reproduciendo música."""
    await bot_client.wait_until_ready()
    idx = 0
    while not bot_client.is_closed():
        try:
            global voice_client_ref
            is_active_song = voice_client_ref and (voice_client_ref.is_playing() or voice_client_ref.is_paused())
            if not is_active_song:
                item = ROTATING_STATUSES[idx % len(ROTATING_STATUSES)]
                t = item.get("type")
                name = item.get("name")
                if t == "stream":
                    act = discord.Streaming(name=name, url="https://twitch.tv/music247")
                elif t == "listening":
                    act = discord.Activity(type=discord.ActivityType.listening, name=name)
                elif t == "watching":
                    act = discord.Activity(type=discord.ActivityType.watching, name=name)
                else:
                    act = discord.Activity(type=discord.ActivityType.playing, name=name)

                await bot_client.change_presence(status=discord.Status.online, activity=act)
                idx += 1
        except Exception as e:
            logger.debug(f"Aviso en rotador de presencia: {e}")
        await asyncio.sleep(15)


class ChangeMusicModal(discord.ui.Modal, title="🔄 Cambiar Canción"):
    cancion_input = discord.ui.TextInput(
        label="¿Qué canción quieres poner?",
        placeholder="Escribe el nombre de la rola o link de YouTube...",
        min_length=2,
        max_length=200,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        query = self.cancion_input.value.strip()
        track = search_audio_track(query)
        if not track:
            await interaction.followup.send(f"❌ No se encontró: `{query}`", ephemeral=True)
            return

        track['requester'] = interaction.user.display_name
        music_mgr.clear()
        music_mgr.current_song = track

        global voice_client_ref
        if voice_client_ref and voice_client_ref.is_connected():
            if voice_client_ref.is_playing() or voice_client_ref.is_paused():
                voice_client_ref.stop()

            try:
                audio = discord.FFmpegPCMAudio(track['url'], **FFMPEG_OPTIONS)
                source = discord.PCMVolumeTransformer(audio, volume=music_mgr.current_volume)

                def after_playback(err):
                    if err:
                        logger.error(f"Error en playback: {err}")
                    play_next_in_queue()

                voice_client_ref.play(source, after=after_playback)

                short_title = track['title'][:60]
                act = discord.Activity(type=discord.ActivityType.listening, name=short_title)
                await bot_client.change_presence(status=discord.Status.online, activity=act)

                embed = discord.Embed(
                    title="🔄 Canción Cambiada",
                    description=f"**[{track['title']}]({track['webpage_url']})**",
                    color=discord.Color.purple()
                )
                if track.get('thumbnail'):
                    embed.set_thumbnail(url=track['thumbnail'])
                embed.add_field(name="⏱️ Duración", value=f"`{track['duration']}`", inline=True)
                embed.add_field(name="👤 Cambiada por", value=interaction.user.mention, inline=True)
                embed.add_field(name="🔊 Volumen", value=f"`{int(music_mgr.current_volume * 100)}%`", inline=True)
                await interaction.followup.send(embed=embed, view=MusicControlView(track))
            except Exception as e:
                logger.error(f"Error cambiando canción: {e}")
                await interaction.followup.send(f"❌ Error al cambiar audio: `{e}`", ephemeral=True)


class MusicControlView(discord.ui.View):
    """Botonera interactiva para controlar la música directamente desde el embed."""
    def __init__(self, track_info: dict):
        super().__init__(timeout=None)
        self.track_info = track_info

    @discord.ui.button(label="Skip", style=discord.ButtonStyle.primary, emoji="⏭️", custom_id="music_skip")
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        global voice_client_ref
        if voice_client_ref and voice_client_ref.is_playing():
            curr = music_mgr.current_song.get('title', 'Canción actual') if music_mgr.current_song else 'Canción'
            voice_client_ref.stop()
            await interaction.response.send_message(f"⏭️ Se saltó: **{curr}**")
        else:
            await interaction.response.send_message("⚠️ No hay música reproduciéndose.", ephemeral=True)

    @discord.ui.button(label="Change Music", style=discord.ButtonStyle.success, emoji="🔄", custom_id="music_change")
    async def change_music(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ChangeMusicModal())

    @discord.ui.button(label="Quitarla", style=discord.ButtonStyle.danger, emoji="⏹️", custom_id="music_stop")
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        global voice_client_ref
        music_mgr.clear()
        if voice_client_ref and voice_client_ref.is_playing():
            voice_client_ref.stop()
        await interaction.response.send_message("⏹️ Música detenida y quitada del reproductor.")

    @discord.ui.button(label="Pausa / Play", style=discord.ButtonStyle.secondary, emoji="⏯️", custom_id="music_pause_resume")
    async def pause_resume(self, interaction: discord.Interaction, button: discord.ui.Button):
        global voice_client_ref
        if voice_client_ref:
            if voice_client_ref.is_playing():
                voice_client_ref.pause()
                music_mgr.is_paused = True
                await interaction.response.send_message("⏸️ Música pausada.", ephemeral=True)
            elif voice_client_ref.is_paused():
                voice_client_ref.resume()
                music_mgr.is_paused = False
                await interaction.response.send_message("▶️ Música reanudada.", ephemeral=True)
            else:
                await interaction.response.send_message("⚠️ No hay música en curso.", ephemeral=True)
        else:
            await interaction.response.send_message("⚠️ No estoy conectado a voz.", ephemeral=True)

    @discord.ui.button(label="Ver Cola", style=discord.ButtonStyle.secondary, emoji="📜", custom_id="music_queue")
    async def show_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        if music_mgr.queue:
            q_txt = "\n".join([f"**{i+1}.** {t['title']} `[{t['duration']}]`" for i, t in enumerate(music_mgr.queue[:5])])
            await interaction.response.send_message(f"📜 **Próximas en la cola:**\n{q_txt}", ephemeral=True)
        else:
            await interaction.response.send_message("📜 No hay más canciones en la cola.", ephemeral=True)


def play_next_in_queue():
    """Reproduce la siguiente canción en la cola de manera encadenada."""
    global voice_client_ref
    if voice_client_ref is None or not voice_client_ref.is_connected():
        return

    next_track = music_mgr.next_song()
    if not next_track:
        return

    try:
        audio = discord.FFmpegPCMAudio(next_track['url'], **FFMPEG_OPTIONS)
        source = discord.PCMVolumeTransformer(audio, volume=music_mgr.current_volume)

        def after_playback(err):
            if err:
                logger.error(f"Error en playback: {err}")
            play_next_in_queue()

        voice_client_ref.play(source, after=after_playback)

        short_title = next_track['title'][:60]
        act = discord.Activity(
            type=discord.ActivityType.listening,
            name=short_title
        )
        asyncio.run_coroutine_threadsafe(
            bot_client.change_presence(status=discord.Status.online, activity=act),
            bot_client.loop
        )
        logger.info(f"▶️ Reproduciendo ahora: {next_track['title']}")
    except Exception as e:
        logger.error(f"Error iniciando reproducción: {e}")
        play_next_in_queue()


async def ensure_voice_connection():
    """Garantiza conexión ininterrumpida las 24 horas del día."""
    global voice_client_ref
    async with is_connecting_lock:
        try:
            guild = bot_client.get_guild(GUILD_ID)
            if guild is None:
                invite = get_invite_url(BOT_ID)
                logger.warning(f"Bot no está en el servidor {GUILD_ID}. Invítalo con:\n{invite}")
                return

            channel = guild.get_channel(VOICE_CHANNEL_ID)
            if channel is None:
                logger.warning(f"No se encontró el canal de voz {VOICE_CHANNEL_ID} en {guild.name}")
                return

            vc = guild.voice_client

            if vc is not None:
                voice_client_ref = vc
                if vc.channel.id != VOICE_CHANNEL_ID:
                    logger.info(f"Movido de canal. Regresando a '{channel.name}'...")
                    await vc.move_to(channel)
                    return

                if vc.is_connected():
                    return
                else:
                    logger.warning("Conexión de voz colapsó. Forzando reconexión...")
                    try:
                        await vc.disconnect(force=True)
                    except Exception:
                        pass
                    await asyncio.sleep(1)

            logger.info(f"Conectando 24/7 a canal de voz '{channel.name}' (ID: {channel.id})...")
            try:
                vc = await channel.connect(
                    reconnect=True,
                    self_deaf=False,
                    self_mute=False,
                    timeout=30.0
                )
                voice_client_ref = vc
                logger.info(f"\033[92m¡CONECTADO PERMANENTEMENTE A '{channel.name}'! (Rumbo a 1 Millón de Horas)\033[0m")
            except discord.errors.ClientException as e:
                if "already connected" not in str(e).lower():
                    logger.warning(f"Aviso de conexión: {e}")
            except Exception as e:
                logger.error(f"Error conectando a voz: {e}")

        except Exception as e:
            logger.error(f"Error en ensure_voice_connection: {e}")


async def voice_keeper_loop():
    """Bucle guardián que verifica la permanencia cada CHECK_INTERVAL_SECONDS segundos."""
    await bot_client.wait_until_ready()
    while not bot_client.is_closed():
        try:
            await ensure_voice_connection()
        except Exception as e:
            logger.error(f"Error en bucle guardián: {e}")
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)


@bot_client.event
async def on_ready():
    invite = get_invite_url(BOT_ID or str(bot_client.user.id))
    print("\n" + "=" * 65)
    print(f"       \033[92m{BOT_NAME} ONLINE - MÚSICA 24/7 (1M DE HORAS)\033[0m")
    print("=" * 65)
    print(f" » Bot User:      {bot_client.user} (ID: {bot_client.user.id})")
    print(f" » Canal de Voz:  ID {VOICE_CHANNEL_ID}")
    print(f" » Enlace Invitar:{invite}")
    print("=" * 65 + "\n")

    # 1. Configurar perfil y avatar
    await update_bot_profile()

    # 2. Iniciar rotador de estados animados
    asyncio.create_task(presence_rotator_loop())

    # 3. Sincronizar Slash Commands directamente en el servidor (instantáneo y con AUTOCOMPLETE)
    try:
        guild_obj = discord.Object(id=GUILD_ID)
        tree.copy_global_to(guild=guild_obj)
        tree.clear_commands(guild=None)
        await tree.sync()
        await tree.sync(guild=guild_obj)
        logger.info("✅ Slash commands con AUTOCOMPLETE sincronizados en el servidor al instante.")
    except Exception as e:
        logger.warning(f"Aviso al sincronizar slash commands: {e}")

    await ensure_voice_connection()


@bot_client.event
async def on_voice_state_update(member, before, after):
    """Si el bot es desconectado o movido por alguien, regresa de inmediato."""
    if member.id == bot_client.user.id:
        if after.channel is None:
            logger.warning("Desconectado de llamada de voz. Reconectando en 2 segundos...")
            await asyncio.sleep(2)
            await ensure_voice_connection()
            return
        if after.channel.id != VOICE_CHANNEL_ID:
            logger.warning(f"Movido al canal '{after.channel.name}'. Regresando a canal oficial...")
            await asyncio.sleep(1)
            guild = bot_client.get_guild(GUILD_ID)
            target = guild.get_channel(VOICE_CHANNEL_ID) if guild else None
            if target and guild.voice_client:
                try:
                    await guild.voice_client.move_to(target)
                except Exception as e:
                    logger.error(f"Error regresando a canal: {e}")


# ==========================================
# SLASH COMMANDS (/play, /skip, /stop, etc.)
# ==========================================

@tree.command(name="play", description="🎵 Reproduce música o agrega una canción a la cola")
@app_commands.describe(cancion="Nombre de la canción o enlace de YouTube/audio")
async def slash_play(interaction: discord.Interaction, cancion: str):
    await interaction.response.defer()
    await ensure_voice_connection()

    global voice_client_ref
    if voice_client_ref is None or not voice_client_ref.is_connected():
        await interaction.followup.send("⚠️ No estoy conectado al canal de voz aún. Intenta en unos segundos.")
        return

    track = search_audio_track(cancion)
    if not track:
        await interaction.followup.send(f"❌ No se pudo encontrar ningún resultado para: `{cancion}`")
        return

    track['requester'] = interaction.user.display_name

    embed = discord.Embed(color=discord.Color.purple())
    if track.get('thumbnail'):
        embed.set_thumbnail(url=track['thumbnail'])

    if voice_client_ref.is_playing() or voice_client_ref.is_paused():
        music_mgr.add(track)
        pos = len(music_mgr.queue)
        embed.title = "🎶 Agregado a la Cola"
        embed.description = f"**[{track['title']}]({track['webpage_url']})**"
        embed.add_field(name="⏱️ Duración", value=f"`{track['duration']}`", inline=True)
        embed.add_field(name="📍 Posición", value=f"`#{pos}`", inline=True)
        embed.add_field(name="👤 Pedido por", value=interaction.user.mention, inline=True)
        await interaction.followup.send(embed=embed)
    else:
        music_mgr.current_song = track
        try:
            audio = discord.FFmpegPCMAudio(track['url'], **FFMPEG_OPTIONS)
            source = discord.PCMVolumeTransformer(audio, volume=music_mgr.current_volume)

            def after_play(err):
                if err:
                    logger.error(f"Error en reproducción: {err}")
                play_next_in_queue()

            voice_client_ref.play(source, after=after_play)

            short_title = track['title'][:60]
            act = discord.Activity(type=discord.ActivityType.listening, name=short_title)
            await bot_client.change_presence(status=discord.Status.online, activity=act)

            embed.title = "▶️ Reproduciendo Ahora"
            embed.description = f"**[{track['title']}]({track['webpage_url']})**"
            embed.add_field(name="⏱️ Duración", value=f"`{track['duration']}`", inline=True)
            embed.add_field(name="👤 Pedido por", value=interaction.user.mention, inline=True)
            embed.add_field(name="🔊 Volumen", value=f"`{int(music_mgr.current_volume * 100)}%`", inline=True)
            embed.set_footer(text="🎧 Bot de Música 24/7 • Rumbo a 1,000,000 de Horas")
            await interaction.followup.send(embed=embed, view=MusicControlView(track))
        except Exception as e:
            logger.error(f"Error reproduciendo audio: {e}")
            await interaction.followup.send(f"❌ Error al reproducir audio: `{e}`")


def fetch_youtube_songs(query: str) -> List[app_commands.Choice[str]]:
    """Busca canciones reales de todo el mundo en YouTube y las filtra limpiamente."""
    opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
        'default_search': 'ytsearch25',
        'socket_timeout': 3,
        'source_address': '0.0.0.0'
    }
    choices = []
    seen_ids = set()
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            res = ydl.extract_info(f"ytsearch25:{query}", download=False)
            if res and 'entries' in res:
                for entry in res['entries']:
                    if not entry:
                        continue
                    video_id = entry.get('id', '')
                    if not video_id or video_id.startswith('UC') or entry.get('_type') == 'channel' or video_id in seen_ids:
                        continue
                    seen_ids.add(video_id)

                    title = entry.get('title', '')
                    if not title:
                        continue

                    clean_title = (
                        title.replace("[Video Oficial]", "")
                        .replace("(Video Oficial)", "")
                        .replace("(Official Video)", "")
                        .replace("[Official Video]", "")
                        .replace("(Lyric Video)", "")
                        .replace("[Lyric Video]", "")
                        .replace("(Video Lyric)", "")
                        .replace("(Audio Oficial)", "")
                        .strip()
                    )

                    display_name = f"🎵 {clean_title}"[:100]
                    val = f"https://www.youtube.com/watch?v={video_id}"
                    choices.append(app_commands.Choice(name=display_name, value=val))
                    if len(choices) >= 25:
                        break
    except Exception as e:
        logger.debug(f"Aviso buscando canciones para autocomplete: {e}")
    return choices


@slash_play.autocomplete('cancion')
async def play_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> List[app_commands.Choice[str]]:
    current = current.strip()
    if not current:
        return [
            app_commands.Choice(name="🔥 Peso Pluma & Tito Double P - LA PATRULLA", value="Peso Pluma LA PATRULLA"),
            app_commands.Choice(name="🔥 El Makabelico - El Comando Exclusivo", value="makabelico comando exclusivo"),
            app_commands.Choice(name="⚡ Natanael Cano & Peso Pluma - PRC", value="Peso Pluma Natanael Cano PRC"),
            app_commands.Choice(name="👑 Bad Bunny - Tití Me Preguntó", value="Bad Bunny Titi Me Pregunto"),
            app_commands.Choice(name="🏎️ Phonk Drift Mix 2026 Gamer", value="phonk drift gamer mix"),
            app_commands.Choice(name="🎧 Lo-Fi Beats 24/7 Chill", value="lofi hip hop radio beats to relax"),
            app_commands.Choice(name="🎶 Fuerza Regida & Grupo Frontera - Bebe Dame", value="Fuerza Regida Bebe Dame"),
            app_commands.Choice(name="💀 El Makabelico - El Ondeado", value="El Makabelico El Ondeado"),
            app_commands.Choice(name="🔥 Gabito Ballesteros - LOU LOU", value="Gabito Ballesteros LOU LOU"),
            app_commands.Choice(name="🎵 Junior H - Fin de Semana", value="Junior H Fin de Semana")
        ]

    # 1. Intentar buscar canciones reales filtradas en todo el mundo con yt-dlp
    try:
        choices = await asyncio.wait_for(
            asyncio.to_thread(fetch_youtube_songs, current),
            timeout=2.2
        )
        if choices:
            return choices[:25]
    except Exception as e:
        logger.debug(f"Aviso en fetch_youtube_songs timeout/error: {e}")

    # 2. Fallback de sugerencias directas
    choices = []
    try:
        url = f"https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&hl=es&gl=mx&q={aiohttp.helpers.quote(current)}"
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=0.7)) as session:
            async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}) as resp:
                if resp.status == 200:
                    data = await resp.json(content_type=None)
                    if len(data) > 1 and isinstance(data[1], list):
                        for item in data[1][:15]:
                            clean_str = str(item).strip()
                            choices.append(app_commands.Choice(name=f"🎵 {clean_str[:95]}", value=clean_str[:100]))
    except Exception as e:
        logger.debug(f"Aviso en suggest query: {e}")

    if not choices:
        choices.append(app_commands.Choice(name=f"🔍 Buscar '{current[:80]}'", value=current[:100]))

    return choices[:25]


@tree.command(name="skip", description="⏭️ Salta a la siguiente canción en la cola")
async def slash_skip(interaction: discord.Interaction):
    global voice_client_ref
    if voice_client_ref and voice_client_ref.is_playing():
        curr = music_mgr.current_song.get('title', 'Canción actual') if music_mgr.current_song else 'Canción'
        voice_client_ref.stop()
        await interaction.response.send_message(f"⏭️ Se saltó: **{curr}**")
    else:
        await interaction.response.send_message("⚠️ No hay ninguna canción reproduciéndose.")


@tree.command(name="stop", description="⏹️ Detiene la música y limpia la cola (permanece 24/7 en voz)")
async def slash_stop(interaction: discord.Interaction):
    global voice_client_ref
    music_mgr.clear()
    if voice_client_ref and voice_client_ref.is_playing():
        voice_client_ref.stop()
    await interaction.response.send_message("⏹️ **Música detenida y cola vaciada.**\n*(Yo permanezco en el canal de voz 24/7 sin salirme jamás)*")


@tree.command(name="pause", description="⏸️ Pausa la música actual")
async def slash_pause(interaction: discord.Interaction):
    global voice_client_ref
    if voice_client_ref and voice_client_ref.is_playing():
        voice_client_ref.pause()
        music_mgr.is_paused = True
        await interaction.response.send_message("⏸️ Música pausada. Usa `/resume` para continuar.")
    else:
        await interaction.response.send_message("⚠️ No hay música reproduciéndose.")


@tree.command(name="resume", description="▶️ Reanuda la música pausada")
async def slash_resume(interaction: discord.Interaction):
    global voice_client_ref
    if voice_client_ref and voice_client_ref.is_paused():
        voice_client_ref.resume()
        music_mgr.is_paused = False
        await interaction.response.send_message("▶️ Música reanudada.")
    else:
        await interaction.response.send_message("⚠️ La música no está pausada.")


@tree.command(name="queue", description="📋 Muestra la lista de canciones en la cola")
async def slash_queue(interaction: discord.Interaction):
    embed = discord.Embed(title="📜 Cola Musical", color=discord.Color.blue())
    if music_mgr.current_song:
        embed.add_field(
            name="▶️ Sonando Ahora",
            value=f"**{music_mgr.current_song['title']}** `[{music_mgr.current_song['duration']}]`",
            inline=False
        )

    if music_mgr.queue:
        tracks_txt = "\n".join([f"**{i+1}.** {t['title']} `[{t['duration']}]`" for i, t in enumerate(music_mgr.queue[:10])])
        if len(music_mgr.queue) > 10:
            tracks_txt += f"\n*... y {len(music_mgr.queue) - 10} canciones más*"
        embed.add_field(name="Próximas en la cola", value=tracks_txt, inline=False)
    else:
        embed.add_field(name="Próximas en la cola", value="No hay más canciones en la cola.", inline=False)

    await interaction.response.send_message(embed=embed)


@tree.command(name="nowplaying", description="🎵 Muestra los detalles de la canción actual")
async def slash_np(interaction: discord.Interaction):
    if not music_mgr.current_song:
        await interaction.response.send_message("💤 No hay ninguna canción reproduciéndose actualmente.")
        return

    t = music_mgr.current_song
    embed = discord.Embed(title="🎵 Sonando Ahora", description=f"**[{t['title']}]({t.get('webpage_url', '')})**", color=discord.Color.purple())
    if t.get('thumbnail'):
        embed.set_thumbnail(url=t['thumbnail'])
    embed.add_field(name="⏱️ Duración", value=f"`{t['duration']}`", inline=True)
    embed.add_field(name="👤 Pedido por", value=t.get('requester', 'Desconocido'), inline=True)
    embed.add_field(name="🔊 Volumen", value=f"`{int(music_mgr.current_volume * 100)}%`", inline=True)
    await interaction.response.send_message(embed=embed)


@tree.command(name="volume", description="🔊 Ajusta el volumen del reproductor (1-100)")
@app_commands.describe(nivel="Porcentaje de volumen del 1 al 100")
async def slash_volume(interaction: discord.Interaction, nivel: int):
    nivel = max(1, min(100, nivel))
    music_mgr.current_volume = nivel / 100.0
    global voice_client_ref
    if voice_client_ref and voice_client_ref.source:
        try:
            voice_client_ref.source.volume = music_mgr.current_volume
        except Exception:
            pass
    await interaction.response.send_message(f"🔊 Volumen ajustado a: **{nivel}%**")


@tree.command(name="stats", description="📊 Muestra las horas acumuladas en el canal rumbo a 1 Millón de Horas")
async def slash_stats(interaction: discord.Interaction):
    uptime = get_uptime_str()
    embed = discord.Embed(
        title="🏆 Estadísticas 24/7 - Rumbo a 1,000,000 de Horas",
        description="Este bot está programado para quedarse en el canal de voz permanentemente sin apagarse jamás.",
        color=discord.Color.gold()
    )
    embed.add_field(name="⏱️ Tiempo Conectado en Esta Sesión", value=f"`{uptime}`", inline=False)
    embed.add_field(name="🎯 Meta", value="`1,000,000 Horas`", inline=True)
    embed.add_field(name="🎙️ Canal de Voz Asignado", value=f"<#{VOICE_CHANNEL_ID}>", inline=True)
    embed.add_field(name="🛡️ Estado de Conexión", value="🟢 **Permanente 24/7 Activo**", inline=False)
    await interaction.response.send_message(embed=embed)


async def main():
    if not BOT_TOKEN:
        logger.error("No se encontró BOT_TOKEN en el archivo .env")
        sys.exit(1)

    # Iniciar bucle guardián en segundo plano
    asyncio.create_task(voice_keeper_loop())
    await bot_client.start(BOT_TOKEN)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot apagado manualmente.")
    except Exception as e:
        logger.critical(f"Error fatal: {e}")
