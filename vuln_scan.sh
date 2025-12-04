#!/bin/bash

# Configuración
OUTPUT_DIR="logs/vuln_scans"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="$OUTPUT_DIR/scan_$TIMESTAMP.txt"

# Si se pasa argumento, usarlo. Si no, usar default.
if [ -z "$1" ]; then
    NETWORK="192.168.1.0/24"
else
    NETWORK="$1"
fi

mkdir -p $OUTPUT_DIR

echo "--- INICIANDO ESCÁNER DE VULNERABILIDADES (NMAP) ---"
echo "Objetivo: $NETWORK"
echo "Guardando reporte en: $REPORT_FILE"

# 1. Descubrimiento de Hosts (Ping Scan)
echo "[*] Buscando dispositivos vivos..."
nmap -sn $NETWORK -oG - | awk '/Up$/{print $2}' > hosts_vivos.txt

COUNT=$(wc -l < hosts_vivos.txt)
echo "[*] Dispositivos encontrados: $COUNT"

if [ "$COUNT" -eq "0" ]; then
    echo "[!] No se encontraron dispositivos. Revisa la IP de la red."
    exit 1
fi

# 2. Escaneo de Vulnerabilidades
echo "[*] Analizando vulnerabilidades en los objetivos (Esto tardará)..."
# -sV: Versiones de servicios
# --script vuln: Ejecuta scripts de detección de CVEs y fallos
# -iL: Lee la lista de hosts vivos
sudo nmap -sV --script vuln -iL hosts_vivos.txt -oN $REPORT_FILE

echo "--- ESCANEO FINALIZADO ---"
echo "Reporte guardado en: $REPORT_FILE"
cat $REPORT_FILE
