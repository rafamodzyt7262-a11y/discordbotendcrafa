import random

# Voces recomendadas para cada bot:
# Bot 1 (Kevin 17): 'es-MX-JorgeNeural' (Voz masculina mexicana natural)
# Bot 2 (RafaModzYT): 'es-MX-DaliaNeural' o 'es-ES-AlvaroNeural' o 'es-CO-GonzaloNeural'
VOICE_BOT1 = "es-MX-JorgeNeural"
VOICE_BOT2 = "es-ES-AlvaroNeural"  # Voz distinta para que contrasten claramente al hablar

# Temas de conversación de la vida real con intercambios realistas y fluidos
CONVERSATION_TOPICS = [
    # Tema 1: Comida y antojos
    [
        ("bot1", "Oye Rafa, no tienes idea del hambre que traigo hoy. ¿Tú qué comiste?"),
        ("bot2", "Hermano, me eché unos tacos de suadero que estaban para chuparse los dedos con harta salsa verde."),
        ("bot1", "Uff, ya me antojaste bien gacho. Yo creo que ahorita me pido una hamburguesa o algo bien grasoso, la dieta empieza el lunes."),
        ("bot2", "Jajaja, el clásico lunes que nunca llega. Pero date el gusto, la vida es una sola y hay que comer rico."),
        ("bot1", "Totalmente de acuerdo contigo, no hay mejor felicidad que comer sabroso.")
    ],
    # Tema 2: El despertador y las mañanas pesadas
    [
        ("bot2", "Kevin, te juro que hoy apagué como cinco alarmas seguidas antes de poder levantarme de la cama."),
        ("bot1", "No me digas eso, a mí me pasó exactamente lo mismo. Esos cinco minutitos extra son la trampa más grande del mundo."),
        ("bot2", "¡Exacto! Pones la alarma a las siete, cierras los ojos un segundo y de repente ya son las ocho y cuarto."),
        ("bot1", "Y sales corriendo como loco por toda la casa buscando las llaves y con un calcetín puesto nada más."),
        ("bot2", "Jajaja, literal mi rutina de todas las semanas. Menos mal que un buen café siempre salva el día.")
    ],
    # Tema 3: Videojuegos y partidas intensas
    [
        ("bot1", "Oye Rafa, ¿jugaste algo anoche o te fuiste a dormir temprano?"),
        ("bot2", "Me quedé jugando unas partidas hasta las dos de la mañana, pero me tocó puro compañero que parecía que jugaba con los ojos vendados."),
        ("bot1", "¡Qué coraje da cuando te toca gente así! A mí el otro día me dio un lagazo justo en el último segundo de la partida y perdí."),
        ("bot2", "No inventes, yo cuando me pasa eso casi tiro el control por la ventana, te da una rabia instantánea."),
        ("bot1", "Jajaja sí, pero a los cinco minutos ya estás dándole a 'buscar otra partida' otra vez, no tenemos remedio."),
        ("bot2", "Es una adicción sana, mi hermano. Hay que echar unas retas juntos más al rato a ver si ganamos algo.")
    ],
    # Tema 4: El clima y el calor/frío
    [
        ("bot2", "Oye Kevin, ¿qué onda con el clima de estos días? Afuera parece un horno prendido a máxima potencia."),
        ("bot1", "Ni me lo recuerdes, salí diez minutos a la tienda y sentí que me derretía en la banqueta."),
        ("bot2", "La neta yo soy cien por ciento fan del frío. En el frío te tapas con una cobija y listo, pero con calor no sabes ni qué hacer."),
        ("bot1", "Tienes razón, con el calor te bañas y a los tres minutos ya estás sudando otra vez. Que llegue el invierno ya por favor."),
        ("bot2", "Totalmente. Un chocolatito caliente y clima nublado, ese sí es el verdadero paraíso.")
    ],
    # Tema 5: Anécdotas graciosas de la calle
    [
        ("bot1", "Rafa, no vas a creer el oso que hice ayer en la calle cuando venía caminando."),
        ("bot2", "A ver, cuéntame, suéltalo que me encanta el chisme."),
        ("bot1", "Iba viendo el teléfono bien distraído, pisé mal la orilla de la banqueta y casi me voy de boca contra un poste."),
        ("bot2", "Jajajaja, ¿y había gente viéndote o zafaste sin público?"),
        ("bot1", "Había como cuatro señoras en la parada del camión. Lo peor es que me hice el que estaba trotando para disimular."),
        ("bot2", "Jajajaja la típica disimulada de empezar a trotar. Todos hemos estado ahí alguna vez, carnal, no te preocupes.")
    ],
    # Tema 6: Series y películas
    [
        ("bot2", "Kevin, ¿has visto alguna película o serie buena últimamente? Es que ya me acabé todo lo que tenía pendiente."),
        ("bot1", "Fíjate que empecé a ver una serie de suspenso recomendada en redes y me quedé tan picado que me eché seis capítulos en una sola sentada."),
        ("bot2", "Eso me pasaba a mí. Lo malo es cuando la serie termina con un final abierto y la siguiente temporada sale hasta dentro de dos años."),
        ("bot1", "¡Uy sí! Te dejan con la intriga al tope y luego para cuando sale la otra temporada ya se te olvidó de qué trataba todo."),
        ("bot2", "Por eso a veces prefiero ver películas completas de dos horas y me ahorro el estrés existencial.")
    ],
    # Tema 7: El gimnasio y la vida fit
    [
        ("bot1", "Hermano, estaba pensando en inscribirme al gimnasio el próximo mes, a ver si ahora sí me pongo en forma."),
        ("bot2", "¿Y vas a ir de verdad o nada más vas a pagar la mensualidad para hacerle donaciones a los dueños?"),
        ("bot1", "Oye, respeta, que esta vez sí es en serio. Aunque el dolor de cuerpo al segundo día de pierna es inhumano."),
        ("bot2", "Uff, bajar las escaleras al día siguiente de hacer pierna parece deporte extremo. Pero ánimo, la constancia lo es todo."),
        ("bot1", "Eso sí, con que vaya tres veces por semana me doy por bien servido.")
    ],
    # Tema 8: Mascotas y cosas curiosas
    [
        ("bot2", "Kevin, estaba viendo videos de perros y gatos en internet y la verdad los animales hacen unas cosas bien chistosas."),
        ("bot1", "Totalmente. El gato de mi vecino se pasa horas enteras viendo la pared fijamente como si estuviera viendo fantasmas."),
        ("bot2", "Jajaja, los gatos tienen una vibra bien misteriosa. En cambio los perros ven una hoja caer del árbol y se emocionan como si fuera fiesta."),
        ("bot1", "Es verdad, la felicidad pura que transmiten los perros cuando llegas a la casa no se compara con nada."),
        ("bot2", "Son lo mejor que hay. Ojalá todos los días fueran tan tranquilos como un domingo con una mascota al lado.")
    ],
    # Tema 9: Recuerdos de la infancia y tecnología vieja
    [
        ("bot1", "Rafa, ¿te acuerdas cuando éramos niños y para escuchar música tenías que esperar a que saliera en la radio para grabarla?"),
        ("bot2", "¡Sí! Y si el locutor hablaba en medio de la canción te echaba a perder toda la grabación en el casete."),
        ("bot1", "Qué tiempos aquellos, o cuando el internet de la casa sonaba como nave espacial y si llamaban por teléfono te cortaban la conexión."),
        ("bot2", "No inventes, qué recuerdos. Ahora la tecnología va tan rápido que uno ya se siente viejito recordando esas cosas."),
        ("bot1", "Jajaja sí, pero la verdad se disfrutaba un montón. Todo era más simple en esa época.")
    ],
    # Tema 10: Fin de semana y planes
    [
        ("bot2", "Kevin, ¿qué planes tienes para este fin de semana? ¿Vas a salir de fiesta o relax total?"),
        ("bot1", "La verdad traigo una flojera acumulada de toda la semana que mi único plan es quedarme en cama viendo películas y comiendo palomitas."),
        ("bot2", "Uff, ese es el mejor plan de todos. El cuerpo necesita recargar pilas de vez en cuando sin salir a ningún lado."),
        ("bot1", "¿Y tú qué vas a hacer, Rafa? ¿Vas a salir con amigos o también en modo oso invernando?"),
        ("bot2", "Igual que tú, carnal. Pijama, comida chatarra, una buena peli y cero preocupaciones por dos días completos."),
        ("bot1", "Esa es la actitud, mi hermano. Que empiece el fin de semana ya.")
    ],
    # Tema 11: Café y desvelo
    [
        ("bot1", "Oye Rafa, ¿tú cuántas tazas de café te tomas al día? Yo ya perdí la cuenta hoy."),
        ("bot2", "Normalmente dos, pero si la noche anterior me desvelé, fácil me echo tres o cuatro para revivir."),
        ("bot1", "Es que el café por la mañana no es una bebida, es el combustible que nos mantiene con vida en este planeta."),
        ("bot2", "Amén a eso, Kevin. Sin café temprano no respondo de mis acciones hasta después de mediodía.")
    ],
    # Tema 12: Música favorita y gustos culposos
    [
        ("bot2", "Oye Kevin, ¿qué música andas escuchando últimamente? Pásame alguna recomendación buena."),
        ("bot1", "De todo un poco, la verdad. Desde rock clásico hasta rolas de esas viejitas que te sabes todas las letras sin querer."),
        ("bot2", "Todos tenemos nuestros gustos culposos, esas canciones que cantas a todo pulmón cuando estás solo en la regadera."),
        ("bot1", "Jajajaja, total. Esas son las mejores porque te sacan toda la energía acumulada del día."),
        ("bot2", "La música alegra el alma, hermano, no hay duda de eso.")
    ]
]

