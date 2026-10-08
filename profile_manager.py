import os
import asyncio
import aiohttp
import logging
from pathlib import Path
import discord

logger = logging.getLogger("ProfileManager")

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)


class StatusAnimator:
    """Maneja estados rotativos animados para dar la sensación de un perfil vivo y en movimiento."""
    def __init__(self):
        self.bot1_active = True
        self.bot2_active = True
        self.bot1_index = 0
        self.bot2_index = 0
        self.interval = 15  # Cada 15 segundos cambia (cumple rate limit de Discord)

        # Estados rotativos por defecto para Kevin 17
        self.bot1_items = [
            {"type": "playing", "name": "Amo A Karen 💖"},
            {"type": "listening", "name": "Makabelico y Corridos 🎧"},
            {"type": "playing", "name": "Kevin 17 Modo Bélico ⚡"},
            {"type": "playing", "name": "Llamada 24/7 (1M Horas) 📞"},
            {"type": "watching", "name": "Cuidando a Karen 👀"}
        ]

        # Estados rotativos por defecto para RafaModzYT
        self.bot2_items = [
            {"type": "stream", "name": "Adicto Alas Tetas [LIVE]"},
            {"type": "playing", "name": "RafaModzYT Oficial 👑"},
            {"type": "listening", "name": "Corridos Pesados 24/7 🔥"},
            {"type": "playing", "name": "Troka Blindada 🏎️"},
            {"type": "watching", "name": "Contenido Exclusivo 🍑"}
        ]
        self._tasks = {}

    def get_activity(self, item: dict) -> discord.Activity:
        t = item.get("type", "playing")
        name = item.get("name", "")
        if t == "stream":
            return discord.Streaming(name=name, url="https://twitch.tv/rafamodzyt")
        elif t == "listening":
            return discord.Activity(type=discord.ActivityType.listening, name=name)
        elif t == "watching":
            return discord.Activity(type=discord.ActivityType.watching, name=name)
        else:
            return discord.Activity(type=discord.ActivityType.playing, name=name)

    async def start(self, bot_client: discord.Client, is_bot1: bool):
        key = "bot1" if is_bot1 else "bot2"
        if key in self._tasks and not self._tasks[key].done():
            return
        self._tasks[key] = asyncio.create_task(self._loop(bot_client, is_bot1))

    async def _loop(self, bot_client: discord.Client, is_bot1: bool):
        await asyncio.sleep(5)  # Espera inicial tras conexión
        while True:
            try:
                active = self.bot1_active if is_bot1 else self.bot2_active
                items = self.bot1_items if is_bot1 else self.bot2_items
                if active and items and bot_client.is_ready():
                    idx = (self.bot1_index if is_bot1 else self.bot2_index) % len(items)
                    item = items[idx]
                    activity = self.get_activity(item)
                    status_to_use = discord.Status.dnd if is_bot1 else discord.Status.online
                    await bot_client.change_presence(status=status_to_use, activity=activity)
                    if is_bot1:
                        self.bot1_index = (self.bot1_index + 1) % len(items)
                    else:
                        self.bot2_index = (self.bot2_index + 1) % len(items)
            except Exception as e:
                logger.debug(f"Aviso en loop de animación: {e}")
            await asyncio.sleep(self.interval)

    def set_active(self, is_bot1: bool, active: bool):
        if is_bot1:
            self.bot1_active = active
        else:
            self.bot2_active = active

    def set_custom_phrases(self, is_bot1: bool, phrases: list):
        items = [{"type": "playing", "name": p.strip()} for p in phrases if p.strip()]
        if not items:
            return False
        if is_bot1:
            self.bot1_items = items
            self.bot1_active = True
            self.bot1_index = 0
        else:
            self.bot2_items = items
            self.bot2_active = True
            self.bot2_index = 0
        return True


status_animator = StatusAnimator()


