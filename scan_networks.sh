#!/bin/bash

INTERFACE="wlan1"
OUTPUT_DIR="logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
FILENAME="scan_$TIMESTAMP"

# Crear carpeta de logs si no existe
mkdir -p $OUTPUT_DIR

echo "--- INICIANDO ESCANEO DE REDES ---"
echo "Los datos se guardarán en: $OUTPUT_DIR/$FILENAME"
echo "Presiona CTRL+C para detener el escaneo."

# Ejecutar airodump-ng y guardar en CSV
# --write-interval 1 : Actualiza el archivo cada segundo (bueno para tiempo real)
sudo airodump-ng --write $OUTPUT_DIR/$FILENAME --output-format csv --write-interval 1 $INTERFACE
