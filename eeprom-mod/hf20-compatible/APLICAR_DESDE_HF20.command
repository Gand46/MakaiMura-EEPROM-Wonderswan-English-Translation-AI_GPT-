#!/bin/bash
set -eu
cd -- "$(dirname -- "$0")"
rom_path="${1:-}"
if [ -z "$rom_path" ]; then
 read -r -p "Ruta de la ROM HF20 (sin comillas): " rom_path
fi
python3 source/apply_patch.py "$rom_path" patches/Makaimura_HF20_EEPROM_v1_FROM_HF20.bps Makaimura_HF20_EEPROM_v1.ws
