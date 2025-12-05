# 🛡️ KAINOS AUDITOR (Cloud Edition)

Sistema de auditoría WiFi autónomo para Raspberry Pi con sincronización en tiempo real a Firebase.

## 📂 Estructura Minimalista

Todo el sistema se ha condensado en un único script inteligente:

1.  **`kainos.py`**: Instalador + Agente + Sincronizador.
2.  **`kainos-auditor-firebase-*.json`**: Tu llave de acceso.

## 🚀 Instalación (Un solo comando)

1.  **Copiar archivos a la Raspberry:**
    ```powershell
    scp -r . pi@192.168.137.133:/home/pi/dump_iot/
    ```

2.  **Ejecutar instalador:**
    ```bash
    cd dump_iot
    sudo python3 kainos.py install
    ```

¡Listo! El script instalará dependencias, creará el servicio y se iniciará automáticamente.

## ☁️ Control Remoto (Firebase)

Controla el agente escribiendo en el nodo `kainos_auditor/commands` de tu Realtime Database:

| Comando | Acción |
| :--- | :--- |
| `"reboot"` | Reinicia la Raspberry Pi |
| `"deauth|BSSID|CANAL"` | Ataca un objetivo (Ej: `deauth|AA:BB:CC:DD:EE:FF|6`) |

## 📊 Datos en Vivo

Toda la información se vuelca en:
- `kainos_auditor/networks`: Redes detectadas.
- `kainos_auditor/clients`: Dispositivos conectados.
- `kainos_auditor/status`: Estado del agente (Online/Offline).

### Opción A: Deployment Automático

**Desde tu PC Windows (PowerShell):**

```powershell
cd C:\Users\TU_USUARIO\Desktop\dump_iot

# Editar deploy.sh y cambiar la IP a la de tu RPi
# RPI_HOST="192.168.1.XX"

# Ejecutar deployment
bash deploy.sh
```

Este script:
1. ✅ Verifica archivos locales
2. ✅ Transfiere todo via SCP
3. ✅ Configura permisos
4. ✅ Ejecuta instalación remota

---

### Opción B: Instalación Manual

#### Paso 1: Flashear Raspberry Pi OS

1. Descarga **Raspberry Pi Imager**: https://www.raspberrypi.com/software/
2. Configuración:
   - **Dispositivo**: Raspberry Pi 3
   - **OS**: Raspberry Pi OS (64-bit) Lite
   - **Personalización** (⚙️):
     - ✅ SSH activado
     - Usuario: `pi` / Contraseña: `raspberry`
     - Wi-Fi: Tu red + contraseña
     - País: `CL`
3. Flashear SD

#### Paso 2: Conectar y Transferir

```powershell
# Esperar 3-5 min tras boot inicial
# Encontrar IP
arp -a | Select-String "b8-27-eb"

# Conectar SSH
ssh pi@192.168.1.XX

# Desde otra terminal en Windows
cd C:\Users\TU_USUARIO\Desktop\dump_iot

# Transferir archivos
scp -r * pi@192.168.1.XX:/home/pi/dump_iot/

# Transferir credenciales
scp .env pi@192.168.1.XX:/home/pi/dump_iot/
# O:
scp kainos-auditor-firebase-*.json pi@192.168.1.XX:/home/pi/dump_iot/
```

#### Paso 3: Instalación en Raspberry

```bash
cd dump_iot
chmod +x *.sh
sudo ./install_all.sh
```

Esto instala (10-15 min):
- Nmap, Aircrack-ng, Wireshark
- Bettercap
- Python (firebase-admin, scapy, rich, customtkinter)
- XRDP (escritorio remoto)
- Drivers kernel

#### Paso 4: Configurar Fenvi AX1800

```bash
# Clonar driver
cd ~
git clone https://github.com/morrownr/rtl8852bu-20240418.git
cd rtl8852bu-20240418

# Instalar
sudo ./install-driver.sh
# Presionar "Y" cuando pregunte por reboot

# Después del reinicio, verificar
ip a | grep wlan1  # Debe aparecer
```

#### Paso 5: Habilitar Firestore

1. https://console.firebase.google.com
2. Proyecto: **Kainos-Auditor**
3. **Firestore Database** → **Create Database**
4. Modo: **Test mode**
5. Región: **us-central**
6. **Enable**

---

## 🎮 Uso del Sistema

### Consola CLI (SSH) ⭐ Recomendada