async def handle_profile_customization(message: discord.Message, bot_client: discord.Client, is_bot1: bool, bot_name: str) -> bool:
    """
    Permite personalizar el perfil completo del bot desde su canal de control:
    - Enviar imagen/GIF o !avatar: cambia la foto de perfil o avatar animado.
    - !nombre <nuevo nombre>: cambia el apodo/nombre del bot.
    - !estado <texto>: cambia la actividad que está jugando/haciendo fija.
    - !animacion on/off/frases: activa o configura estados animados rotativos.
    - !tipo <jugando/stream/escuchando/viendo>: cambia el tipo de actividad.
    - !presencia <online/dnd/idle>: cambia el estado verde, rojo o amarillo.
    - !perfil: muestra la tarjeta completa del bot.
    - !ayuda: muestra los comandos disponibles.
    """
    content = message.content.strip()
    content_lower = content.lower()

    # 1. Cambio de Foto de Perfil o Avatar Animado (soporta PNG, JPG, WEBP y GIF animado)
    if message.attachments or content_lower.startswith("!avatar") or content_lower.startswith("!foto"):
        image_url = None
        is_gif = False
        if message.attachments:
            # Si subió un archivo adjunto directamente
            for att in message.attachments:
                fname = att.filename.lower()
                if any(fname.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".webp", ".gif"]):
                    image_url = att.url
                    if fname.endswith(".gif"):
                        is_gif = True
                    break
        elif len(content.split()) > 1:
            # Si pasó una URL: !avatar https://...
            image_url = content.split()[1]
            if ".gif" in image_url.lower():
                is_gif = True

        if image_url:
            tipo_label = "Avatar Animado (GIF)" if is_gif else "Foto de Perfil"
            status_msg = await message.channel.send(f"⏳ Descargando y aplicando **{tipo_label}** a **{bot_name}**...")
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(image_url) as resp:
                        if resp.status == 200:
                            img_data = await resp.read()
                            await bot_client.user.edit(avatar=img_data)
                            await status_msg.edit(content=f"✅ **¡{tipo_label} de {bot_name} actualizado con éxito!** ✨")
                            return True
                        else:
                            await status_msg.edit(content="❌ No se pudo descargar la imagen proporcionada.")
            except discord.HTTPException as e:
                await status_msg.edit(content=f"⚠️ Discord limitó temporalmente el cambio de foto (rate limit de 10 min de Discord): `{e}`")
            except Exception as e:
                await status_msg.edit(content=f"❌ Error al cambiar avatar: `{e}`")
            return True

    # 2. Comando !nombre (Cambia apodo en el servidor)
    # 2. Comando !nombre (Cambia apodo en el servidor y nombre del bot)
    if any(content_lower.startswith(p) for p in ["!nombre", "!apodo", "nombre:", "cambiar nombre"]):
        parts = content.split(" ", 1)
        if len(parts) > 1:
            new_name = parts[1].strip()
            guild = message.guild
            changed_nick = False
            if guild:
                member = guild.get_member(bot_client.user.id)
                if member:
                    try:
                        await member.edit(nick=new_name)
                        changed_nick = True
                    except Exception as e:
                        logger.warning(f"No se pudo cambiar apodo en servidor: {e}")

            # Intentar cambiar username global del bot si es posible
            try:
                await bot_client.user.edit(username=new_name)
                await message.channel.send(f"✅ **Nombre y Apodo de {bot_name} cambiados con éxito a:** `{new_name}`")
            except Exception:
                if changed_nick:
                    await message.channel.send(f"✅ **Apodo en el servidor cambiado a:** `{new_name}` (Discord limita cambiar el username global a 2 veces por hora)")
                else:
                    await message.channel.send(f"⚠️ No pude actualizar el apodo. Asegúrate de que mi rol esté arriba.")
        else:
            await message.channel.send("Uso: `!nombre [Nuevo Nombre]`")
        return True

    # 3. Comando !estado (Cambia el texto de lo que está jugando/haciendo fijo)
    if any(content_lower.startswith(p) for p in ["!estado", "!status", "estado:", "cambiar estado"]):
        parts = content.split(" ", 1)
        if len(parts) > 1:
            new_state = parts[1].strip()
            status_animator.set_active(is_bot1, False)  # Pausar rotación animada para fijar este estado
            act = discord.Activity(type=discord.ActivityType.playing, name=new_state, state=new_state)
            await bot_client.change_presence(activity=act)
            await message.channel.send(f"✅ Actividad fija de **{bot_name}** actualizada a: **Jugando a {new_state}**\n*(Rotación animada pausada. Escribe `!animacion on` si quieres reactivar los estados en movimiento)*")
        else:
            await message.channel.send("Uso: `!estado [Texto de la actividad]` (Ejemplo: `!estado Amo A Karen`)")
        return True

    # 4. Comando !animacion (Manejo de estados animados y rotativos en vivo)
    if any(content_lower.startswith(p) for p in ["!animacion", "!animar", "animacion:"]):
        parts = content.split(" ", 1)
        if len(parts) > 1:
            sub = parts[1].strip()
            sub_lower = sub.lower()
            if sub_lower in ["on", "activar", "si", "start"]:
                status_animator.set_active(is_bot1, True)
                await message.channel.send(f"🔄 **¡Animación de perfil activada para {bot_name}!** Su estado irá rotando automáticamente cada 15 segundos.")
            elif sub_lower in ["off", "desactivar", "pausar", "stop"]:
                status_animator.set_active(is_bot1, False)
                await message.channel.send(f"⏸️ **Animación de perfil pausada para {bot_name}.** Su estado permanecerá fijo.")
            elif sub_lower in ["lista", "ver"]:
                items = status_animator.bot1_items if is_bot1 else status_animator.bot2_items
                lista_txt = "\n".join([f"{i+1}. `{it.get('name')}`" for i, it in enumerate(items)])
                await message.channel.send(f"📋 **Estados que rotan en la animación de {bot_name}:**\n{lista_txt}")
            elif "|" in sub:
                phrases = sub.split("|")
                if status_animator.set_custom_phrases(is_bot1, phrases):
                    await message.channel.send(f"✨ **¡Animación personalizada creada para {bot_name}!**\nAhora rotará entre estas {len(phrases)} frases cada 15 segundos.")
                else:
                    await message.channel.send("⚠️ No se pudieron procesar las frases. Ejemplo: `!animacion Frase 1 | Frase 2 | Frase 3`")
            else:
                await message.channel.send("Uso:\n• `!animacion on` (Activar rotación)\n• `!animacion off` (Pausar)\n• `!animacion frase 1 | frase 2 | frase 3` (Personalizar frases)\n• `!animacion lista` (Ver frases)")
        else:
            await message.channel.send("Uso: `!animacion [on / off / lista / frase 1 | frase 2 | frase 3]`")
        return True

    # 5. Comando !tipo (Cambia a stream, jugando, escuchando)
    if any(content_lower.startswith(p) for p in ["!tipo", "tipo:"]):
        parts = content.split(" ", 2)
        if len(parts) > 1:
            status_animator.set_active(is_bot1, False)  # Pausar rotación animada
            tipo = parts[1].lower()
            texto = parts[2] if len(parts) > 2 else "En Vivo"
            if "stream" in tipo:
                act = discord.Streaming(name=texto, url="https://twitch.tv/rafamodzyt")
                await bot_client.change_presence(activity=act)
                await message.channel.send(f"🟣 Actividad de **{bot_name}** actualizada a: **Transmitiendo {texto} [LIVE]**")
            elif "escuchando" in tipo or "musica" in tipo:
                act = discord.Activity(type=discord.ActivityType.listening, name=texto)
                await bot_client.change_presence(activity=act)
                await message.channel.send(f"🎧 Actividad de **{bot_name}** actualizada a: **Escuchando {texto}**")
            elif "viendo" in tipo or "pelicula" in tipo:
                act = discord.Activity(type=discord.ActivityType.watching, name=texto)
                await bot_client.change_presence(activity=act)
                await message.channel.send(f"📺 Actividad de **{bot_name}** actualizada a: **Viendo {texto}**")
            else:
                act = discord.Activity(type=discord.ActivityType.playing, name=texto)
                await bot_client.change_presence(activity=act)
                await message.channel.send(f"🎮 Actividad de **{bot_name}** actualizada a: **Jugando a {texto}**")
        else:
            await message.channel.send("Uso: `!tipo [stream/jugando/escuchando/viendo] [texto]`")
        return True

    # 6. Comando !presencia (Online 🟢, DND 🔴, Idle 🟡)
    if any(content_lower.startswith(p) for p in ["!presencia", "!color", "presencia:"]):
        parts = content.split(" ", 1)
        if len(parts) > 1:
            p = parts[1].lower()
            if "dnd" in p or "rojo" in p or "molestar" in p:
                await bot_client.change_presence(status=discord.Status.dnd)
                await message.channel.send(f"🔴 Estado de **{bot_name}** cambiado a: **No Molestar**")
            elif "idle" in p or "amarillo" in p or "ausente" in p:
                await bot_client.change_presence(status=discord.Status.idle)
                await message.channel.send(f"🟡 Estado de **{bot_name}** cambiado a: **Ausente**")
            else:
                await bot_client.change_presence(status=discord.Status.online)
                await message.channel.send(f"🟢 Estado de **{bot_name}** cambiado a: **Conectado**")
        else:
            await message.channel.send("Uso: `!presencia [online/dnd/idle]`")
        return True

    # 7. Comando !perfil (Muestra la tarjeta actual)
    if content_lower in ["!perfil", "!status", "perfil", "status"]:
        guild = message.guild
        member = guild.get_member(bot_client.user.id) if guild else None
        current_activity = bot_client.activity.name if bot_client.activity else "Ninguna"
        is_animating = status_animator.bot1_active if is_bot1 else status_animator.bot2_active
        embed = discord.Embed(
            title=f"🎛️ Panel de Control - {bot_name}",
            description=f"Personalización en tiempo real para **{bot_client.user}**",
            color=discord.Color.red() if is_bot1 else discord.Color.purple()
        )
        embed.set_thumbnail(url=bot_client.user.display_avatar.url)
        embed.add_field(name="📛 Nombre / Apodo", value=member.display_name if member else bot_client.user.name, inline=True)
        embed.add_field(name="🎮 Actividad Actual", value=current_activity, inline=True)
        embed.add_field(name="🟢 Presencia", value=str(bot_client.status).capitalize(), inline=True)
        embed.add_field(name="🔄 Estado Animado", value="Activo (Rotando frases) ✨" if is_animating else "Pausado (Fijo)", inline=False)
        embed.set_footer(text="Arrastra fotos/GIFs o escribe !ayuda para ver todos los comandos.")
        await message.channel.send(embed=embed)
        return True

    # 8. Comando !ayuda
    if content_lower in ["!ayuda", "!help", "ayuda", "comandos"]:
        embed = discord.Embed(
            title=f"🛠️ Comandos de Personalización - {bot_name}",
            description="Usa estos comandos en este canal para personalizar al bot:",
            color=discord.Color.gold()
        )
        embed.add_field(name="🖼️ Avatar Fijo o Animado (GIF)", value="Arrastra cualquier imagen o **GIF animado** aquí, o escribe `!avatar [enlace.gif]`", inline=False)
        embed.add_field(name="🔄 Animación de Perfil en Vivo", value="`!animacion on` / `!animacion off` / `!animacion Frase 1 | Frase 2 | Frase 3` (El estado cambia automáticamente cada 15s)", inline=False)
        embed.add_field(name="📛 Cambiar Apodo / Nombre", value="`!nombre [Nuevo Nombre]`", inline=False)
        embed.add_field(name="🎮 Actividad Fija", value="`!estado [Texto]`", inline=False)
        embed.add_field(name="🟣 Modo Stream / TV", value="`!tipo stream [Texto]` (Insignia LIVE morada)", inline=False)
        embed.add_field(name="🟢 Color de Estado", value="`!presencia [online/dnd/idle]`", inline=False)
        embed.add_field(name="📊 Ver Tarjeta Actual", value="`!perfil`", inline=False)
        await message.channel.send(embed=embed)
        return True

    return False
