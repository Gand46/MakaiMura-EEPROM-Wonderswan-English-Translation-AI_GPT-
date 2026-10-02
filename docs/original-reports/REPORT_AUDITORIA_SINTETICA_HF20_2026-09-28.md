# Makai-Mura — auditoría sintética posterior a HF20

Fecha: 2026-09-28 UTC. Idioma objetivo EN-US. **HF20 permanece como build y BPS vigentes; esta iteración no cambió la ROM.** La base JP de 2 MiB es SHA-256 `ac0c793b30d2de19ff6504d5a205e33f42aeeac724e7c284b48f48fbfbe53ed8`; HF20 es `885eb8268ad8594c1ee5e229db22b0f639da5498a22f262e0d4c0884a1401b51`.

## Avance de acceso sintético

Mesen 2.1.1 inicia con START, DOWN y A hasta juego. En el fotograma 3400 el script escribe el modo en WRAM `0x1B74` y reinicializa el estado `0x0170` en `0x1E33`. **Método: `WRAM_POKE` + `SYNTHETIC_STATE`**. Los valores `0x00–0x11` cargan 18 tramos o variantes de juego, no 18 fases únicas demostradas. El modo `0x05` pasa temporalmente por `0x0111` y luego deja `0x06`; `0x0A` tarda más en inicializar. Los demás se estabilizan en `0x0080` dentro de la ventana hasta el fotograma 4200. Ver `MODE_STATE_TRACE.json`.

Se capturaron JP/HF20 en fotogramas **3800 y 4200** para cada modo: **36 pares nativos 224×157**. Los 36 pares son idénticos píxel a píxel. Esta igualdad significa que las aperturas y ventanas observadas no contienen diferencias introducidas por el parche; no demuestra que el resto de cada fase carezca de japonés ni que se haya visto Stage Clear. Los mosaicos `JP_MODES_f4200_CONTACT.png` y `HF20_MODES_f4200_CONTACT.png` registran todas las pantallas. El ejecutor `source/run_synthetic_modes_hf20.py` se probó de nuevo con `0,5,10,17`: sus cuatro capturas f4200 coincidieron byte a byte con el barrido inicial.

## Estados altos y diálogos

Un rastreo de escrituras al estado encontró `0x0265`, `0x0267`, `0x0280`, `0x02B0`, `0x0365`, `0x0367`, `0x0380` y `0x03B0`, ausentes del censo previo. Se inyectaron individualmente al fotograma 180 en JP y HF20. `0x0365→0x0267` y `0x0367→0x0265`; `0x0380→0x0280` y `0x03B0→0x02B0` tras inicializar. Los dos últimos activan diálogos japoneses en JP y su traducción inglesa existente en HF20. Los otros seis estados no presentaron una cadena nueva que traducir en el fotograma 900.

Se ampliaron `0x0380` y `0x03B0` hasta f3000 sin pulsar botones. Las líneas parcialmente visibles en f900 se desplazan como parte de la animación; fotogramas posteriores permiten leer frases completas. En diez pares de fotogramas seleccionados, las diferencias JP/HF20 quedan dentro de la región textual `x=60–171, y=33–111`, con retratos idénticos. Las hojas `JP_HF20_STORY_0380_CONTACT.png` y `JP_HF20_STORY_03B0_CONTACT.png` conservan la comparación; `GRAPHICAL_SYNTHETIC_RECORD.json` registra geometría, bounding boxes y recuentos. La revisión se limita a las líneas vistas, no equivale a certificar todas las ramas narrativas.

## Intento acotado de transición

El código `9000:8837–889E` lleva a la ayuda de orientación `0x0171` si se cumplen coordenadas y condiciones del actor. Desde modo `0x0A`, se probó un poke en f4200. El juego recalculó `0x1B92` de 304 a 288 antes de disparar la rama; otro poke del actor reinicializó `0x0170` con estado de caída. **No se obtuvo Stage Clear ni una ruta normal a orientación**. La condición nueva para repetir es trazar el consumidor y aplicar una inyección en el punto de lectura, o construir un checkpoint anterior coherente; no reiterar las mismas escrituras de fin de fotograma.

| Control | Estado de esta iteración |
| --- | --- |
| Acceso a 18 modos, capturas JP/HF20 y ejecución del barrido | PASS sintético (`WRAM_POKE` + `SYNTHETIC_STATE`) |
| Render de `0x0380/0x03B0` y consistencia visual fuera del texto en los fotogramas elegidos | PASS sintético para el material observado |
| Traducciones nuevas y parche nuevo | N/A: no hubo texto confirmado pendiente en este lote; HF20/BPS permanecen sin cambios |
| Stage Clear, recorrido natural, fases completas, persistencia en frío | NOT_VALIDATED |
| `FINAL_APPROVED` global | NOT_VALIDATED; no RC |

El paquete incluye íntegros los fuentes y el BPS acumulativo HF20, además de los nuevos scripts y registros; no incluye ROM ni BIOS. Ahorro de tokens: no medido.