```bash
cd dump_iot

# Iniciar servicios de fondo
./start_agent.sh

# Abrir consola
python3 console_cli.py
```

**Menú:**
```
1. 📡 Activar Modo Monitor
2. 🔍 Escanear Redes (Airodump)
3. 😈 Ataque Deauth
4. 🕵️ Rastreador (Probe Requests)
5. 🛡️ Escáner de Vulnerabilidades
6. ☠️ Bettercap (MITM)
7. ☁️ Sincronizar con Firebase
0. 🚪 Salir
```

### Consola GUI (RDP)

**Desde Windows:**
1. Abrir "Conexión a Escritorio Remoto"
2. IP: `192.168.1.XX`
3. Usuario: `pi` / Contraseña: `raspberry`

**Dentro del escritorio:**
```bash
cd dump_iot
python3 console.py
```

---

## 🔥 Flujo de Trabajo Típico

### Escenario: Auditar Red de Inacap

```bash
# 1. Conectar RPi por Ethernet al router
# (WiFi interno NO se conecta a Inacap para evitar bloqueo)

# 2. SSH desde tu laptop (conectado a Inacap WiFi)
ssh pi@192.168.1.59

# 3. Activar modo monitor
python3 console_cli.py
# → Opción 1

# 4. Escanear redes cercanas
# → Opción 2
# Dejar correr 2-3 minutos, Ctrl+C

# 5. Volver al menú y sincronizar
# → Opción 7

# 6. Ver datos en Firebase
# Abrir navegador: https://console.firebase.google.com
# → Realtime Database: auditoria/redes_detectadas
# → Firestore: colección "redes"
```

**Resultado:**
- ✅ Raspberry detecta ~20-30 redes Inacap
- ✅ Datos suben vía Ethernet
- ✅ Tu laptop ve todo en Firebase en tiempo real
- ✅ No te conectaste a ninguna red WiFi sospechosa

---

## 📂 Estructura de Archivos

```
dump_iot/
├── console.py              # gui (customtkinter)
├── console_cli.py          # cli (rich) ⭐
├── auditor.py              # firebase dual storage
├── tracker.py              # sniffer probe requests
├── sync_service.py         # daemon auto-sync
├── setup_monitor.sh        # activar modo monitor
├── scan_networks.sh        # wrapper airodump-ng
├── deauth_test.sh          # ataque deauth
├── vuln_scan.sh            # escaneo nmap
├── install_all.sh          # instalador maestro
├── start_agent.sh          # iniciar servicios
├── deploy.sh               # deployment automatizado
├── generate_env.py         # generador .env
├── requirements.txt        # dependencias python
├── database.rules.json     # reglas firebase rtdb
├── FENVI_SETUP.md          # guía antena
└── README.md               # este archivo
```

---

## 🆘 Troubleshooting

### No detecta wlan1 (Fenvi)

```bash
# Verificar USB
lsusb | grep Realtek

# Si no aparece: re-conectar físicamente

# Si aparece pero no wlan1:
sudo modprobe 8852bu
sudo reboot
```

### Airodump no funciona

```bash
# Instalar aircrack-ng
sudo apt install -y aircrack-ng

# Verificar modo monitor
iwconfig wlan1  # Debe decir "Mode:Monitor"

# Si no:
sudo ./setup_monitor.sh
```

### Firebase no conecta

```bash
# Verificar credenciales
ls -la .env
ls -la *.json

# Probar conexión
python3 auditor.py

# Debe decir:
# 🔥 Firebase Realtime Database Conectado
# 💾 Firestore Conectado
```

### Sync service no sube datos

```bash
# Verificar que esté corriendo
ps aux | grep sync_service

# Si no está:
./start_agent.sh

# Ver logs en vivo
tail -f logs/sync.log
```

### XRDP pantalla negra

```bash
sudo apt install -y lxde-core lightdm
sudo systemctl restart xrdp
sudo reboot
```

---

## 🔒 Seguridad

### Archivos Protegidos (NO COMMIT)

`.gitignore` bloquea automáticamente:
- `.env` (credenciales base64)
- `kainos-auditor-firebase-*.json` (clave de servicio)
- `networks.json` (caché redes)
- `logs/` (datos capturados)

### Cambiar Contraseña

```bash
passwd
# Ingresar nueva contraseña
```

### Reglas Firebase

**Realtime Database:**
Copia `database.rules.json` a:
Firebase Console → Realtime Database → Rules

