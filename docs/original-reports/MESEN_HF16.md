# Reproducción QA HF16 con Mesen 2.1.1

Prepare el binario Linux x64 y su perfil portátil como explica `MESEN_HF15.md`.
El framebuffer observado mide 224×157; omita `--normalize-wonderswan`.
Tras generar privadamente `HF16_PRIVATE.ws` desde la ROM japonesa:

```bash
bash scripts/prepare_mesen.sh --zip /ruta/Mesen_2.1.1_Linux_x64.zip --dest /ruta/mesen-2.1.1
bash scripts/preview_rom.sh --mesen /ruta/mesen-2.1.1/Mesen --rom /ruta/HF16_PRIVATE.ws --lua /ruta/proyecto/source/qa_ending_25.lua --output /ruta/ending.png --timeout 55
bash scripts/preview_rom.sh --mesen /ruta/mesen-2.1.1/Mesen --rom /ruta/HF16_PRIVATE.ws --lua /ruta/proyecto/source/qa_cast_complete.lua --output /ruta/cast.png --timeout 60
QA_END=10800 QA_CONTINUE=1 bash scripts/preview_rom.sh --mesen /ruta/mesen-2.1.1/Mesen --rom /ruta/HF16_PRIVATE.ws --lua /ruta/proyecto/source/qa_gameover_probe.lua --output /ruta/gameover.png --timeout 60
```

Ejecute desde la carpeta de `mesen_visualization_source_v1.1.0`. El final y
las tarjetas usan `SYNTHETIC_STATE` (RAM `0x0134` en frame 180). La ruta de
GAME OVER usa `SCRIPTED_NATURAL`: START para abrir menú, DOWN/A para NEW GAME,
sin mover a Arthur; pulsación A en CONTINUE al frame 9900. La ROM puede crear
un archivo de guardado por nombre en el perfil Mesen: aísle el perfil si
necesita cifras iniciales de estadísticas reproducibles. Esta prueba no
certifica guardado y carga en frío.
