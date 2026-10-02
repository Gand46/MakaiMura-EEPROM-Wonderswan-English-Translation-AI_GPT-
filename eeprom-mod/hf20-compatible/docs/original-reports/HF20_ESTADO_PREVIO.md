# Makai-Mura — auditoría de compuerta RC en una iteración

Fecha UTC: 2026-09-28. Destino EN-US. **Decisión: HF20 sigue como build de desarrollo verificable; no se declara RC.** La ROM no se modificó en esta iteración y no se fabrica un HF21 ni un BPS nuevo. El BPS acumulativo JP→HF20 permanece vigente.

## Base e integridad

| Control | Resultado |
| --- | --- |
| JP original, 2 MiB | SHA-256 `ac0c793b30d2de19ff6504d5a205e33f42aeeac724e7c284b48f48fbfbe53ed8` |
| HF20 reconstruido | SHA-256 `885eb8268ad8594c1ee5e229db22b0f639da5498a22f262e0d4c0884a1401b51` |
| BPS acumulativo directo | SHA-256 `3fc350fd39cd1c15608c4e9e791487b9d2f8aa535a73482472e11d4c337a796a` |
| `source/validate_hf20.py` | PASS: build, reaplicación BPS byte a byte, checksum WS `0x5962`, diferencias permitidas |

## Censo de fuentes de texto comprobadas

`source/audit_active_e000_hf20.py` siguió cinco instrucciones `mov si` consumidoras, sus selectores de atlas, 241 punteros, límites, terminadores y tokens. Las tres tablas narrativas se cotejaron con las líneas inglesas exactas del builder. Los 13 registros de reparto solo usan sus nombres latinos activos, más la línea original de medidas de la princesa; las lecturas fonéticas japonesas fueron retiradas en HF14. El atlas del quinto grupo se inspeccionó gráficamente y contiene signos latinos; su tabla de 165 entradas es la de créditos.

| Familia | Tabla / consumidor ROM | Entradas | Resultado |
| --- | --- | ---: | --- |
| Rescate | `E000:CD80` / `0x14594C` | 23 | Tokens y líneas inglesas integradas |
| Variante | `E000:CF80` / `0x145B4B` | 15 | Tokens y líneas inglesas integradas |
| Final | `E000:D180` / `0x145F30` | 25 | Tokens y líneas inglesas integradas |
| Reparto | `E000:0579` / `0x1460A8` | 13 | Códigos japoneses inactivos; nombres latinos activos |
| Créditos | `E000:06F5` / `0x146729` | 165 | Atlas latino; 165 punteros y códigos válidos |

**Japonés activo confirmado pendiente en estas cinco tablas: 0.** Es un denominador de 241 entradas estructurales, incluidas pausas, no el universo completo de cadenas y gráficos del juego. El barrido CP932 bruto generó 1.905 candidatos HF20 en datos binarios, mayormente patrones de mosaicos; no se presenta esa cifra como texto japonés ni se le asigna traducción sin consumidor. `qa/sjis_candidates_hf20.json` conserva los candidatos y el método.

## Mesen 2.1.1 y revisión visual

- Matriz de 30 estados inyectados en f180, JP y HF20: 60 ejecuciones completadas; 120 pares en f240/360/600/900. **54 pares idénticos y 66 con diferencias** de gráficos o texto; `STATE_MATRIX_30_STATES.json` documenta cada caja de diferencias y estado alcanzado. En las superficies seleccionadas se leen ERASURE, CONTINUE, STAGE, INDEX, ARTHUR, detalles y diálogos sin recorte significativo. La inyección aislada `0x016B` carece de VRAM contextual y dibuja mosaicos corruptos también en JP; no se confunde con una ruta válida ni se usa para aprobarla.
- Los créditos **sí** continúan desde `0x0133`: 40 pares JP/HF20 cada 600 fotogramas hasta f24000, todos idénticos píxel a píxel. En f1200–14400 se ven cargos y nombres latinos; desde f15000, la imagen `The End`. `JP_HF20_CREDITS_40_FRAMES.png` documenta el recorrido. Se corrige la clasificación anterior de `0x0133` como mera tarjeta de fase: sus primeros fotogramas lo parecían, pero la ejecución extensa demuestra los créditos.
- A, P, R y W de la fuente 8×16 nativa tienen bytes idénticos en JP y HF20; `NATIVE_APRW_GLYPHS.png` ofrece inspección directa. Las capturas `HF20_12_SURFACES_CONTACT.png` permiten comprobar a tamaño nativo el diseño de doce superficies. Las escenas de rescate/final y las tarjetas de reparto conservan la evidencia sintética específica de HF18/HF20 incluida en este paquete; el muestreo global no sustituye lectura a ciegas de cada glifo en todas las páginas.
- **Guardado en frío acotado PASS**: con una copia privada aislada de HF20, la ruta natural de juego alcanzó tres muertes y `CONTINUE?` a f9600. Se cerró Mesen y se inició un proceso nuevo con el guardado del cartucho: ARTHUR mostró `DEATHS 000003` frente a `000000` inicial. Se entregan capturas, traza y `.sav`/`.ieeprom` de prueba. Esto demuestra la persistencia del contador; no examina cada flag del juego.

## Decisión de compuertas

| Compuerta | Estado | Motivo |
| --- | --- | --- |
| Integridad, checksum, build, BPS acumulativo | PASS | Reproducción HF20 y hash verificados |
| Tablas activas `E000` conocidas | PASS en 241 entradas | Cinco consumidores y atlas verificados; créditos runtime |
| Fuente nativa y diseño de las pantallas representadas | PASS acotado | Glifos idénticos y capturas nativas revisadas |
| Persistencia del contador de muertes tras arranque frío | PASS acotado | Dos procesos, antes/después y guardado real |
| Salida de fase / pantalla independiente «Stage Clear» | **NOT_VALIDATED** | El ensayo del marcador tipo `0x44` no activó al consumidor; inyectar `0x0132` muestra el selector pero no causa el evento |
| Censo estructural completo de otros atlas, gráficos y rutas | **NOT_VALIDATED** | Las 241 entradas son un subconjunto demostrado; no hay denominador global defendible |
| Revisión lingüística y reconocimiento independiente del contexto global | **NOT_VALIDATED** | Cobertura visual y semántica representativa, no exhaustiva |
| `FINAL_APPROVED` y etiqueta RC | **NO** | Las reglas v1.5 bloquean RC con compuertas obligatorias `NOT_VALIDATED` |

El recorrido completo manual queda **fuera de alcance en este entorno y no figura como pendiente**. Las compuertas abiertas requieren instrumentación y capturas sintéticas dirigidas: observar el banco y la condición leída por el consumidor de fin de fase, cubrir sus variantes y ampliar el censo de gráficos con texto. No se atribuye ausencia universal de japonés a los 40 fotogramas de créditos ni al barrido CP932. Ahorro de tokens: no medido.

El paquete contiene fuentes acumulativas, BPS HF20, scripts de reproducción, manifiesto y registros gráficos. No contiene ROM ni BIOS.