**Firestore:**
Firebase Console → Firestore → Rules:
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}
```

---

## 📊 Estructura de Datos en Firebase

### Realtime Database

```
auditoria/
├── estado_sistema/                 # último heartbeat
├── redes_detectadas/               # scans airodump
│   └── AA-BB-CC-DD-EE-FF/
│       ├── ssid: "Inacap_WiFi"
│       ├── channel: "6"
│       ├── crypto: "WPA2"
│       └── power: "-45"
├── live_tracking/                  # probe requests
│   └── 11-22-33-44-55-66/
│       ├── last_seen: 1733290000
│       ├── last_ssid_searched: "iPhone de Juan"
│       ├── rssi: -60
│       └── history/
└── reportes_vuln/                  # nmap reports
    └── scan_20251204_044532.txt
```

### Firestore

```
redes/                              # escaneos wifi
└── AA-BB-CC-DD-EE-FF
    ├── ssid: "Inacap_WiFi"
    ├── channel: 6
    ├── timestamp: 1733290000
    
tracking/                           # dispositivos rastreados
└── 11-22-33-44-55-66
    ├── mac: "11:22:33:44:55:66"
    ├── last_seen: 1733290000
    ├── last_ssid: "iPhone de Juan"
    └── history/
        └── 1733290000
            ├── ssid: "iPhone de Juan"
            ├── rssi: -60

reportes_vuln/                      # vulnerabilidades
└── scan_20251204_044532.txt
    ├── contenido: "Nmap scan report..."
    ├── timestamp: 1733290000
```

---

## 🔧 Comandos Útiles (Cheat Sheet)

```bash
# === ESTADO DEL SISTEMA ===
ip a                                # ver interfaces
iwconfig wlan1                      # verificar modo monitor
ps aux | grep sync_service          # ver servicio sync

# === OPERACIONES ===
./start_agent.sh                    # iniciar servicios
python3 console_cli.py              # abrir consola
sudo ./setup_monitor.sh             # activar modo monitor

# === LOGS ===
tail -f logs/sync.log               # ver sync en vivo
tail -f logs/tracker_log.csv        # ver tracking
ls logs/                            # listar logs

# === FIREBASE ===
python3 auditor.py                  # test conexión
cat networks.json | jq              # ver caché redes

# === TROUBLESHOOTING ===
lsusb | grep Realtek                # verificar fenvi
sudo modprobe 8852bu                # cargar driver
sudo systemctl status xrdp          # estado rdp
```

---

## 🤝 Contribuir

Pull requests bienvenidos. Abre un issue primero para cambios mayores.

---

## 📜 Licencia y Disclaimer

**Solo para fines educativos y auditorías autorizadas**.

⚠️ **ADVERTENCIA**: El uso no autorizado de estas herramientas es **ilegal**. El autor no se responsabiliza por el mal uso. Siempre obtén permiso por escrito antes de auditar cualquier red que no sea tuya.

---

## 🛠️ Desarrollado por

**Ricardo / KAINOS SYSTEMS - 2025**

Stack: Raspberry Pi OS · Python · Firebase (Realtime DB + Firestore) · Scapy · Bettercap · Aircrack-ng

---

**¿Preguntas?** Abre un issue en GitHub.

![Kainos](https://img.shields.io/badge/System-Raspberry_Pi_OS-red) ![Python](https://img.shields.io/badge/Python-3.11-blue) ![Status](https://img.shields.io/badge/Status-Operational-green) ![Firebase](https://img.shields.io/badge/Cloud-Firebase-orange)

---

## 🚀 Características

### 📡 Monitoreo WiFi
- **Modo Monitor Automático:** Activación de un click para Fenvi AX1800 (RTL8852BU)
- **Rastreo Intensivo:** Detecta dispositivos cercanos vía Probe Requests (MAC, RSSI, Historial de SSID)
- **Escaneo de Redes:** Airodump-ng con guardado automático en CSV

### ⚔️ Herramientas Ofensivas
- **Ataque Deauth:** Desconecta objetivos de sus redes
- **Escáner de Vulnerabilidades:** Nmap automatizado con scripts NSE
- **Bettercap:** Integrado para MITM y sniffing avanzado

### ☁️ Inteligencia en la Nube
- **Sincronización en Tiempo Real:** Logs y redes detectadas → Firebase Realtime Database
- **Caché Local:** `networks.json` para selección inteligente de objetivos
- **Historial Completo:** Probe requests y reportes de vulnerabilidades

### 🎛️ Interfaces Duales
- **GUI (Graphical):** Consola Dark Mode con selector de objetivos inteligente
- **CLI (Terminal):** TUI con Rich para uso por SSH (⭐ Recomendado)

---

## 📋 Requisitos

### Hardware
- Raspberry Pi 3B+ (o superior)
- Tarjeta MicroSD 16GB+
- Adaptador WiFi USB (Fenvi AX1800 / RTL8852BU recomendado)
- Fuente de alimentación 5V 2.5A

### Software
- Raspberry Pi OS Lite (64-bit) - **Recomendado**
- Python 3.11+
- Conexión a Internet (para instalación inicial)

---

## 🛠️ Instalación Completa

### Paso 1: Flashear Raspberry Pi OS

1. Descarga **Raspberry Pi Imager**: https://www.raspberrypi.com/software/
2. Selecciona:
   - **Dispositivo:** Raspberry Pi 3
   - **OS:** Raspberry Pi OS (64-bit) Lite
   - **Storage:** Tu MicroSD
3. **Configuración personalizada** (⚙️ engranaje):
   - ✅ Activar SSH
   - Usuario: `pi` / Contraseña: `raspberry`
   - Wi-Fi: Tu red + Contraseña
   - País: `CL` (o el tuyo)
4. Escribe y verifica

### Paso 2: Primer Boot y SSH

```powershell
# Espera 3-5 minutos tras conectar la RPi
# Encuentra la IP en tu router o ejecuta:
arp -a | Select-String "b8-27-eb"

