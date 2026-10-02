# Mesen 2.1.1 para HF14

La documentación de `mesen_visualization_source_v1.1.0` fue contrastada con
una ejecución real. El perfil mínimo `settings.json` con `{}` debe quedar
**junto al ELF `Mesen`**. Sin ese perfil se había observado `XOpenDisplay
failed`; con él, `--testRunner` cargó la ROM HF13 y HF14 sin `DISPLAY`.

Desde la carpeta del paquete de visualización suministrado por el proyecto:

```bash
bash scripts/prepare_mesen.sh --zip /ruta/Mesen_2.1.1_Linux_x64.zip --dest /ruta/.tools/mesen-2.1.1
bash scripts/probe_mesen.sh --mesen /ruta/.tools/mesen-2.1.1/Mesen --rom /ruta/HF14_PRIVATE.ws
bash scripts/preview_rom.sh --mesen /ruta/.tools/mesen-2.1.1/Mesen --rom /ruta/HF14_PRIVATE.ws --output /ruta/hf14_boot.png --frame 180 --timeout 30
bash scripts/preview_rom.sh --mesen /ruta/.tools/mesen-2.1.1/Mesen --rom /ruta/HF14_PRIVATE.ws --lua source/qa_force_ending.lua --output /ruta/hf14_ending.png --timeout 45
```

El último Lua modifica temporalmente RAM en la instancia del emulador para
entrar en la rutina final; no modifica la ROM ni equivale a un recorrido
natural. Captura hitos entre los fotogramas 181 y 7000, y termina en 7200.

**Geometría observada:** Mesen produjo PNG válidos de **224×157**, incluyendo
la franja inferior de 13 píxeles. La opción `--normalize-wonderswan` del
paquete de visualización rechazó esa geometría porque su lista admite solo
224×144 o 237×144. Omita esa opción y preserve el PNG 224×157; el proceso
terminó con `passed=true`. No se recortó ni reescaló una captura para acreditar
legibilidad. La hoja `HF14_CAST_NATIVE_FONT_PREVIEW_NOT_RUNTIME.png` es una
composición diagnóstica de los glifos originales, no una captura de Mesen.

El modo GUI no estuvo disponible aquí (sin `DISPLAY` ni Xvfb); no es necesario
para las capturas con `--testRunner`.
