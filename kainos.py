import firebase_admin
from firebase_admin import credentials, db
import subprocess
import time
import os
import glob
import sys
import signal
from datetime import datetime

# --- CONFIGURACIÓN ---
# Busca la llave JSON automáticamente
KEY_FILES = glob.glob("kainos-auditor-firebase-adminsdk-*.json")
CONFIG = {
    "db_url": "https://kainos-auditor-default-rtdb.firebaseio.com/",
    "interface": "wlan1",
    "csv_prefix": "dump_kainos",
    "scan_interval": 5
}

def install_system():
    """Instala dependencias y configura el servicio systemd."""
    print("🚀 INSTALANDO KAINOS AGENT (Raspberry Pi)...")
    
    # 1. Instalar paquetes del sistema
    print("[*] Instalando aircrack-ng y python3-pip...")
    subprocess.run("sudo apt-get update && sudo apt-get install -y aircrack-ng python3-pip libpcap-dev", shell=True)
    
    # 2. Instalar librerías Python
    print("[*] Instalando firebase-admin...")
    subprocess.run("sudo pip3 install firebase-admin --break-system-packages", shell=True)
    
    # 3. Crear servicio systemd
    print("[*] Creando servicio 'kainos.service'...")
    script_path = os.path.abspath(__file__)
    working_dir = os.path.dirname(script_path)
    
    service_content = f"""[Unit]
Description=Kainos Auditor Agent
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory={working_dir}
ExecStart=/usr/bin/python3 {script_path}
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""
    with open("/tmp/kainos.service", "w") as f:
        f.write(service_content)
        
    subprocess.run("sudo mv /tmp/kainos.service /etc/systemd/system/kainos.service", shell=True)
    subprocess.run("sudo systemctl daemon-reload", shell=True)
    subprocess.run("sudo systemctl enable kainos.service", shell=True)
    subprocess.run("sudo systemctl restart kainos.service", shell=True)
    
    print("\n✅ INSTALACIÓN COMPLETADA.")
    print("El agente se está ejecutando en segundo plano.")
    print("Usa 'sudo systemctl status kainos.service' para ver el estado.")
    sys.exit(0)

class KainosAgent:
    def __init__(self):
        if not KEY_FILES:
            print("❌ ERROR: Falta llave JSON de Firebase (kainos-auditor-firebase-adminsdk-*.json).")
            sys.exit(1)
            
        # Conexión a Firebase
        cred = credentials.Certificate(KEY_FILES[0])
        firebase_admin.initialize_app(cred, {'databaseURL': CONFIG["db_url"]})
        self.ref_root = db.reference('kainos_auditor')
        
        self.interface = CONFIG["interface"]
        self.process = None
        self.running = True

    def setup_interface(self):
        """Pone la interfaz en modo monitor."""
        print(f"[*] Configurando {self.interface} en modo monitor...")
        subprocess.run(["sudo", "airmon-ng", "check", "kill"], stdout=subprocess.DEVNULL)
        subprocess.run(["sudo", "airmon-ng", "start", self.interface], stdout=subprocess.DEVNULL)
        
        # A veces cambia de nombre a wlan1mon
        if os.path.exists("/sys/class/net/wlan1mon"): 
            self.interface = "wlan1mon"
        print(f"✅ Interfaz lista: {self.interface}")

    def run_airodump(self):
        """Inicia airodump-ng."""
        # Borrar CSVs viejos
        for f in glob.glob(f"{CONFIG['csv_prefix']}*"):
            try: os.remove(f)
            except: pass

        cmd = ["sudo", "airodump-ng", "--write", CONFIG["csv_prefix"], "--output-format", "csv", 
               "--write-interval", str(CONFIG["scan_interval"]), self.interface]
        
        self.process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def parse_csv(self):
        """Lee el CSV generado por airodump."""
        csv_file = f"{CONFIG['csv_prefix']}-01.csv"
        if not os.path.exists(csv_file): return None
        
        data = {"networks": {}, "clients": {}}
        try:
            with open(csv_file, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
                
            section = "networks"
            for line in lines:
                line = line.strip()
                if not line or line.startswith('BSSID, First'): continue
                if line.startswith('Station MAC'): section = "clients"; continue
                
                parts = [p.strip() for p in line.split(',')]
                
                # Parsear Redes
                if section == "networks" and len(parts) >= 14 and len(parts[0]) == 17:
                    bssid = parts[0]
                    ssid = parts[13]
                    channel = parts[3]
                    pwr = parts[8]
                    sec = f"{parts[5]}/{parts[6]}".strip()
                    
                    data["networks"][bssid] = {
                        "ssid": ssid, 
                        "ch": channel, 
                        "pwr": pwr, 
                        "sec": sec, 
                        "last": datetime.now().isoformat()
                    }
                
                # Parsear Clientes
                elif section == "clients" and len(parts) >= 6 and len(parts[0]) == 17:
                    mac = parts[0]
                    bssid = parts[5]
                    pwr = parts[3]
                    
                    data["clients"][mac] = {
                        "bssid": bssid, 
                        "pwr": pwr, 
                        "last": datetime.now().isoformat()
                    }
            return data
        except Exception as e:
            print(f"Error parsing CSV: {e}")
            return None

    def loop(self):
        print("📡 Agente activo y sincronizando...")
        while self.running:
            # 1. Leer y Subir Datos
            data = self.parse_csv()
            if data:
                # Heartbeat
                self.ref_root.child('status').set({
                    "online": True, 
                    "updated": datetime.now().isoformat(),
                    "nets": len(data['networks']), 
                    "clients": len(data['clients'])
                })
                
                # Actualizar listas
                if data['networks']: self.ref_root.child('networks').update(data['networks'])
                if data['clients']: self.ref_root.child('clients').update(data['clients'])
            
            # 2. Leer Comandos
            cmd = self.ref_root.child('commands').get()
            if cmd:
                print(f"⚡ Comando recibido: {cmd}")
                self.ref_root.child('commands').set(None) # Borrar comando
                
                if cmd == "reboot": 
                    os.system("sudo reboot")
                elif cmd.startswith("deauth"):
                    # Formato: deauth|BSSID|CHANNEL
                    try:
                        _, target, ch = cmd.split("|")
                        # Detener airodump temporalmente
                        if self.process: self.process.terminate()
                        
                        # Cambiar canal
                        subprocess.run(["sudo", "iwconfig", self.interface, "channel", ch])
                        # Atacar
                        subprocess.run(["sudo", "aireplay-ng", "--deauth", "25", "-a", target, self.interface])
                        
                        # Reiniciar airodump
                        self.run_airodump()
                    except Exception as e:
                        print(f"Error en ataque: {e}")
            
            time.sleep(CONFIG["scan_interval"])

    def start(self):
        try:
            self.setup_interface()
            self.run_airodump()
            self.loop()
        except KeyboardInterrupt:
            print("\n🛑 Deteniendo...")
            if self.process: self.process.terminate()
            self.ref_root.child('status').update({"online": False})

if __name__ == "__main__":
    # Si se ejecuta con "install", instala el servicio
    if len(sys.argv) > 1 and sys.argv[1] == "install":
        install_system()
    else:
        # Si no, corre el agente
        KainosAgent().start()
