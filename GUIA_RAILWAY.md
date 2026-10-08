# ☁️ Guía Definitiva: Desplegar los 3 Bots a Railway.com (100% Online 24/7)

Con esta configuración, los **3 Bots** estarán activos las **24 horas del día, los 7 días de la semana** en los servidores de la nube de **[Railway.com](https://railway.com)**.
**¡Podrás apagar tu computadora por completo, desconectarte de internet o viajar, y los 3 bots seguirán 100% activos en Discord sin apagarse jamás!**

---

## 🤖 Los 3 Bots Incluidos en el Despliegue

| Bot | Función Principal | Canal en Discord |
| :--- | :--- | :--- |
| **Kevin 17** | Habla con voz real mexicana, responde a los usuarios y tira cotorreo con Rafa. Slash commands `/perfil`, `/cambiar_foto`, `/animacion`. | Canal de Voz `General` (`1542358479270846565`) + Canal Logs `#logskevin17` (`1557677467580366878`) |
| **RafaModzYT** | Habla con voz real, responde a micrófono y debate con Kevin. Slash commands de personalización. | Canal de Voz `General` (`1542358479270846565`) + Canal Logs `#logsrafamodzyt` (`1557677511058395196`) |
| **MusicBot 24/7** | DJ 24/7 con meta de 1,000,000 de horas, comando `/play` con filtro mundial de canciones en tiempo real, botones interactivos (Skip, Pausar, Cambiar, Quitar) y avatar Cyberpunk DJ. | Canal de Voz `🎵・Música` (`1557674216340586507`) |

---

## ⚡ ¿Por qué funciona en 1 solo servicio de Railway?
Hemos creado el supervisor maestro **`run_all_3_bots.py`**:
- Ejecuta los 3 bots simultáneamente dentro de un único contenedor Docker optimizado.
- **Auto-reinicio inteligente:** Si la conexión a Discord o YouTube parpadea, el supervisor reinicia el bot afectado automáticamente en 3 segundos.
- **Servidor de Monitoreo / Healthcheck HTTP:** Integra un servidor web en el puerto `8080` para que Railway marque el servicio en verde permanente (`ONLINE`) y nunca lo suspenda.

---

## 🚀 PASO A PASO PARA SUBIRLO A RAILWAY

### 1. Inicializar Git y Crear el Repositorio

Si aún no has subido el proyecto a tu GitHub:

Abre PowerShell en `d:\DiscordBotRAFA` y ejecuta:
```bash
git init
git add .
git commit -m "Sistema 24/7 con 3 bots para Railway"
```

Luego, en tu cuenta de GitHub (ej. `https://github.com/new`), crea un nuevo repositorio llamado por ejemplo `discord-bots-24-7` (puede ser Privado o Público) y corre:
```bash
git branch -M main
git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
git push -u origin main
```

---

### 2. Conectar Railway con tu Repositorio

1. Entra a **[railway.com](https://railway.com)** e inicia sesión con tu cuenta de GitHub.
2. Haz clic en el botón morado **`+ New Project`** (o **`Dashboard`** -> **`New`**).
3. Selecciona **`Deploy from GitHub repo`**.
4. Escoge tu repositorio recién creado (ej. `discord-bots-24-7`).
5. Haz clic en **`Deploy Now`**.

Railway detectará automáticamente el archivo `Dockerfile` y empezará a construir el contenedor con Python 3.12, FFmpeg y todas las dependencias de audio.

---

### 3. Configurar las Variables de Entorno en Railway (Opcional pero Recomendado)

Dentro de tu proyecto en Railway:
1. Haz clic en la tarjeta de tu servicio.
2. Ve a la pestaña **`Variables`**.
3. Haz clic en **`RAW Editor`** (arriba a la derecha de la pestaña) y pega este bloque:

```env
# Reemplaza con tus tokens de Discord Developer Portal:
BOT1_TOKEN=tu_token_de_kevin17
BOT1_ID=1557663276051996745
BOT1_NAME=Kevin 17
KEVIN_CONTROL_CHANNEL_ID=1557677467580366878

BOT2_TOKEN=tu_token_de_rafamodzyt
BOT2_ID=1557663530625278042
BOT2_NAME=RafaModzYT
RAFA_CONTROL_CHANNEL_ID=1557677511058395196

BOT3_TOKEN=tu_token_de_musicbot
BOT3_ID=1557681419873165403
BOT3_NAME=MusicBot 24/7
MUSIC_VOICE_CHANNEL_ID=1557674216340586507

BOT4_TOKEN=tu_token_de_freefire
BOT4_ID=1557688476818743306
BOT4_NAME=INFO CUENTA DE FREE FIRE
FF_CHANNEL_ID=1557688386683146270

GUILD_ID=1538269421020258304
VOICE_CHANNEL_ID=1542358479270846565

PORT=8080
```
4. Haz clic en **Save Changes**. Railway redeplegará automáticamente en unos segundos.

---

### 4. Apagar los Bots Locales de tu Computadora

Una vez que veas en Railway en la pestaña **`Deployments`** -> **`View Logs`** que los 3 bots están conectados exitosamente a Discord:
- Cierra cualquier terminal o proceso en tu PC.
- ¡Listo! Los bots ahora están viviendo 100% en Railway.
- Puedes apagar tu PC por completo. Tus 3 bots nunca se desconectarán de Discord.
