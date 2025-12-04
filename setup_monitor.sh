#!/bin/bash

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

INTERFACE="wlan1"

echo -e "${GREEN}[*] Configurando tarjeta $INTERFACE en Modo Monitor...${NC}"

# Bajar interfaz
sudo ip link set $INTERFACE down

# Cambiar a modo monitor
sudo iw dev $INTERFACE set type monitor

# Subir interfaz
sudo ip link set $INTERFACE up

# Verificar
MODE=$(iwconfig $INTERFACE | grep "Mode:Monitor")

if [ -n "$MODE" ]; then
    echo -e "${GREEN}[SUCCESS] ¡Tarjeta lista en MODO MONITOR! 😈${NC}"
    iwconfig $INTERFACE
else
    echo -e "${RED}[ERROR] No se pudo activar el modo monitor.${NC}"
fi
