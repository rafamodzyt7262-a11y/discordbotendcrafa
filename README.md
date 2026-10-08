# 🎙️ Bots de Discord 24/7 con Escucha de Voz en Vivo + Música

Este proyecto contiene 2 bots de Discord independientes configurados para permanecer en un canal de voz **24/7 sin salir jamás**, **platican activamente entre ellos** y además **escuchan tu micrófono en vivo**: cuando hablas en la llamada, los bots te escuchan y te responden con su voz: *"Dime, ¿qué quieres que ponga?"*.

---

## 📌 Datos de los Bots

| Bot | Nombre | ID de Aplicación | Voz Neuronal | Presencia / Perfil |
| :--- | :--- | :--- | :--- | :--- |
| **Bot 1** | **Kevin 17** | `1557663276051996745` | `es-MX-JorgeNeural` (Mexicano) | `Jugando a WAKURABA CHEATS` (DND 🔴) |
| **Bot 2** | **RafaModzYT** | `1557663530625278042` | `es-ES-AlvaroNeural` (Español/Latino) | `Transmitiendo Visual Studio Code` (LIVE 🟣) |

- **Servidor ID:** `1538269421020258304`
- **Canal de Voz ID:** `1542358479270846565` (Canal "General")

---

## 🎧 ¡NUEVO! Detección de Tu Voz en Vivo en la Llamada

1. **Hablas por tu micrófono en Discord:**  
   Cuando abres tu micrófono en el canal de voz y empiezas a hablar, el detector de voz (`VoiceRecvClient` + `SpeakingState`) te escucha.
2. **El bot te responde con su voz:**  
   El bot pausa inmediatamente la plática de fondo y te responde hablando en la llamada:  
   🗣️ *"Dime, ¿qué quieres que ponga?"*
3. **Pide tu música:**  
   Puedes pedirle en voz o escribiendo en el chat:  
   - `oye kevin 17 pon musica de makabelico`
   - `oye rafamodzyt pon musica random`
   - `oye kevin 17 pon [canción]`
   - `oye username cuéntate un chiste`
   - `oye username quita la musica`
4. **Reproducción instantánea:**  
   El bot confirmado reproduce la canción en alta fidelidad en el canal de voz.

---

## ☁️ Despliegue en Railway.com (24/7 en la Nube)

Para mantenerlos activos las 24 horas aunque apagues tu PC:
👉 **Consulta [GUIA_RAILWAY.md](file:///d:/DiscordBotRAFA/GUIA_RAILWAY.md)**

Incluye:
- `Dockerfile` con Python 3.12, FFmpeg y librerías de recepción de audio.
- `railway.json` con auto-recuperación ante cortes.
- `run_both_unified.py` para correr ambos en un solo contenedor económico.

---

## 💬 Comandos por Nombre de Usuario en Chat

- `oye kevin 17 pon musica` : Solo responde Kevin 17 y pone música.
- `oye rafamodzyt pon musica` : Solo responde RafaModzYT y pone música.
- `oye kevin 17 pon musica de makabelico` : Pone rolas del Makabelico.
- `oye username cuéntate un chiste` : Te cuenta un chiste en chat y en voz.
- `oye username quita la musica` : Apaga la música y siguen platicando.
