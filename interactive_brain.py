import random
import re

CHISTES = [
    "Había una vez un perro que se llamaba Pegamento, se cayó y se pegó... Jajajajaja.",
    "¿Qué le dice una impresora a otra? ¿Esa hoja es tuya o es impresión mía? Jajaja no manches.",
    "—Mamá, en la escuela me dicen interesado. — ¿Quiénes hijo? — ¡Dame 100 pesos y te digo! Jajajaja.",
    "¿Por qué los pájaros vuelan para el sur en invierno? ¡Porque caminando tardarían un montón! Jajaja.",
    "— Papá, ¿qué se siente tener un hijo tan guapo? — No sé mijo, pregúntale a tu abuelo. ¡Uff qué quemada!",
    "¿Qué hace una abeja en el gimnasio? ¡Zuuuumba! Jajajaja buenísimo.",
    "Iba caminando por la calle y vi a un señor vendiendo relojes. Le pregunté qué hora es y me dijo: La de comprarse uno... Qué manchado jajaja.",
    "¿Cómo maldice un pollito a otro pollito? ¡Caldito seas! Jajajaja clásico."
]

RESPUESTAS_SALUDO_KEVIN = [
    "¡Qué onda carnal! Aquí ando echando el coto en llamada con Rafa, ¿tú qué cuentas bro?",
    "¡Todo al tiro mi compa! Aquí jugando Free Fire y cotorreando un rato, ¿qué se te ofrece?",
    "¡Qué rollo bro! Al cien y pasadito, aquí platicando bien a gusto, ¿qué hay de nuevo?",
    "¡Qué onda viejo! Reportándome en vivo y en directo, ¿cómo te trata la vida?"
]

RESPUESTAS_SALUDO_RAFA = [
    "¡Qué onda hermano! Aquí streameando y platicando con Kevin, ¿cómo andas?",
    "¡Ese mi rey! Aquí reportándome, qué pasó viejo, ¿todo bien?",
    "¡Wenas bro! Al tiro como siempre echando el cotorreo, ¿qué onda?",
    "¡Qué tranza pariente! Aquí andamos al millón, ¿en qué te ayudamos o qué hacemos?"
]

RESPUESTAS_RANDOM_KEVIN = [
    "Jajaja Simón carnal, te la sabes de memoria.",
    "Así mero viejo, pura verdad lo que dices.",
    "No manches carnal, te mamaste con eso jajaja.",
    "A huevo mi bro, aquí andamos firmes para lo que sea.",
    "Tranqui viejo, pura buena vibra aquí en el canal.",
    "Jajajaja no inventes, me sacaste la risa compa."
]

RESPUESTAS_RANDOM_RAFA = [
    "Jajaja totalmente de acuerdo mi rey, no le fallas.",
    "Claro que sí hermano, aquí andamos echando plática 24/7.",
    "Jajajaja qué bárbaro bro, eso no me lo esperaba.",
    "Pura vibra perrona pariente, aquí seguimos al tiro.",
    "A huevo carnal, tú nomás dinos qué rollo y le damos."
]