# Conecta por SSH (reemplaza con tu IP)
ssh pi@192.168.1.59
```

### Paso 3: Transferir Archivos

**Desde PowerShell en Windows:**
```powershell
cd C:\Users\TU_USUARIO\Desktop\dump_iot

# Transferir todos los archivos
scp -r * pi@192.168.1.59:/home/pi/dump_iot/

# Transferir credenciales (IMPORTANTE)
scp .env pi@192.168.1.59:/home/pi/dump_iot/
# O si tienes el JSON:
scp kainos-auditor-firebase-*.json pi@192.168.1.59:/home/pi/dump_iot/
```

### Paso 4: Instalación Automática

**En SSH de la Raspberry:**
```bash
cd dump_iot
chmod +x install_all.sh
sudo ./install_all.sh
```

Esto instalará (⏳ 10-15 minutos):
- ✅ Nmap, Aircrack-ng, Wireshark, Bettercap
- ✅ Python (firebase-admin, scapy, rich, customtkinter)
- ✅ XRDP (Escritorio Remoto)
- ✅ Drivers del kernel

### Paso 5: Configurar Firebase

```bash
# Si trabajaste con .env
ls .env  # Debe existir

# Si usas el JSON directo
ls kainos-auditor-firebase-*.json

# Probar conexión
python3 auditor.py
# Debe decir: "🔥 Firebase Conectado Exitosamente"
```

---

## 🎮 Uso

### Opción A: Consola CLI (⭐ Recomendada para SSH)

```bash
python3 console_cli.py
```

**Menú:**
```
1. 📡 Activar Modo Monitor
2. 🔍 Escanear Redes (Airodump)
3. 😈 Ataque Deauth (Desconexión)
4. 🕵️ Rastreador (Probe Requests)
5. 🛡️ Escáner de Vulnerabilidades
6. ☠️ Bettercap (MITM)
7. ☁️ Sincronizar con Firebase
0. 🚪 Salir
```

### Opción B: Consola GUI (Para Escritorio Remoto)

**Desde Windows:**
1. Abre "Conexión a Escritorio Remoto"
2. Conecta a: `192.168.1.59`
3. Usuario: `pi` / Contraseña: `raspberry`

**Dentro del escritorio:**
```bash
cd dump_iot
python3 console.py
```

### Servicios de Fondo

```bash
# Iniciar sincronización automática a Firebase
./start_agent.sh

