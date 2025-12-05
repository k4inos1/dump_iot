# 🛡️ KAINOS AUDITOR

> **Sistema de Auditoría Wi-Fi IoT con Sincronización en la Nube**

![Status](https://img.shields.io/badge/Status-Active-success)
![Platform](https://img.shields.io/badge/Platform-Raspberry_Pi_3B+-cbb06a)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Firebase](https://img.shields.io/badge/Backend-Firebase_Realtime_DB-orange)

**Kainos Auditor** es una plataforma avanzada de seguridad ofensiva y monitoreo de espectro diseñada para la era del Internet de las Cosas (IoT). Transforma una Raspberry Pi en un agente autónomo capaz de auditar redes Wi-Fi, detectar amenazas y ejecutar contramedidas, todo controlado remotamente desde una consola centralizada en la nube.

---

## 🌟 Características Principales

*   **📡 Monitoreo en Tiempo Real:** Detección continua de redes (APs) y clientes conectados.
*   **☁️ Arquitectura Cloud-Native:** Sincronización bidireccional con Google Firebase. Controla tu agente desde cualquier lugar del mundo.
*   **��️ Modo Sigiloso:** Operación pasiva en "Modo Monitor" indetectable por la mayoría de los sistemas.
*   **⚡ Respuesta Activa:** Capacidad de inyección de paquetes (Deauth) para pruebas de seguridad y captura de handshakes.
*   **🖥️ Consola Multi-Interfaz:**
    *   **CLI (Terminal):** Para servidores y usuarios avanzados (basada en `Rich`).
    *   **GUI (Gráfica):** Interfaz moderna y visual (basada en `CustomTkinter`).

---

## 🛠️ Arquitectura del Sistema

El sistema se compone de dos nodos principales desacoplados físicamente:

1.  **El Agente (Raspberry Pi):**
    *   Ejecuta `kainos.py` como servicio del sistema (`systemd`).
    *   Gestiona la tarjeta Wi-Fi en modo monitor (`airmon-ng`).
    *   Publica telemetría en Firebase.
    *   Escucha y ejecuta comandos remotos.

2.  **La Consola (PC Windows/Linux):**
    *   Ejecuta `console.py`.
    *   Visualiza los datos en tiempo real.
    *   Envía comandos de ataque o gestión al agente.

---

## 📋 Requisitos

### Hardware
*   **Raspberry Pi 3B+** (o superior).
*   **Tarjeta Wi-Fi USB** compatible con Modo Monitor e Inyección de Paquetes (Chipsets: Atheros AR9271, Ralink RT3070, Realtek RTL8812AU, etc.).
*   Tarjeta MicroSD (16GB+).

### Software
*   **OS Agente:** Raspberry Pi OS (Legacy/Bullseye recomendado para mejor compatibilidad con drivers).
*   **OS Consola:** Windows 10/11 o Linux.
*   **Python 3.9+**.
*   **Cuenta de Google Firebase** (Realtime Database).

---

## 🚀 Instalación Rápida

### 1. Preparación del Agente (Raspberry Pi)

Transfiere los archivos del proyecto a tu Raspberry Pi:

```bash
# Desde tu PC (PowerShell)
scp -r . pi@<IP_DE_TU_RPI>:/home/pi/dump_iot/
```

### 2. Instalación Automática

Conéctate por SSH a la Raspberry Pi y ejecuta el instalador integrado:

```bash
ssh pi@<IP_DE_TU_RPI>
cd dump_iot

# Este comando instala dependencias (aircrack-ng, python libs) y configura el servicio
sudo python3 kainos.py install
```

El agente se iniciará automáticamente y comenzará a reportar a la nube.

### 3. Configuración de la Consola (PC)

Asegúrate de tener las dependencias instaladas en tu máquina local:

```bash
pip install -r requirements.txt
```

---

## 🎮 Uso

### Iniciar la Consola de Control

Puedes iniciar la consola en modo interactivo, que te permitirá elegir entre la interfaz gráfica o de texto:

```bash
python console.py
```

### Comandos Disponibles (Desde la Consola)

*   **Escanear:** El agente escanea automáticamente (Channel Hopping).
*   **Atacar (Deauth):** Selecciona una red y envía paquetes de desautenticación para desconectar clientes.
*   **Reiniciar Agente:** Envía un comando de `reboot` a la Raspberry Pi remota.

---

## 📂 Estructura del Proyecto

```text
dump_iot/
├── kainos.py           # CEREBRO: Script principal del agente (IoT)
├── console.py          # INTERFAZ: Launcher de la consola de control
├── console_cli.py      # UI: Interfaz de línea de comandos (Rich)
├── console_remote.py   # UI: Interfaz gráfica (CustomTkinter)
├── requirements.txt    # Dependencias de Python
├── INFORME_TECNICO.md  # Documentación detallada del proyecto
└── ...
```

---

## ⚠️ Aviso Legal y Ético

**Kainos Auditor** es una herramienta educativa y de auditoría profesional.

*   **Uso Autorizado:** Úsalo únicamente en redes de tu propiedad o para las cuales tengas permiso explícito por escrito.
*   **Responsabilidad:** Los desarrolladores no se hacen responsables del mal uso de esta herramienta. La interrupción de redes ajenas es un delito penado por la ley en la mayoría de los países.

---

_Desarrollado con ❤️ y ☕ para el avance de la ciberseguridad IoT._
