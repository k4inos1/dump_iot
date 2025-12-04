import customtkinter as ctk
import subprocess
import threading
import os
import sys
import time
from PIL import Image
import json

# Configuración de tema
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

class KainosConsole(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("KAINOS AUDITOR - ADVANCED COMMAND CENTER")
        self.geometry("1000x700")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- VARIABLES DE CONTROL ---
        self.sync_process = None
        self.target_bssid_var = ctk.StringVar()
        self.target_ip_var = ctk.StringVar(value="192.168.1.0/24")
        self.channel_var = ctk.StringVar(value="Auto")
        self.ports_var = ctk.StringVar(value="Top 100")

        # --- SIDEBAR (MENÚ) ---
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(8, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar, text="KAINOS\nWARFARE", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Botones de Acción
        self.btn_monitor = ctk.CTkButton(self.sidebar, text="📡 Modo Monitor", command=self.enable_monitor)
        self.btn_monitor.grid(row=1, column=0, padx=20, pady=10)

        self.btn_scan = ctk.CTkButton(self.sidebar, text="🔍 Escanear WiFi", command=self.scan_networks)
        self.btn_scan.grid(row=2, column=0, padx=20, pady=10)

        self.btn_deauth = ctk.CTkButton(self.sidebar, text="😈 Ataque Deauth", command=self.run_deauth, fg_color="#990000", hover_color="#660000")
        self.btn_deauth.grid(row=3, column=0, padx=20, pady=10)

        self.btn_tracker = ctk.CTkButton(self.sidebar, text="🕵️ Rastreador", command=self.run_tracker, fg_color="#4B0082", hover_color="#38006b")
        self.btn_tracker.grid(row=4, column=0, padx=20, pady=10)

        self.btn_vuln = ctk.CTkButton(self.sidebar, text="🛡️ Vuln Scan", command=self.run_vuln_scan, fg_color="#FF8C00", hover_color="#cc7000")
        self.btn_vuln.grid(row=5, column=0, padx=20, pady=10)

        self.btn_bettercap = ctk.CTkButton(self.sidebar, text="☠️ Bettercap", command=self.run_bettercap, fg_color="#000000", hover_color="#333333", border_color="red", border_width=1)
        self.btn_bettercap.grid(row=6, column=0, padx=20, pady=10)

        # --- PANEL PRINCIPAL ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)


        # 1. CONFIGURACIÓN (TARGETING)
        self.config_frame = ctk.CTkFrame(self.main_frame)
        self.config_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.config_frame.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(self.config_frame, text="SELECCIÓN DE OBJETIVO (DESDE SCAN)", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w", columnspan=4)

        # Smart Target Selector
        ctk.CTkLabel(self.config_frame, text="Red Detectada:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.combo_targets = ctk.CTkComboBox(self.config_frame, width=300, command=self.on_target_select)
        self.combo_targets.set("--- Escanea primero ---")
        self.combo_targets.grid(row=1, column=1, padx=10, pady=5, sticky="ew", columnspan=2)
        
        self.btn_refresh = ctk.CTkButton(self.config_frame, text="🔄", width=30, command=self.load_targets)
        self.btn_refresh.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        # Manual Override (Hidden/Secondary)
        ctk.CTkLabel(self.config_frame, text="BSSID:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.entry_bssid = ctk.CTkEntry(self.config_frame, textvariable=self.target_bssid_var, placeholder_text="Auto-relleno")
        self.entry_bssid.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.config_frame, text="Canal:").grid(row=2, column=2, padx=10, pady=5, sticky="e")
        self.combo_channel = ctk.CTkComboBox(self.config_frame, variable=self.channel_var, values=["Auto"] + [str(i) for i in range(1, 15)])
        self.combo_channel.grid(row=2, column=3, padx=10, pady=5, sticky="w")


        # Network Targets
        ctk.CTkLabel(self.config_frame, text="IP / Rango:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.entry_ip = ctk.CTkEntry(self.config_frame, textvariable=self.target_ip_var)
        self.entry_ip.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.config_frame, text="Puertos:").grid(row=2, column=2, padx=10, pady=5, sticky="e")
        self.combo_ports = ctk.CTkComboBox(self.config_frame, variable=self.ports_var, values=["Top 100", "Full (1-65535)", "Web (80,443)", "SSH (22)"])
        self.combo_ports.grid(row=2, column=3, padx=10, pady=5, sticky="w")

        # 2. SYNC CONTROL
        self.sync_frame = ctk.CTkFrame(self.main_frame, fg_color="#1a1a1a")
        self.sync_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        self.lbl_sync = ctk.CTkLabel(self.sync_frame, text="☁️ FIREBASE SYNC:", font=ctk.CTkFont(weight="bold"))
        self.lbl_sync.pack(side="left", padx=20, pady=10)
        
        self.switch_sync = ctk.CTkSwitch(self.sync_frame, text="DESACTIVADO", command=self.toggle_sync, onvalue="ON", offvalue="OFF", progress_color="#00ff00")
        self.switch_sync.pack(side="left", padx=10)

        # 3. LOGS
        self.log_box = ctk.CTkTextbox(self.main_frame, font=("Consolas", 12))
        self.log_box.grid(row=2, column=0, sticky="nsew")
        self.log_box.insert("0.0", "--- SISTEMA LISTO ---\n")

    def log(self, msg):
        self.log_box.insert("end", f"> {msg}\n")
        self.log_box.see("end")

    def load_targets(self):
        """Carga las redes desde networks.json"""
        try:
            if os.path.exists('networks.json'):
                with open('networks.json', 'r') as f:
                    data = json.load(f)
                
                self.network_data = data # Guardar referencia
                targets = []
                for bssid_key, info in data.items():
                    bssid = bssid_key.replace("-", ":")
                    ssid = info.get('ssid', 'Hidden')
                    rssi = info.get('power', '?')
                    targets.append(f"{ssid} | {bssid} | {rssi}dBm")
                
                self.combo_targets.configure(values=targets)
                self.log(f"Cargados {len(targets)} objetivos desde caché.")
            else:
                self.log("⚠️ No hay datos de escaneo. Ejecuta 'Escanear WiFi' primero.")
        except Exception as e:
            self.log(f"Error cargando targets: {e}")

    def on_target_select(self, choice):
        """Auto-rellena BSSID y Canal al seleccionar del combo"""
        try:
            # choice format: "SSID | BSSID | RSSI"
            parts = choice.split(" | ")
            if len(parts) >= 2:
                bssid = parts[1]
                self.target_bssid_var.set(bssid)
                
                # Buscar canal en los datos cargados
                key = bssid.replace(":", "-")
                if hasattr(self, 'network_data') and key in self.network_data:
                    channel = self.network_data[key].get('channel', 'Auto')
                    self.channel_var.set(channel)
                    self.log(f"Objetivo fijado: {parts[0]} (CH {channel})")
        except:
            pass



    # --- LOGICA ---
    def toggle_sync(self):
        if self.switch_sync.get() == "ON":
            self.switch_sync.configure(text="ACTIVADO (Subiendo datos...)")
            self.log("Iniciando servicio de sincronización...")
            # Lanzar sync_service.py en segundo plano
            self.sync_process = subprocess.Popen(["python3", "sync_service.py"])
        else:
            self.switch_sync.configure(text="DESACTIVADO")
            self.log("Deteniendo sincronización...")
            if self.sync_process:
                self.sync_process.terminate()
                self.sync_process = None

    def enable_monitor(self):
        self.log("Activando Modo Monitor...")
        subprocess.Popen("lxterminal -e 'sudo ./setup_monitor.sh'", shell=True)

    def scan_networks(self):
        self.log("Escaneando redes...")
        subprocess.Popen("lxterminal -e 'sudo ./scan_networks.sh'", shell=True)

    def run_deauth(self):
        target = self.target_bssid_var.get()
        channel = self.channel_var.get()
        
        if not target:
            self.log("❌ ERROR: Debes especificar un BSSID objetivo arriba.")
            return
            
        cmd = f"sudo ./deauth_test.sh {target}"
        if channel != "Auto":
            cmd += f" {channel}"
            
        self.log(f"Lanzando ataque a {target} (CH: {channel})...")
        subprocess.Popen(f"lxterminal -e '{cmd}'", shell=True)

    def run_tracker(self):
        self.log("Iniciando Rastreador...")
        subprocess.Popen("lxterminal -e 'sudo python3 tracker.py'", shell=True)

    def run_vuln_scan(self):
        target = self.target_ip_var.get()
        self.log(f"Escaneando vulnerabilidades en {target}...")
        # Pasamos el target como variable de entorno o argumento si modificamos el script
        # Por ahora el script usa una variable interna, pero podríamos mejorarlo:
        cmd = f"sudo ./vuln_scan.sh {target}" 
        subprocess.Popen(f"lxterminal -e '{cmd}'", shell=True)

    def run_bettercap(self):
        self.log("Iniciando Bettercap...")
        subprocess.Popen("lxterminal -e 'sudo bettercap'", shell=True)

if __name__ == "__main__":
    app = KainosConsole()
    app.mainloop()
