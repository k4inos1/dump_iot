import firebase_admin
from firebase_admin import credentials, db
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.prompt import Prompt
from rich import box
import time
import sys
import glob
import os

# --- CONFIGURACIÓN ---
KEY_FILES = glob.glob("kainos-auditor-firebase-adminsdk-*.json")
if not KEY_FILES:
    print("❌ ERROR: No se encontró la llave JSON de Firebase.")
    sys.exit(1)

DB_URL = "https://kainos-auditor-default-rtdb.firebaseio.com/"

# Inicializar Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(KEY_FILES[0])
    firebase_admin.initialize_app(cred, {'databaseURL': DB_URL})

ref_root = db.reference('kainos_auditor')
console = Console()

def generate_table(data):
    """Genera la tabla de redes detectadas."""
    table = Table(title="📡 KAINOS AUDITOR - LIVE MONITOR", box=box.ROUNDED, expand=True)
    table.add_column("BSSID", style="cyan")
    table.add_column("SSID", style="white", header_style="bold")
    table.add_column("CH", justify="center", style="magenta")
    table.add_column("PWR", justify="center", style="green")
    table.add_column("SEC", style="yellow")
    table.add_column("LAST SEEN", style="dim")

    if data and 'networks' in data:
        # Ordenar por potencia (PWR) descendente
        nets = sorted(data['networks'].items(), key=lambda x: int(x[1].get('pwr', -100)), reverse=True)
        for bssid, info in nets:
            table.add_row(
                bssid,
                info.get('ssid', '<Oculto>'),
                info.get('ch', '?'),
                info.get('pwr', '?'),
                info.get('sec', '?'),
                info.get('last', '').split('T')[-1][:8]
            )
    return table

def send_command(cmd):
    ref_root.child('commands').set(cmd)
    console.print(f"[bold green]⚡ Comando enviado: {cmd}[/bold green]")
    time.sleep(1.5)

def main_loop():
    with Live(generate_table(None), refresh_per_second=1, screen=True) as live:
        while True:
            try:
                data = ref_root.get()
                live.update(generate_table(data))
            except KeyboardInterrupt:
                break
            except Exception:
                time.sleep(2)

    # Menú al salir con Ctrl+C
    while True:
        console.clear()
        console.print(Panel.fit("⚔️ KAINOS COMMAND CENTER", style="bold red"))
        console.print("1. 📡 Volver al Monitor")
        console.print("2. 💥 Lanzar Deauth (Ataque)")
        console.print("3. 🔄 Reiniciar Raspberry")
        console.print("4. 🚪 Salir")
        
        choice = Prompt.ask("Opción", choices=["1", "2", "3", "4"])
        
        if choice == "1": main_loop()
        elif choice == "2":
            target = Prompt.ask("BSSID Objetivo")
            channel = Prompt.ask("Canal")
            send_command(f"deauth|{target}|{channel}")
        elif choice == "3":
            if Prompt.ask("¿Seguro?", choices=["s", "n"]) == "s": send_command("reboot")
        elif choice == "4": sys.exit(0)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        pass