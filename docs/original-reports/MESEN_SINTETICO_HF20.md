# Repetir la exploración sintética en Mesen 2.1.1

Con Mesen, `mesen_visual.py` y una ROM privada JP o HF20 reconstruida, desde la raíz del paquete:

```bash
python3 source/run_synthetic_modes_hf20.py \
  --rom /ruta/ROM_JP_o_HF20.ws \
  --mesen /ruta/Mesen \
  --visual /ruta/mesen_visual.py \
  --output /ruta/capturas \
  --jobs 2
```

El ejecutor exige uno de los dos SHA-256 conocidos. Una prueba breve usa `--modes 0,5,10,17`. Mantener salidas JP y HF20 en carpetas distintas. El script Lua `source/qa_synthetic_modes_hf20.lua` pulsa START, DOWN y A, escribe modo en `0x1B74` y estado `0x0170` en `0x1E33` al f3400; registra f3400/3440/3500/3600/3800/4200 y PNG 224×157. `MODE_SURVEY.json` incluye la traza.

Para los diálogos, usar el capturador Mesen con `source/qa_story_extended_hf20.lua` y `QA_STATE=896` (`0x0380`) o `QA_STATE=944` (`0x03B0`), repetido con ambas ROMs. Este Lua registra f240/600/900/1200/1500/1800/2100/2500/3000. `source/qa_graphical_synthetic_hf20.py` verifica las capturas ya incluidas y recompone las hojas de contacto y `GRAPHICAL_SYNTHETIC_RECORD.json` (requiere Pillow).

El acceso es `WRAM_POKE` + `SYNTHETIC_STATE`, no una ruta de juego natural; el guardado en frío y Stage Clear siguen pendientes. No se usó un savestate ni se probó persistencia.
