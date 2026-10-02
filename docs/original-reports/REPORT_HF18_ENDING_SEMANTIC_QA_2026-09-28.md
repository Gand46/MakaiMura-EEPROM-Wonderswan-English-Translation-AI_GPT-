# Makai-Mura WonderSwan — HF18, corrección lingüística del final

Fecha: 2026-09-28 UTC. Destino EN-US. **Build de desarrollo, no RC.** Continúa HF17 a partir de la ROM japonesa limpia; las capturas japonesas y de ambos builds son registros reales de Mesen con entrada sintética a la escena.

## Hallazgo y traducción

La comparación de las 25 pantallas japonesas confirmó que el final describe el derrumbe del castillo junto con la **ambición** de Azagol (`野望`), y que Arthur y la princesa se dirigen hacia la **capital** (`都`). HF17 decía `ITS SHADE` y `HEADED HOME`, que cambiaban ambos sentidos. HF18 sustituye cinco entradas del recurso del final:

| Línea | HF17 | HF18 | Resultado |
| ---: | --- | --- | --- |
| 15 | `THE DARK KEEP` | `HIS KEEP FELL` | Identifica la caída del castillo sin atribuirle oscuridad literal. |
| 16 | `AND ITS SHADE` | `HIS AMBITION` | Recupera la ambición de Azagol. La línea 17 continúa `CRUMBLED AWAY`. |
| 21 | `ARTHUR AND` | `ARTHUR WENT` | Mantiene al protagonista en el cierre. |
| 22 | `THE PRINCESS` | `WITH HER TO` | El pronombre remite a la princesa mostrada y mencionada en la escena; expresa desplazamiento conjunto. |
| 23 | `HEADED HOME.` | `THE CAPITAL.` | Recupera el destino de la frase japonesa. |

`ARTHUR WENT / WITH HER TO / THE CAPITAL.` condensa el detalle japonés de las personas que esperaban en la ciudad. Ese matiz sigue pendiente de una eventual ampliación de la caja de texto; no se declara equivalencia literal completa. `CLOUDS PARTED` también comprime la transición desde el castillo cubierto de nubes a la luz del sol. No hay texto japonés visible en las 25 capturas inglesas, pero esto no cierra el censo de todo el juego.

## Integridad binaria

| Componente | Resultado |
| --- | --- |
| ROM japonesa limpia | 2,097,152 bytes; SHA-256 `ac0c793b30d2de19ff6504d5a205e33f42aeeac724e7c284b48f48fbfbe53ed8` |
| HF17 previo | SHA-256 `90cc07da4db2909d47f131134564d3b1b796823f16f1d30200b17d9059f10715` |
| HF18 | SHA-256 `0ee826c9d1c98b3b2e02a525dd9a089a961be48e0cea5c9a2d55b8421e807c25` |
| BPS acumulativo JP→HF18 | SHA-256 `a0528929f8d92c9832e134d8f364b535acbfa4568122024c3cf0b03796a6ffa6`; 28,140 bytes |
| Checksum WonderSwan | `0x6426`, almacenado y recalculado |
| HF17→HF18 | 106 bytes distintos; recurso `E000:D180–D2B9`, byte residual hasta `D2BA` y checksum; offsets inesperados: **0** |

`source/build_phase4w_hf18.py` recompone HF17 con las fuentes anteriores, exige su SHA y la tabla antigua exacta, y sólo entonces escribe las nuevas entradas. La tabla conserva **25 punteros**, las cinco pausas en `4,9,14,20,24`, terminadores y límite de **13 celdas** con el atlas nativo 8×16 sin modificarlo. La nueva tabla termina en `E000:D2B9`, un byte antes de la anterior; el sobrante se rellena `FF`. `source/validate_hf18.py` confirma que no se toca ninguna otra región. El BPS se construyó desde la ROM japonesa y fue reaplicado por `ws_patch_tools.bps.apply` del paquete independiente WS Patch Tools v0.1.1: resultado idéntico byte a byte, rechazo por CRC de una base equivocada.

## Registro gráfico y ejecución

Mesen 2.1.1 Linux x64 (SHA-256 `ae43f1438282aaaff90a009aa8ada648bc5d631b070656285d7de9cbff513b41`) recibió el estado `0x0134` en WRAM en el fotograma 180. El script `source/qa_ending_25.lua` capturó **25/25** entradas de cada ROM JP, HF17 y HF18 en **224×157** píxeles nativos. `evidence/ending_HF18/` incluye las 75 capturas, la hoja `JP_HF17_HF18_ENDING_COMPARISON.png` y `GRAPHICAL_RECORD_HF18.json` con hash y recuento por entrada. El texto revisado aparece legible, sin cortes ni mosaicos espurios centrales, en las capturas nativas. La tipografía y sus glifos son los mismos de HF17; no se editó el atlas.

La comparación píxel a píxel de HF17/HF18 difiere sólo en entradas **15–24**, por persistencia y desplazamiento del texto en pantalla; **cero píxeles fuera de `108<=x<212`** en las 25 capturas. Las entradas 0–14 son idénticas. Los fragmentos en los bordes superior e inferior del desplazamiento ya existen en JP y HF17. La pantalla de controles `0x0171` capturada sintéticamente en HF18 a 157×224 es idéntica byte a byte a HF17 (`evidence/ending_HF18/HF18_CONTROLS_REGRESSION.png`).

| Control de esta iteración | Estado |
| --- | --- |
| `DISCOVERED`, `TRANSLATED`, `INTEGRATED` | PASS para las cinco entradas revisadas del final |
| `RUNTIME_CONFIRMED`, `LINGUISTIC_APPROVED`, `TYPOGRAPHY_APPROVED`, `LEGIBILITY_APPROVED`, `DESIGN_APPROVED`, `VISUAL_APPROVED` | PASS para la lectura y composición observadas en el final sintético; la condensación de “todos esperan” queda registrada |
| `FUNCTIONAL_APPROVED` | PASS para avance de 25 pasos bajo entrada sintética; recorrido natural hasta el final: NOT_VALIDATED |
| Stage Clear, entrada natural al aviso, juego tardío, guardado frío | NOT_VALIDATED |
| `FINAL_APPROVED` global | NOT_VALIDATED; no se promociona a RC |

Se ejecutó `build_hf18.command` en Linux para reproducir build y validador. El `.bat` está incluido para Windows, sin ensayo allí. Tampoco se ejecutó el `.command` en macOS. Ahorro de tokens: no medido.