def process_user_interaction(message_text: str, bot_targeted: str = "both"):
    raw_lower = message_text.lower().strip()

    if bot_targeted == "bot1":
        speaker = "Kevin 17"
        voice_key = "bot1"
    elif bot_targeted == "bot2":
        speaker = "RafaModzYT"
        voice_key = "bot2"
    else:
        if "kevin" in raw_lower or "17" in raw_lower:
            speaker = "Kevin 17"
            voice_key = "bot1"
        elif "rafa" in raw_lower or "modz" in raw_lower:
            speaker = "RafaModzYT"
            voice_key = "bot2"
        else:
            speaker = random.choice(["Kevin 17", "RafaModzYT"])
            voice_key = "bot1" if speaker == "Kevin 17" else "bot2"

    cleaned = raw_lower
    cleaned = re.sub(r"^(?:oye|ey|hola)\s+", "", cleaned)
    cleaned = re.sub(r"^(?:kevin\s*17|kevin|rafamodzyt|rafa)\s*", "", cleaned).strip()

    # 1. Soundboard / Efectos de sonido
    sound_triggers = {
        "balazo": ("balazo", "💥 ¡Soltando ráfaga de plomo! ¡Agáchense todos!"),
        "balazos": ("balazo", "💥 ¡Soltando ráfaga de plomo! ¡Agáchense todos!"),
        "disparos": ("balazo", "💥 ¡Puro fuego cruzado pariente!"),
        "fierro": ("fierro", "🤠 ¡Fierro pariente! ¡Puro pa' delante!"),
        "risas": ("risas", "😂 ¡Jajajaja soltando la carcajada!"),
        "risa": ("risas", "😂 ¡Jajajaja soltando la risa!"),
        "booyah": ("booyah", "🏆 ¡Booyah! ¡Victoria magistral para la escuadra!"),
        "nextel": ("nextel", "📻 *Prip-Prip* Cambio y fuera."),
        "radio": ("nextel", "📻 *Prip-Prip* Central en frecuencia.")
    }
    for trigger, (snd_name, snd_text) in sound_triggers.items():
        if trigger in cleaned:
            return {
                "speaker": speaker,
                "voice_key": voice_key,
                "text_reply": f"🔊 **[{speaker}]:** {snd_text}",
                "voice_reply": snd_text,
                "is_music": False,
                "music_query": None,
                "is_stop_music": False,
                "is_soundboard": True,
                "sound_name": snd_name,
                "is_tiradera": False
            }

    # 2. Modo Tiradera / Rimas / Pelea de compas
    if any(k in cleaned for k in ["peleen", "tiradera", "tirense rimas", "rimas", "pelea", "tirate una rima"]):
        return {
            "speaker": speaker,
            "voice_key": voice_key,
            "text_reply": f"🥊 **[{speaker}]:** ¡Se armó la tiradera en vivo! Escúchanos en la llamada que nos vamos a dar con todo.",
            "voice_reply": "¡Se armó el desmadre! A ver Rafa, ponte trucha que te voy a tirar tus verdades.",
            "is_music": False,
            "music_query": None,
            "is_stop_music": False,
            "is_soundboard": False,
            "sound_name": None,
            "is_tiradera": True
        }

    # 3. Detener música
    if any(k in cleaned for k in ["quita la musica", "para la musica", "apaga la musica", "stop musica", "silencio", "pausa la musica", "para", "stop"]):
        frase = "¡Listo carnal, música apagada! Seguimos con la plática."
        return {
            "speaker": speaker,
            "voice_key": voice_key,
            "text_reply": f"⏹️ **[{speaker}]:** {frase}",
            "voice_reply": frase,
            "is_music": False,
            "music_query": None,
            "is_stop_music": True,
            "is_soundboard": False,
            "sound_name": None,
            "is_tiradera": False
        }

    # 4. Peticiones de Música
    if cleaned == "pon musica" or cleaned == "ponte musica" or cleaned == "pon una rola" or cleaned == "pon musica random" or "pon musica" in cleaned or "ponte una" in cleaned or "pon " in cleaned:
        if "makabelico" in cleaned or "comando" in cleaned:
            query = "makabelico comando exclusivo"
            frases_makabelico = [
                "¡Fierro pariente! Ahí te va una rola pesada del Makabelico, ¡súbele al volumen!",
                "¡Simón compa, Makabelico al tiro! Póngale play que retumbe la bocina.",
                "¡A huevo viejo, esa del Makabelico está perrona! Ahí te la suelto."
            ]
            chosen_phrase = random.choice(frases_makabelico)

        elif cleaned in ["pon musica", "ponte musica", "pon una rola", "pon musica random", "pon rola"] or "random" in cleaned or "aleatoria" in cleaned:
            query = "random"
            frases_random = [
                "¡Simón carnal! Ahí te va una rola bien perrona, ¡súbele al volumen!",
                "¡Venga compadre, soltando rolita para la banda! ¡A disfrutar!",
                "¡Sale viejo, música activada! Que se prenda el cotorreo."
            ]
            chosen_phrase = random.choice(frases_random)

        else:
            m = re.search(r"(?:pon musica de|pon musica|pon una de|pon|reproduce)\s+(.+)", cleaned)
            if m:
                query = m.group(1).strip()
            else:
                query = "random"

            if query == "musica" or query == "":
                query = "random"
                chosen_phrase = "¡Simón carnal! Ahí te pongo una rola buena, ¡súbele al volumen!"
            else:
                chosen_phrase = f"¡Claro que sí carnal! Ahí te pongo {query}. ¡Que retumbe!"

        return {
            "speaker": speaker,
            "voice_key": voice_key,
            "text_reply": f"🎶 **[{speaker}]:** {chosen_phrase}",
            "voice_reply": chosen_phrase,
            "is_music": True,
            "music_query": query,
            "is_stop_music": False,
            "is_soundboard": False,
            "sound_name": None,
            "is_tiradera": False
        }

    # 5. Petición de Chiste
    if any(k in cleaned for k in ["chiste", "cuentate un chiste", "dime un chiste", "broma", "hazme reir"]):
        chiste = random.choice(CHISTES)
        intro = "A ver carnal, ahí te va este chiste:" if speaker == "Kevin 17" else "Jajaja escucha este chiste hermano:"
        return {
            "speaker": speaker,
            "voice_key": voice_key,
            "text_reply": f"😂 **[{speaker}]:** {intro}\n> *{chiste}*",
            "voice_reply": f"{intro} {chiste}",
            "is_music": False,
            "music_query": None,
            "is_stop_music": False,
            "is_soundboard": False,
            "sound_name": None,
            "is_tiradera": False
        }

    # 6. Saludos
    if any(k in cleaned for k in ["hola", "que onda", "que tal", "como andas", "como estas", "que haces", "que tranza", "que rollo", "buenas"]) or cleaned == "":
        saludos = RESPUESTAS_SALUDO_KEVIN if speaker == "Kevin 17" else RESPUESTAS_SALUDO_RAFA
        frase = random.choice(saludos)
        return {
            "speaker": speaker,
            "voice_key": voice_key,
            "text_reply": f"👋 **[{speaker}]:** {frase}",
            "voice_reply": frase,
            "is_music": False,
            "music_query": None,
            "is_stop_music": False,
            "is_soundboard": False,
            "sound_name": None,
            "is_tiradera": False
        }

    # 7. Respuestas cotidianas
    respuestas = RESPUESTAS_RANDOM_KEVIN if speaker == "Kevin 17" else RESPUESTAS_RANDOM_RAFA
    frase = random.choice(respuestas)
    return {
        "speaker": speaker,
        "voice_key": voice_key,
        "text_reply": f"💬 **[{speaker}]:** {frase}",
        "voice_reply": frase,
        "is_music": False,
        "music_query": None,
        "is_stop_music": False,
        "is_soundboard": False,
        "sound_name": None,
        "is_tiradera": False
    }
