#!/bin/sh
set -eu
if [ "$#" -ne 1 ]; then
  echo 'Usage: build_hf20.command CLEAN_JP.ws' >&2
  exit 2
fi
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
base_rom=$1
python3 "$script_dir/source/build_phase4w_hf20.py" "$base_rom" "$script_dir/HF20_PRIVATE.ws" "$script_dir/HF20_CUMULATIVE_FROM_JP.bps"
python3 "$script_dir/source/validate_hf20.py" "$base_rom"
