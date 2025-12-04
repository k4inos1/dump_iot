import os
import subprocess
import time
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich import print

console = Console()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_banner():
    clear_screen()
    console.print(Panel.fit(
        "[bold green]KAINOS AUDITOR SYSTEM[/bold green]\n"
        "[cyan]Raspberry Pi 3B+ Control Center[/cyan]",
        border_style="green"
    ))

def run_script(script_name, args=""):
    """Ejecuta un script .sh o comando"""
    console.print(f"\n[bold yellow]>> Ejecutando {script_name}...[/bold yellow]")
    
    # Detectar si es Windows (para pruebas) o Linux
    if os.name == 'nt':
        console.print("[dim]Simulando ejecución en Windows...[/dim]")
        time.sleep(1)
        console.print("[bold green]Comando finalizado (Simulación)[/bold green]")
        input("\nPresiona ENTER para continuar...")
        return

    try:
        # En Linux/RPi usamos sudo
        cmd = f"sudo ./{script_name} {args}"
        if script_name.endswith(".py"):
            cmd = f"python3 {script_name} {args}"
            
        os.system(cmd)
    except Exception as e:
        console.print(f"[bold red]ERROR: {e}[/bold red]")
    
    input("\nPresiona ENTER para continuar...")

def menu_monitor_mode():
    run_script("setup_monitor.sh")

def menu_scan():
    console.print("\n[bold cyan]INICIANDO ESCANEO...[/bold cyan]")
    console.print("Presiona [bold red]CTRL+C[/bold red] para detener el escaneo cuando quieras.")
    time.sleep(2)
    run_script("scan_networks.sh")

def menu_deauth():
    target = Prompt.ask("\n[bold red]Introduce el BSSID (MAC) del objetivo[/bold red]")
    if not target:
        return
    
    channel = Prompt.ask("[bold cyan]Canal (Opcional, ENTER para saltar)[/bold cyan]")
    
    args = f"{target} {channel}".strip()
    run_script("deauth_test.sh", args)

def menu_firebase():
    run_script("auditor.py")

def main_menu():
    while True:
        show_banner()
        
        table = Table(show_header=False, box=None)
        table.add_row("[bold green]1.[/bold green] 📡 Activar Modo Monitor")
        table.add_row("[bold green]2.[/bold green] 🔍 Escanear Redes (Airodump)")
        table.add_row("[bold green]3.[/bold green] 😈 Ataque Deauth (Desconexión)")
        table.add_row("[bold magenta]4.[/bold magenta] 📡 Rastreador (Probe Requests)")
        table.add_row("[bold yellow]5.[/bold yellow] 🛡️ Escáner de Vulnerabilidades")
        table.add_row("[bold red]6.[/bold red] ☠️ Bettercap (MITM)")
        table.add_row("[bold blue]7.[/bold blue] ☁️  Sincronizar con Firebase")
        table.add_row("[bold red]0.[/bold red] 🚪 Salir")
        
        console.print(table)
        
        choice = Prompt.ask("\n[bold cyan]Selecciona una opción[/bold cyan]", choices=["1", "2", "3", "4", "5", "6", "7", "0"])
        
        if choice == "1":
            menu_monitor_mode()
        elif choice == "2":
            menu_scan()
        elif choice == "3":
            menu_deauth()
        elif choice == "4":
            run_script("tracker.py")
        elif choice == "5":
            run_script("vuln_scan.sh")
        elif choice == "6":
            run_script("bettercap") # Bettercap es un binario, no un script local
        elif choice == "7":
            menu_firebase()
        elif choice == "0":
            console.print("[bold green]Saliendo... ¡Happy Hacking![/bold green]")
            break

if __name__ == "__main__":
    main_menu()
