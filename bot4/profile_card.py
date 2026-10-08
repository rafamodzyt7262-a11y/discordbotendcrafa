import io
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Any

def create_ff_profile_image(data: Dict[str, Any]) -> io.BytesIO:
    """Genera una tarjeta visual de estadísticas idéntica al estilo de la foto."""
    width = 800
    height = 420
    
    # Fondo oscuro profesional FF
    bg_color = (18, 18, 22)
    card_bg = (28, 28, 34)
    border_color = (45, 45, 55)
    accent_blue = (52, 152, 219)
    accent_gold = (241, 196, 15)
    text_white = (245, 245, 245)
    text_muted = (160, 160, 175)
    
    img = Image.new("RGBA", (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Fuentes por defecto del sistema
    try:
        font_large = ImageFont.truetype("arial.ttf", 26)
        font_med = ImageFont.truetype("arial.ttf", 18)
        font_small = ImageFont.truetype("arial.ttf", 14)
        font_title = ImageFont.truetype("arial.ttf", 20)
    except Exception:
        font_large = font_med = font_small = font_title = ImageFont.load_default()

    # Panel Izquierdo: Resumen Cuenta
    draw.rounded_rectangle([20, 20, 380, 200], radius=10, fill=card_bg, outline=border_color, width=1)
    draw.text((35, 35), f"🔷 {data['nickname']}", fill=text_white, font=font_large)
    draw.text((35, 75), f"ID: {data['uid']}  ·  Region: {data['region']}", fill=text_muted, font=font_small)
    draw.text((35, 100), f"Nivel: {data['level']}  ·  Likes: {data['likes']}", fill=accent_gold, font=font_med)
    draw.text((35, 130), f"Creada: {data['created_at']}", fill=text_muted, font=font_small)
    draw.text((35, 155), f"Antigüedad: {data['antiguedad']}", fill=accent_blue, font=font_small)

    # Panel Derecho: Rangos Competitivos
    draw.rounded_rectangle([400, 20, 780, 200], radius=10, fill=card_bg, outline=border_color, width=1)
    draw.text((415, 35), "🏆 RANGO COMPETITIVO", fill=accent_gold, font=font_title)
    
    # BR
    draw.text((415, 75), f"Battle Royale: {data['br_rank']}", fill=text_white, font=font_med)
    draw.text((415, 100), f"Puntos: {data['br_points']}", fill=text_muted, font=font_small)
    draw.rectangle([415, 120, 760, 126], fill=(50, 50, 60))
    draw.rectangle([415, 120, 650, 126], fill=accent_blue)
    
    # CS
    draw.text((415, 140), f"Clash Squad: {data['cs_rank']}", fill=text_white, font=font_med)
    draw.text((415, 165), f"Marcas: {data['cs_marks']}", fill=text_muted, font=font_small)
    draw.rectangle([415, 185, 760, 191], fill=(50, 50, 60))
    draw.rectangle([415, 185, 680, 191], fill=(46, 204, 113))

    # Panel Inferior: Equipamiento y Gremio
    draw.rounded_rectangle([20, 220, 780, 395], radius=10, fill=card_bg, outline=border_color, width=1)
    draw.text((35, 235), f"🛡️ Gremio: {data['guild_name']} (Nvl {data['guild_level']})  ·  Líder: {data['captain_name']}", fill=text_white, font=font_med)
    
    # Skins / Equipamiento
    draw.text((35, 275), f"🎮 Personaje: {data['character']}", fill=text_muted, font=font_med)
    draw.text((250, 275), f"🐾 Mascota: {data['pet']}", fill=text_muted, font=font_med)
    draw.text((450, 275), f"⚡ Habilidad: {data['ability']}", fill=text_muted, font=font_med)
    
    draw.text((35, 315), f"📝 Bio: \"{data['bio']}\"", fill=(200, 200, 220), font=font_small)
    draw.text((35, 355), f"Última conexión: {data['last_login']}  ·  Free Fire Lookup 24/7", fill=text_muted, font=font_small)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf
