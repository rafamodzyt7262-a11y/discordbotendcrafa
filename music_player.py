import random
import logging
import yt_dlp
import discord

logger = logging.getLogger("MusicPlayer")

RANDOM_MUSIC_QUERIES = [
    "makabelico comando exclusivo",
    "el makabelico pongale musica",
    "makabelico comando belico",
    "corridos belicos mix",
    "corridos tumbados mix",
    "phonk drift mix gamer",
    "trap latino mix",
    "reggaeton mix callejero"
]

YDL_OPTS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'default_search': 'ytsearch1',
    'extract_flat': False
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}


class MusicManager:
    def __init__(self):
        self.is_playing_music = False
        self.current_title = ""

    def search_song(self, query: str):
        if not query or query.strip().lower() in ["random", "aleatoria", "cualquiera", "algo"]:
            query = random.choice(RANDOM_MUSIC_QUERIES)
        elif "makabelico" in query.lower() or "comando" in query.lower():
            query = "makabelico comando exclusivo"

        logger.info(f"🔎 Buscando canción para: '{query}'...")
        try:
            with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
                info = ydl.extract_info(f"ytsearch1:{query}", download=False)
                if 'entries' in info and len(info['entries']) > 0:
                    entry = info['entries'][0]
                    return entry['url'], entry.get('title', query)
        except Exception as e:
            logger.error(f"Error al buscar audio en yt-dlp: {e}")
        return None, None

    def play_song(self, voice_client: discord.VoiceClient, query: str):
        url, title = self.search_song(query)
        if not url:
            return False, "No encontré esa canción, carnal."

        try:
            if voice_client.is_playing():
                voice_client.stop()

            source = discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS)
            self.is_playing_music = True
            self.current_title = title

            def after_play(error):
                self.is_playing_music = False
                if error:
                    logger.error(f"Error durante playback musical: {error}")
                else:
                    logger.info("🎵 Terminó la reproducción de música.")

            voice_client.play(source, after=after_play)
            return True, title
        except Exception as e:
            logger.error(f"Error al reproducir audio musical: {e}")
            self.is_playing_music = False
            return False, str(e)

    def stop_song(self, voice_client: discord.VoiceClient):
        if voice_client and voice_client.is_playing():
            voice_client.stop()
        self.is_playing_music = False
        self.current_title = ""
