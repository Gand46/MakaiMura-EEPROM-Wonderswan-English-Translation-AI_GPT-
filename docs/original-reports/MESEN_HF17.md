# Mesen HF17 — reproducción de las evidencias gráficas

Mesen 2.1.1 Linux x64 y el paquete `mesen_visualization_source_v1.1.0` se usan con perfil portátil y `--testRunner`. Se requiere la ROM japonesa exacta indicada en `README.md`; compile HF16 y HF17 privadamente con los lanzadores o con sus constructores Python. El script Lua `source/qa_state_survey.lua` lee `QA_STATE`, `MESEN_CAPTURE_PATH` y `MESEN_LUA_REPORT`.

Ejemplo desde el directorio que contiene `mesen_visualization_source_v1.1.0`, Mesen, ROMs privadas y este proyecto (ajuste rutas según corresponda):

```bash
QA_STATE=369 python3 mesen_visualization_source_v1.1.0/scripts/mesen_visual.py capture --mesen mesen-2.1.1/Mesen --rom HF17_PRIVATE.ws --lua source/qa_state_survey.lua --output controls_hf17.png --timeout 25
```

El script introduce `0x0171` en WRAM `0x1E33` al fotograma 180 y captura en 240, 360, 600 y 900. Para la salida con A, use `source/qa_171_exit.lua`; pulsa A en 960–965 y captura 900, 1000 y 1300. Para el menú con entradas naturales programadas use `source/qa_start_route.lua`. El `qa_graphical_records_hf17.py` genera una hoja suplementaria sin reescalar las capturas originales y registra el diff en píxeles; requiere Pillow. Todas las capturas y resultados de esta entrega están en `evidence/controls_HF17/`.

Las capturas son 157×224 para el aviso en modo vertical; no se normalizan a 224×144. La secuencia del menú usa orientación horizontal 224×157. El programa Mesen adjunto es Linux x64: el `.command` de macOS sólo reconstruye la ROM con Python, no ejecuta ese ELF.
