import logging
from scapy.all import *
from datetime import datetime
import os
import sys
import time

# Importar módulo de conexión Firebase (del auditor.py)
try:
    from auditor import init_firebase, db
    FIREBASE_AVAILABLE = init_firebase()
except ImportError:
    FIREBASE_AVAILABLE = False
    print("⚠️ No se pudo importar auditor.py. Modo Offline.")

# Configuración
INTERFACE = "wlan1"
LOG_FILE = "logs/tracker_log.csv"

# Colores
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'

if not os.path.exists("logs"):
    os.makedirs("logs")

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as f:
        f.write("Timestamp,MAC,SSID,RSSI,Vendor\n")

print(f"{GREEN}[*] INICIANDO RASTREADOR + FIREBASE SYNC{RESET}")

def packet_handler(pkt):
    if pkt.haslayer(Dot11ProbeReq):
        try:
            mac = pkt.addr2
            ssid = pkt.info.decode('utf-8') if pkt.info else "<OCULTO>"
            rssi = pkt.dBm_AntSignal if hasattr(pkt, 'dBm_AntSignal') else -100
            
            now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ts = int(time.time())
            
            # 1. Guardar en CSV Local
            with open(LOG_FILE, "a") as f:
                f.write(f"{now_str},{mac},{ssid},{rssi},Unknown\n")
            
            # 2. Subir a Firebase (Real-time)
            if FIREBASE_AVAILABLE:
                try:
                    # Usamos la MAC como clave (reemplazando : por -)
                    mac_key = mac.replace(":", "-")
                    ref = db.reference(f'auditoria/live_tracking/{mac_key}')
                    
                    data = {
                        'last_seen': ts,
                        'last_ssid_searched': ssid,
                        'rssi': rssi,
                        'mac': mac
                    }
                    
                    # Actualizar datos del dispositivo
                    ref.update(data)
                    
                    # Guardar historial de búsquedas de este dispositivo
                    if ssid != "<OCULTO>":
                        ref.child('history').push({
                            'ssid': ssid,
                            'ts': ts
                        })
                        
                except Exception as e:
                    pass # No bloquear si falla internet

            # Mostrar en pantalla
            color = GREEN
            if int(rssi) > -60: 
                color = RED
            
            print(f"{color}[{now_str}] 📡 {mac} ({rssi}dBm) -> Buscando: '{ssid}'{RESET}")
            
        except Exception as e:
            pass

try:
    sniff(iface=INTERFACE, prn=packet_handler, store=0)
except KeyboardInterrupt:
    print(f"\n{RED}[*] Detenido.{RESET}")
except Exception as e:
    print(f"\n{RED}[!] Error: {e}{RESET}")
