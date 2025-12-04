#!/bin/bash

echo "--- INSTALANDO ARSENAL DE CIBERGUERRA ---"

# 1. Actualizar
sudo apt update

# 2. Instalar Nmap y dependencias de Python
sudo apt install -y nmap python3-pip libpcap-dev

# 3. Instalar Bettercap (La bestia)
echo "[*] Instalando Bettercap..."
# En RPi a veces es mejor bajar el binario precompilado o usar Go, 
# pero intentaremos primero por apt o descarga directa si falla.
sudo apt install -y bettercap

# 4. Instalar Scapy (Para el tracker.py)
echo "[*] Instalando Scapy..."
sudo pip3 install scapy --break-system-packages

echo "--- INSTALACIÓN COMPLETADA ---"
echo "Ahora puedes usar:"
echo "1. tracker.py (Rastreo)"
echo "2. vuln_scan.sh (Vulnerabilidades)"
echo "3. bettercap (MITM y Sniffing)"
