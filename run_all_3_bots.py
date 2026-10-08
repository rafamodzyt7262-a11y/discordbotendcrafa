import os
import sys
import time
import signal
import threading
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Puerto para Railway / Cloud healthcheck
PORT = int(os.getenv("PORT", "8080"))

start_time = time.time()
running = True

# Estado de los procesos
processes = {
    "voice_bots": None,  # run_both_unified.py (Kevin 17 & RafaModzYT)
    "music_bot": None,   # bot3/bot.py (MusicBot 24/7)
    "ff_bot": None       # bot4/bot.py (INFO CUENTA DE FREE FIRE)
}


class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        uptime_seconds = int(time.time() - start_time)
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{hours}h {minutes}m {seconds}s"

        p1_alive = processes["voice_bots"] is not None and processes["voice_bots"].poll() is None
        p2_alive = processes["music_bot"] is not None and processes["music_bot"].poll() is None
        p3_alive = processes["ff_bot"] is not None and processes["ff_bot"].poll() is None

        data = {
            "status": "ONLINE" if (p1_alive and p2_alive and p3_alive) else "PARTIAL",
            "uptime": uptime_str,
            "supervisor": "Master 24/7",
            "bots": {
                "kevin17": "ONLINE" if p1_alive else "OFFLINE",
                "rafamodzyt": "ONLINE" if p1_alive else "OFFLINE",
                "musicbot247": "ONLINE" if p2_alive else "OFFLINE",
                "freefirebot": "ONLINE" if p3_alive else "OFFLINE"
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode("utf-8"))

    def log_message(self, format, *args):
        # Silenciar logs HTTP constantes de Railway
        return


def run_health_server():
    try:
        server = HTTPServer(("0.0.0.0", PORT), HealthCheckHandler)
        print(f"[SUPERVISOR] 🌐 Servidor de monitoreo y Healthcheck activo en http://0.0.0.0:{PORT}")
        server.serve_forever()
    except Exception as e:
        print(f"[SUPERVISOR] ⚠️ No se pudo iniciar el servidor web HTTP en puerto {PORT}: {e}")


def stream_logs(pipe, prefix):
    try:
        for line in iter(pipe.readline, ''):
            if not line:
                break
            line_str = line.strip()
            if line_str:
                print(f"{prefix} {line_str}", flush=True)
    except Exception:
        pass


def launch_process(script_args, name, prefix):
    print(f"[SUPERVISOR] 🚀 Iniciando subproceso: {name} ({' '.join(script_args)})...", flush=True)
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    proc = subprocess.Popen(
        script_args,
        cwd=str(BASE_DIR),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    t = threading.Thread(target=stream_logs, args=(proc.stdout, prefix), daemon=True)
    t.start()
    return proc


def shutdown_handler(signum, frame):
    global running
    print(f"\n[SUPERVISOR] 🛑 Señal de apagado recibida ({signum}). Terminando procesos ordenadamente...", flush=True)
    running = False
    for name, proc in processes.items():
        if proc and proc.poll() is None:
            print(f"[SUPERVISOR] Cerrando {name}...", flush=True)
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
    print("[SUPERVISOR] ✅ Todos los bots han sido detenidos.", flush=True)
    sys.exit(0)


def main():
    global running

    print("=" * 70, flush=True)
    print("      🚀 INICIANDO SUPERVISOR MASTER 24/7 - BOTS DISCORD", flush=True)
    print("      1. Kevin 17          (Canal Voz General + IA + Logs)", flush=True)
    print("      2. RafaModzYT        (Canal Voz General + IA + Logs)", flush=True)
    print("      3. MusicBot 24/7     (Canal Voz Música + /play + Controles)", flush=True)
    print("      4. Free Fire Bot     (Canal #uid-free-fire + /id)", flush=True)
    print("      PLATAFORMA: Railway.com / Docker Cloud 24/7", flush=True)
    print("=" * 70, flush=True)

    # Registrar señales de parada (Docker / Railway SIGTERM)
    signal.signal(signal.SIGINT, shutdown_handler)
    try:
        signal.signal(signal.SIGTERM, shutdown_handler)
    except Exception:
        pass

    # Iniciar servidor web de monitoreo en segundo plano
    http_thread = threading.Thread(target=run_health_server, daemon=True)
    http_thread.start()

    # Comandos para cada proceso
    python_cmd = sys.executable
    cmd_voice = [python_cmd, str(BASE_DIR / "run_both_unified.py")]
    cmd_music = [python_cmd, str(BASE_DIR / "bot3" / "bot.py")]
    cmd_ff = [python_cmd, str(BASE_DIR / "bot4" / "bot.py")]

    # Iniciar los procesos
    processes["voice_bots"] = launch_process(cmd_voice, "Kevin 17 & RafaModzYT", "[VOICE-DUO]")
    processes["music_bot"] = launch_process(cmd_music, "MusicBot 24/7", "[MUSIC-BOT]")
    processes["ff_bot"] = launch_process(cmd_ff, "INFO CUENTA DE FREE FIRE", "[FF-BOT]")

    # Bucle de supervisión y autoreconexión infinita
    while running:
        try:
            time.sleep(3)

            # Verificar Proceso 1 (Kevin 17 & RafaModzYT)
            p1 = processes["voice_bots"]
            if p1 is not None and p1.poll() is not None:
                exit_code = p1.poll()
                print(f"[SUPERVISOR] ⚠️ [VOICE-DUO] terminó con código {exit_code}. Reiniciando en 3s...", flush=True)
                time.sleep(3)
                processes["voice_bots"] = launch_process(cmd_voice, "Kevin 17 & RafaModzYT", "[VOICE-DUO]")

            # Verificar Proceso 2 (MusicBot 24/7)
            p2 = processes["music_bot"]
            if p2 is not None and p2.poll() is not None:
                exit_code = p2.poll()
                print(f"[SUPERVISOR] ⚠️ [MUSIC-BOT] terminó con código {exit_code}. Reiniciando en 3s...", flush=True)
                time.sleep(3)
                processes["music_bot"] = launch_process(cmd_music, "MusicBot 24/7", "[MUSIC-BOT]")

            # Verificar Proceso 3 (Free Fire Bot)
            p3 = processes["ff_bot"]
            if p3 is not None and p3.poll() is not None:
                exit_code = p3.poll()
                print(f"[SUPERVISOR] ⚠️ [FF-BOT] terminó con código {exit_code}. Reiniciando en 3s...", flush=True)
                time.sleep(3)
                processes["ff_bot"] = launch_process(cmd_ff, "INFO CUENTA DE FREE FIRE", "[FF-BOT]")

        except KeyboardInterrupt:
            shutdown_handler(signal.SIGINT, None)
        except Exception as e:
            print(f"[SUPERVISOR] Error en bucle de supervisión: {e}", flush=True)
            time.sleep(5)


if __name__ == "__main__":
    main()