# Ver logs en tiempo real
tail -f logs/sync.log
```

---

## 📂 Estructura del Proyecto

```
dump_iot/
├── console.py              # GUI (CustomTkinter)
├── console_cli.py          # CLI (Rich)
├── auditor.py              # Integración Firebase
├── tracker.py              # Sniffer Probe Requests (Scapy)
├── sync_service.py         # Daemon de sincronización
├── setup_monitor.sh        # Activar Modo Monitor
├── scan_networks.sh        # Wrapper Airodump-ng
├── deauth_test.sh          # Ataque Deauth
├── vuln_scan.sh            # Escaneo Nmap
├── install_all.sh          # Instalador maestro
├── install_warfare.sh      # Instalador de herramientas
├── start_agent.sh          # Iniciar servicios
├── generate_env.py         # Generador .env
├── requirements.txt        # Dependencias Python
├── database.rules.json     # Reglas Firebase
└── README.md               # Este archivo
```

---

## 🔥 Ejemplos de Uso

### 1. Rastreo de Dispositivos Cercanos

```bash
# Activar modo monitor primero
sudo ./setup_monitor.sh

# Iniciar rastreador
sudo python3 tracker.py

# Los datos se guardan en:
# - Local: logs/tracker_log.csv
# - Firebase: auditoria/live_tracking/
```

### 2. Escaneo de Redes

```bash
# Desde la consola CLI (Opción 2)
# O manualmente:
sudo ./scan_networks.sh

# Resultados: logs/scan_TIMESTAMP.csv
# Firebase: auditoria/redes_detectadas/
```

### 3. Ataque Deauth

```bash
# Método 1: Desde consola GUI (selector inteligente)
# Método 2: Desde consola CLI (Opción 3)
# Método 3: Manual
sudo ./deauth_test.sh AA:BB:CC:DD:EE:FF 6
```

### 4. Escaneo de Vulnerabilidades

```bash
# Escanear red local
sudo ./vuln_scan.sh

# Escanear IP específica
sudo ./vuln_scan.sh 192.168.1.100

# Resultados: logs/vuln_scans/scan_TIMESTAMP.txt
```

---

## 🆘 Troubleshooting

### No encuentra la Raspberry por SSH

```powershell
# Buscar IP manualmente
arp -a | Select-String "b8-27"

# O escanear red
ping raspberrypi.local
```

### Error "ModuleNotFoundError"

```bash
# Reinstalar dependencias
sudo pip3 install -r requirements.txt --break-system-packages
```

### Modo Monitor no funciona

```bash
# Verificar interfaces
ip a

# Debe aparecer wlan1 (Fenvi)
# Si no:
sudo modprobe 8852bu
```

### Firebase no conecta

```bash
# Verificar credenciales
ls -la .env
ls -la *.json

# Probar conexión directa
python3 -c "from auditor import init_firebase; init_firebase()"
```

### XRDP pantalla negra

```bash
# Instalar escritorio completo
sudo apt install -y lxde-core lightdm
sudo systemctl restart xrdp
sudo reboot
```

---

## 🔒 Seguridad

### Archivos Críticos (NO SUBIR A GIT)

El `.gitignore` bloquea automáticamente:
- ✅ `.env` (Credenciales encriptadas)
- ✅ `*.json` (Claves Firebase)
- ✅ `networks.json` (Caché local de redes)
- ✅ `logs/` (Datos capturados)

### Cambiar Contraseña Predeterminada

```bash
passwd
# Ingresa una nueva contraseña segura
```

### Reglas Firebase

Copia el contenido de `database.rules.json` a tu Consola Firebase:
1. Ve a https://console.firebase.google.com
2. Realtime Database → Reglas
3. Pega el contenido y publica

---

## 📊 Monitoreo en Tiempo Real

### Ver Datos en Firebase Console

1. https://console.firebase.google.com
2. Proyecto: **Kainos-Auditor**
3. Realtime Database

**Estructura:**
```
auditoria/
├── live_tracking/          # Dispositivos rastreados
│   └── AA-BB-CC-DD-EE-FF/
│       ├── last_seen
│       ├── last_ssid_searched
│       └── history/
├── redes_detectadas/       # Redes WiFi escaneadas
│   └── AA-BB-CC-DD-EE-FF/
│       ├── ssid
│       ├── channel
│       └── crypto
└── reportes_vuln/          # Reportes Nmap
    └── scan_TIMESTAMP.txt
```

---

## 🤝 Contribuir

Pull requests son bienvenidos. Para cambios mayores, abre un issue primero.

---

## 📜 Licencia

Este proyecto es **solo para fines educativos y auditorías autorizadas**.

**⚠️ ADVERTENCIA:** El uso no autorizado de estas herramientas es ilegal. El autor no se responsabiliza por el mal uso.

---

## 🛠️ Desarrollado por

**Ricardo / KAINOS SYSTEMS - 2025**

Powered by: Raspberry Pi OS • Python • Firebase • Scapy • Bettercap
