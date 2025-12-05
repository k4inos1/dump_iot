import customtkinter as ctk
import firebase_admin
from firebase_admin import credentials, db
import glob
import sys
import threading
import time

# --- CONFIGURACIÓN ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

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

class KainosGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Kainos Auditor - Command Center")
        self.geometry("1100x700")
        
        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="🛡️ KAINOS", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(30, 10))
        ctk.CTkLabel(self.sidebar, text="AUDITOR", font=ctk.CTkFont(size=16)).pack(pady=(0, 20))
        
        self.status_indicator = ctk.CTkLabel(self.sidebar, text="⚫ CONECTANDO...", font=("Arial", 12, "bold"))
        self.status_indicator.pack(pady=10)
        
        ctk.CTkLabel(self.sidebar, text="_________________", text_color="gray").pack(pady=10)
        
        self.btn_reboot = ctk.CTkButton(self.sidebar, text="🔄 REINICIAR PI", fg_color="#c0392b", hover_color="#e74c3c", command=self.cmd_reboot)
        self.btn_reboot.pack(pady=20, padx=20, side="bottom")

        # --- MAIN AREA ---
        self.main_frame = ctk.CTkScrollableFrame(self, label_text="REDES DETECTADAS (Tiempo Real)")
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        # Iniciar loop de actualización
        self.after(1000, self.update_loop)

    def update_loop(self):
        """Consulta Firebase y actualiza la UI."""
        try:
            # Leer todo el nodo
            data = ref_root.get()
            if data:
                self.update_status(data.get('status', {}))
                self.render_networks(data.get('networks', {}))
        except Exception as e:
            print(f"Error sync: {e}")
        
        self.after(3000, self.update_loop) # Actualizar cada 3 seg

    def update_status(self, status):
        if status.get('online'):
            self.status_indicator.configure(text="🟢 ONLINE", text_color="#2ecc71")
        else:
            self.status_indicator.configure(text="🔴 OFFLINE", text_color="#e74c3c")

    def render_networks(self, networks):
        # Limpiar frame (optimizable)
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        if not networks:
            ctk.CTkLabel(self.main_frame, text="Esperando datos del agente...").pack(pady=20)
            return

        # Ordenar por potencia
        sorted_nets = sorted(networks.items(), key=lambda x: int(x[1].get('pwr', -100)), reverse=True)
        
        for bssid, info in sorted_nets:
            self.create_card(bssid, info)

    def create_card(self, bssid, info):
        card = ctk.CTkFrame(self.main_frame, fg_color="#2b2b2b")
        card.pack(fill="x", padx=5, pady=5)
        
        # Columna Izq: Info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", padx=10, pady=10)
        
        ssid = info.get('ssid', '<Oculto>')
        if not ssid.strip(): ssid = "<Oculto>"
        
        ctk.CTkLabel(info_frame, text=ssid, font=("Arial", 16, "bold")).pack(anchor="w")
        ctk.CTkLabel(info_frame, text=f"{bssid}  |  CH: {info.get('ch')}  |  {info.get('sec')}", text_color="gray").pack(anchor="w")
        
        # Columna Centro: Señal
        pwr = int(info.get('pwr', -100))
        color = "#2ecc71" if pwr > -60 else "#f1c40f" if pwr > -80 else "#e74c3c"
        ctk.CTkLabel(card, text=f"{pwr} dBm", text_color=color, font=("Arial", 14, "bold")).pack(side="left", padx=20)
        
        # Columna Der: Botón
        btn = ctk.CTkButton(card, text="⚔️ DEAUTH", width=100, fg_color="#8e44ad", hover_color="#9b59b6",
                            command=lambda b=bssid, c=info.get('ch'): self.cmd_deauth(b, c))
        btn.pack(side="right", padx=10)

    def cmd_reboot(self):
        ref_root.child('commands').set("reboot")
        print("Comando enviado: REBOOT")

    def cmd_deauth(self, bssid, channel):
        cmd = f"deauth|{bssid}|{channel}"
        ref_root.child('commands').set(cmd)
        print(f"Comando enviado: DEAUTH -> {bssid}")

if __name__ == "__main__":
    app = KainosGUI()
    app.mainloop()