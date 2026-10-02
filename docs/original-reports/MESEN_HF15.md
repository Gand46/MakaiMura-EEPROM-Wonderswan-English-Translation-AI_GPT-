# QA HF15 en Mesen 2.1.1

Prepare el perfil portátil `settings.json` (`{}`) junto al ELF de Mesen con el
paquete `mesen_visualization_source_v1.1.0` suministrado. Ejecute desde la
carpeta de ese paquete:

```bash
bash scripts/prepare_mesen.sh --zip /ruta/Mesen_2.1.1_Linux_x64.zip --dest /ruta/mesen-2.1.1
bash scripts/probe_mesen.sh --mesen /ruta/mesen-2.1.1/Mesen --rom /ruta/HF15_PRIVATE.ws
bash scripts/preview_rom.sh --mesen /ruta/mesen-2.1.1/Mesen --rom /ruta/HF15_PRIVATE.ws --lua /ruta/proyecto/source/qa_ending_25.lua --output /ruta/ending.png --timeout 40
bash scripts/preview_rom.sh --mesen /ruta/mesen-2.1.1/Mesen --rom /ruta/HF15_PRIVATE.ws --lua /ruta/proyecto/source/qa_cast_complete.lua --output /ruta/cast.png --timeout 65
```

Los Lua inyectan solo el estado de entrada `0x0134` en RAM del emulador, desde
el fotograma 180. El primero captura `ending.png.line00.png` a `.line24.png`
en el avance del contador real del juego; el segundo captura
`cast.png.card00.png` a `.card12.png`. Esta ruta sintética no modifica la ROM
y permite reproducir la escena sin recorrer las fases. Consulte los JSON de
`build/` para fotogramas y hashes exactos.

El framebuffer de esta ROM mide **224×157** en Mesen 2.1.1. Omita la opción
`--normalize-wonderswan` de ese paquete: solo admite 224×144 o 237×144.
Se conservaron las capturas nativas completas, sin recorte. Esta prueba no
sustituye un recorrido natural completo ni certifica otras rutas de juego.
