import time
import os
import csv
import glob
from auditor import init_firebase, db

# Configuración
LOG_DIR = "logs"
VULN_DIR = "logs/vuln_scans"

def parse_airodump_csv(filepath):
    """Lee el CSV de Airodump y extrae redes"""
    networks = {}
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.reader(f)
            section = 0 # 0: Header, 1: Networks, 2: Clients
            for row in reader:
                if not row: continue
                if len(row) > 0 and row[0].strip() == 'BSSID':
                    section = 1
                    continue
                if len(row) > 0 and row[0].strip() == 'Station MAC':
                    section = 2
                    continue
                
                if section == 1 and len(row) >= 14:
                    bssid = row[0].strip()
                    channel = row[3].strip()
                    crypto = row[5].strip()
                    ssid = row[13].strip()
                    power = row[8].strip()
                    
                    if bssid and bssid != 'BSSID':
                        networks[bssid.replace(":", "-")] = {
                            'ssid': ssid,
                            'channel': channel,
                            'crypto': crypto,
                            'power': power,
                            'last_seen': int(time.time())
                        }
    except Exception as e:
        print(f"Error parsing CSV {filepath}: {e}")
    return networks

import json

# ... (imports)

def upload_networks():
    """Busca el archivo CSV más reciente, lo sube y guarda caché local"""
    list_of_files = glob.glob(f'{LOG_DIR}/*.csv') 
    if not list_of_files: return

    # Tomar el más nuevo
    latest_file = max(list_of_files, key=os.path.getctime)
    
    networks = parse_airodump_csv(latest_file)
    
    if networks:
        # 1. Guardar caché local para la GUI
        try:
            with open('networks.json', 'w') as f:
                json.dump(networks, f, indent=4)
        except Exception as e:
            print(f"Error guardando networks.json: {e}")

        # 2. Subir a Firebase
        try:
            ref = db.reference('auditoria/redes_detectadas')
            ref.update(networks)
            print(f"✅ {len(networks)} redes actualizadas en Firebase y Local.")
        except:
            pass

def upload_vuln_reports():
    """Sube reportes de Nmap"""
    if not os.path.exists(VULN_DIR): return
    
    list_of_files = glob.glob(f'{VULN_DIR}/*.txt')
    for filepath in list_of_files:
        filename = os.path.basename(filepath).replace(".", "_")
        
        with open(filepath, 'r') as f:
            content = f.read()
            
        ref = db.reference(f'auditoria/reportes_vuln/{filename}')
        ref.set({
            'content': content,
            'timestamp': int(time.time())
        })
        # Opcional: Mover a 'processed' para no resubir siempre
        # os.rename(filepath, filepath + ".uploaded")

def main_loop():
    print("--- INICIANDO SERVICIO DE SINCRONIZACIÓN ---")
    if not init_firebase():
        print("❌ No se pudo conectar a Firebase. Saliendo.")
        return

    while True:
        try:
            upload_networks()
            upload_vuln_reports()
        except Exception as e:
            print(f"⚠️ Error en ciclo de sync: {e}")
        
        time.sleep(10) # Revisar cada 10 segundos

if __name__ == "__main__":
    main_loop()
