# Makai-Mura WonderSwan — HF20, índice del primer libro

Fecha: 2026-09-28 UTC. Traducción EN-US. **Build de desarrollo, no RC.** La base JP y HF19 coinciden con los SHA-256 registrados. HF20 se reconstruye desde JP con todas las fuentes acumulativas.

## Hallazgo y cambio

El barrido de 14 estados adicionales del libro detectó el encabezado `もくじ` (tabla de contenidos) en la entrada `0x0161`. En HF19 los seis mosaicos ya estaban modificados, pero el rótulo resultaba ilegible. La ruta programada normal —menú → biblioteca → izquierda desde la cubierta de Arthur → A— confirmó el defecto en pantalla. HF20 reemplaza ese encabezado por **`INDEX`**, equivalente breve que cabe en la ventana de 48 píxeles de ancho. Los glifos se componen con la fuente latina 8×16 nativa; no se modifica su atlas.

La traza de Mesen vinculó las teselas de pantalla `0x2F50–0x2FA0` y `0x30C0–0x3110` a las fuentes ROM `F000:BBF9–BC58` y `F000:BD69–BDC8`. El builder verifica sus hashes HF19 antes de editar. HF19→HF20 cambia **157 bytes** dentro de esos 12 mosaicos y el checksum, con **0 offsets inesperados**. No se alteran los datos de nombres ni la página derecha.

| Elemento | Resultado |
| --- | --- |
| JP original, 2 MiB | `ac0c793b30d2de19ff6504d5a205e33f42aeeac724e7c284b48f48fbfbe53ed8` |
| HF19 anterior | `a924932e2aac1f3350badb3f82fe946d716a6abd1474e4cbd3bc86214227e22b` |
| HF20 | `885eb8268ad8594c1ee5e229db22b0f639da5498a22f262e0d4c0884a1401b51` |
| BPS acumulativo JP→HF20 | `3fc350fd39cd1c15608c4e9e791487b9d2f8aa535a73482472e11d4c337a796a` (28.938 bytes) |
| Checksum WonderSwan | `0x5962`, almacenado y recalculado |

El BPS aplicado de forma independiente con WS Patch Tools v0.1.1 produce exactamente HF20. Una base alterada fue rechazada por CRC. No se distribuye ROM comercial.

## Registro gráfico y alcance

Capturas nativas **224×157** de JP, HF19 y HF20 en Mesen 2.1.1, ruta normal con entradas programadas, fotogramas **840, 860 y 880**. Los tres alcanzan el estado estable `0x0061` tras inicializar `0x0161`. En cada fotograma, HF19/HF20 difieren en **401 píxeles** confinados a `x=32–79, y=16–28`; **0 píxeles** distintos fuera del encabezado. El rótulo `INDEX` se lee sin recorte y las filas empiezan debajo. Los estados sintéticos vecinos `0x0160`, `0x0162`, `0x0163`, `0x0168` y `0x016B` son idénticos HF19/HF20. Ver `evidence/arthur_index_HF20/JP_HF19_HF20_ARTHUR_INDEX_COMPARISON.png` y `GRAPHICAL_RECORD_HF20.json`.

El barrido comparativo de `0x0135`, `0x0160–0x016B` y `0x0171` conserva sus capturas JP/HF19. `0x016B` dibuja letras repetidas al forzar el estado directamente tanto en JP como en HF19/HF20; falta contexto anterior de VRAM, por lo que no se clasifica como defecto de la ruta normal. Las restantes páginas visibles del barrido ya muestran texto inglés en HF19; el muestreo no demuestra ausencia de japonés en todas las rutas.

| Control | Estado y alcance |
| --- | --- |
| `DISCOVERED`, `TRANSLATED`, `INTEGRATED`, `RUNTIME_CONFIRMED`, `FUNCTIONAL_APPROVED` | PASS para el encabezado y el acceso normal programado a `0x0161` |
| `LINGUISTIC_APPROVED`, `TYPOGRAPHY_APPROVED`, `LEGIBILITY_APPROVED`, `DESIGN_APPROVED`, `VISUAL_APPROVED` | PASS para `INDEX` en esta pantalla y las cinco regresiones observadas |
| Stage Clear, fases tardías, entrada natural al borrado, guardado/carga en frío | NOT_VALIDATED |
| `FINAL_APPROVED` global | NOT_VALIDATED; sigue en desarrollo |

`build_hf20.command` se ejecutó en Linux y produjo una ROM privada idéntica. `BUILD_HF20.bat` no se ensayó en Windows; `.command` no se ensayó en macOS.