# Frases dinámicas de transición entre temas
TRANSITIONS = [
    "Oye Rafa, y cambiando un poquito de tema...",
    "Hermano, por cierto, me acabo de acordar de algo...",
    "Oye, antes de que se me olvide, te quería preguntar algo...",
    "Kevin, fíjate que estaba pensando en otra cosa hace rato...",
    "Oye, sabes qué me pasó por la mente recién...",
    "Hablando de todo un poco, Rafa...",
    "Oye carnal, qué opinas de esto...",
]

class ConversationManager:
    def __init__(self):
        self.topics = list(CONVERSATION_TOPICS)
        random.shuffle(self.topics)
        self.topic_index = 0
        self.step_index = 0
        self.current_topic = self.topics[self.topic_index]
        self.is_paused = False

    def get_next_line(self):
        """Retorna (bot_who_speaks, text_to_say, is_topic_start)"""
        if self.is_paused:
            return None, None, False

        # Si terminó el tema actual, pasar al siguiente tema
        if self.step_index >= len(self.current_topic):
            self.topic_index = (self.topic_index + 1) % len(self.topics)
            if self.topic_index == 0:
                random.shuffle(self.topics)
            self.current_topic = self.topics[self.topic_index]
            self.step_index = 0

        speaker, text = self.current_topic[self.step_index]
        self.step_index += 1
        return speaker, text, (self.step_index == 1)

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False
