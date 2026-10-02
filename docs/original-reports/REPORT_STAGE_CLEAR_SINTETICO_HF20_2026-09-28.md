# Makai-Mura HF20 — prueba sintética del resultado de fase

Fecha: 2026-09-28 UTC. Objetivo EN-US. **HF20 sigue vigente; no hay cambio binario en esta iteración.** JP SHA-256 `ac0c793b30d2de19ff6504d5a205e33f42aeeac724e7c284b48f48fbfbe53ed8`; HF20 SHA-256 `885eb8268ad8594c1ee5e229db22b0f639da5498a22f262e0d4c0884a1401b51`.

## Ejecución y resultado

Mesen 2.1.1 arrancó con START/DOWN/A. En f3400 se inyectó el modo 17 y, por separado, los estados `0x0132` y `0x0133` en WRAM `0x1E33`. En JP y HF20 ambos estados convergieron respectivamente a `0x0032` y `0x0033`. El primero muestra el selector `STAGE / AREA / GO! / EXIT` (modo 17 muestra `STAGE 7`, `AREA A`); el segundo comienza con una animación de paisaje y personaje que continúa hacia los créditos, confirmada después hasta f24000. Se compararon siete fotogramas nativos 224×157 por estado (f3420, 3480, 3540, 3660, 3900, 4300 y 4800): **14 pares JP/HF20 idénticos píxel a píxel**, sin solapamiento ni japonés visible en estas capturas. `evidence/synthetic_stage_clear_HF20/JP_HF20_STAGE_RESULT_CONTACT.png` y los JSON guardan el registro gráfico y la traza.

Se hizo además un barrido de los 18 modos `0x00–0x11` con inyección `0x0180`, de f3400 a f4800. Solo el modo `0x05` cambió al estado `0x0111` y después al modo `0x06`; los demás volvieron a juego (`0x0080`), con pasos transitorios por `0x0070` en varios modos. Esto **no equivale** a completar 18 fases ni demuestra una pantalla independiente de «Stage Clear». `STATE_0180_SWEEP.json` conserva cada transición.

Para probar un disparador de salida, se puso un objeto activo de tipo `0x44` en `0x1BA4`, tipo en `0x1BB5` y posición `0x1BAC` al lado del actor, después de inicializar juego. Se repitió en modo 0 con subestados 1, 2 y 4, con un paso por `0x0070`, y en modo 17. El objeto permaneció en RAM; **no se registró lectura de `0x1BB5` ni transición de fase atribuible a ese objeto**. En subestados 2/4 apareció después `0x0111`, consistente con otra ruta de juego, por lo que no se atribuye al marcador. Las trazas `EXIT_MODE*_TRACE.json` permiten auditar el intento fallido. No se alteró la ROM para este sondeo.

## Estado de calidad

| Criterio | Resultado |
| --- | --- |
| Selector de fase `0x0132` e inicio de créditos `0x0133`, JP/HF20, 14 pares | PASS **sintético y visual** para las ventanas observadas |
| Japonés residual y composición en esas ventanas | Ninguno visible; pantallas coincidentes y sin error de diseño detectado |
| Disparador real de fin de fase y posible pantalla independiente «Stage Clear» | **NO VALIDADO**: la inyección del objeto no alcanzó el consumidor |
| Traducción o parche nuevo | N/A: ningún resto japonés confirmado en las superficies observadas; se conserva el BPS acumulativo HF20 |
| Recorrido completo en este entorno | **FUERA DE ALCANCE**, no es un pendiente ni una condición de cierre de esta etapa; sustituido por pruebas sintéticas acotadas |
| Aprobación global / RC | No otorgada por esta prueba parcial |

La próxima prueba debe verificar el banco ejecutado al entrar en juego, observar una lectura del marcador o el evento de jefe en el punto de consumo y capturar JP/HF20 desde antes del cambio de estado hasta el selector. No se debe etiquetar `Stage Clear PASS` con la inyección directa a `0x0132`. Este informe prevalece sobre las rutas históricas que proponían un recorrido completo en este entorno.

Fuentes de reproducción: `source/qa_stage_clear_probe.lua`, `source/qa_stage_exit_object.lua`, `source/qa_stage_intro_frames.lua`, `source/build_stage_clear_record.py`. Los recursos históricos del paquete siguen para trazabilidad. El ZIP no incluye ROM ni BIOS; el BPS HF20 sigue siendo el parche acumulativo.
