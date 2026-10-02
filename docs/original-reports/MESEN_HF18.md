# Mesen 2.1.1 — reproducción HF18

Aplica el BPS a la ROM japonesa de SHA-256 `ac0c793b30d2de19ff6504d5a205e33f42aeeac724e7c284b48f48fbfbe53ed8`, o ejecuta `build_hf18.command` / `BUILD_HF18.bat` con esa ROM privada. El resultado debe tener SHA-256 `0ee826c9d1c98b3b2e02a525dd9a089a961be48e0cea5c9a2d55b8421e807c25`. No se incluye la ROM.

Con el Mesen Linux x64 2.1.1 suministrado, `settings.json` portátil `{}`, el capturador `mesen_visualization_source_v1.1.0/scripts/mesen_visual.py` y `source/qa_ending_25.lua`:

```sh
python3 mesen_visual.py capture --mesen /ruta/Mesen --rom /ruta/HF18_PRIVATE.ws --lua source/qa_ending_25.lua --output /ruta/hf18_ending.png --timeout 45
```

La secuencia introduce **sintéticamente** el estado `0x0134` en el fotograma 180, y guarda las 25 entradas `hf18_ending.png.line00.png`…`line24.png`. Son capturas reales del emulador, 224×157, pero no prueban llegar al final jugando. `source/qa_graphical_records_hf18.py` genera las capturas comparativas y el censo de píxeles de los tres builds. La pantalla de controles se capturó con `source/qa_state_survey.lua`, `QA_STATE=369`, a 157×224; idéntica a HF17.

El `.command` se ejecutó en Linux para un ensayo de build. No se ha ejecutado en macOS ni se ha ejecutado el `.bat` en Windows en este entorno.
