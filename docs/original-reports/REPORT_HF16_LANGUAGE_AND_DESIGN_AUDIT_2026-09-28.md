# Makai-Mura WonderSwan — auditoría y corrección HF16

Fecha: 2026-09-28. Traducción EN-US. **Build de desarrollo, no RC.**

## Base y cambio

La ROM japonesa limpia tiene 2.097.152 bytes y SHA-256
`ac0c793b30d2de19ff6504d5a205e33f42aeeac724e7c284b48f48fbfbe53ed8`.
HF15 reconstruido coincide con SHA-256
`448113002b885d24d1b39d41bbfb35c77f9d961befb5c67777b9afa367d45456`.

Al comparar el japonés del final (tabla original `E000:0458`, 25 entradas) con
HF15, el pasaje 10–13 sustituyó **魔界** (reino demoníaco) por el genérico
“EVIL”, y repitió “YET STILL”. El pasaje 15–19 interpretó nubes y sombra
como “VEIL OF NIGHT” e introdujo “FIRST SUNLIGHT”. El original describe el
castillo envuelto en nubes, su derrumbe con la sombra remanente y el sol que
ilumina el lugar. Estas adiciones no están respaldadas por el japonés.

HF16 modifica únicamente los renglones 10, 11, 13 y 16–19 del recurso
`E000:D180–D2BA`. Los cambios principales son:

| Pasaje | HF15 | HF16 |
| --- | --- | --- |
| Duda sobre el reino | `EVIL MAY YET / STILL REMAIN. / I PRAY THIS / PEACE LASTS.` | `DEMON REALM / MAY REMAIN. / I PRAY THIS / PEACE ENDURES` |
| Castillo y luz | `THE DARK KEEP / AND THE VEIL / OF NIGHT FELL / AS THE FIRST / SUNLIGHT CAME` | `THE DARK KEEP / AND ITS SHADE / CRUMBLED AWAY / CLOUDS PARTED / THE SUN SHONE` |

Se conservan 25 punteros, las pausas 4, 9, 14, 20 y 24, la cuadrícula nativa
8×16, el atlas latino del juego y el límite de 13 celdas. “CLOUDS PARTED”
condensa la desaparición de las nubes antes de que el sol ilumine el lugar;
el inglés final no reproduce literalmente todos los matices de tiempo y
permanencia. La primera estrofa aún condensa la fuerza oculta del brazalete
y el título de Azagol, y la última resume la capital donde aguardan los demás
como `HOME`: revisión lingüística integral pendiente.

La anterior memoria HF15 afirmó **277** bytes de diferencia con HF14; la
reconstrucción y validador sobre la base verificada cuentan **276**. Se
conserva el informe histórico y se registra aquí la corrección documental.

## QA real en Mesen 2.1.1 Linux x64

Mesen ELF SHA-256
`ae43f1438282aaaff90a009aa8ada648bc5d631b070656285d7de9cbff513b41`,
perfil `settings.json` igual a `{}`; framebuffer **224×157**.

| Superficie | Método y resultado |
| --- | --- |
| Final HF16 | `SYNTHETIC_STATE`: inicialización `0x0134` en frame 180; 25/25 entradas capturadas en `evidence/HF16_ending_line00–24.png`. En las capturas de líneas 14 y 20 se leen, respectivamente, `DEMON REALM / MAY REMAIN. / I PRAY THIS / PEACE ENDURES` y `THE DARK KEEP / AND ITS SHADE / CRUMBLED AWAY / CLOUDS PARTED / THE SUN SHONE`. No se observa desbordamiento horizontal ni mosaicos espurios centrales. Los fragmentos transitorios del scroll en los bordes se mantienen como en HF15 y la ROM japonesa. |
| Tarjetas de reparto | `SYNTHETIC_STATE`: 13/13 capturas HF16, comparadas byte por byte con HF15 en los mismos frames: **0 diferentes**. |
| GAME OVER y CONTINUE | `SCRIPTED_NATURAL`: desde título, `DOWN` y `A` para NEW GAME, sin movimiento posterior. Estado `0x0112` hacia frame 9000 y menú `0x0035` en frame 9600. Las capturas JP y HF16 de ese menú son idénticas byte por byte (SHA-256 `2863ccec88abebb01b833435723ee2c2e67e261019f9bb5b328e7f0a6fbc1c89`). `A` en frame 9900 reinicia la partida: estado `0x0070` a 10200 y `0x0080` a 10800. El menú original ya muestra `CONTINUE? / EXIT` en inglés, sin japonés observado en esta ruta. |
| ARTHUR y USE PASSWORD | `SCRIPTED_NATURAL`: ambos rótulos se leen en capturas HF16. La región de 112×32 píxeles del encabezado ARTHUR y la región 44,42–176,84 de USE PASSWORD son idénticas a HF15. Las estadísticas numéricas de Arthur variaron por el archivo de guardado que Mesen mantuvo durante las pruebas. La cabecera ornamental derecha también aparece irregular en la ROM japonesa; requiere análisis de tilemap para atribuirla, sin aprobarla ni cambiarla a ciegas. |

Las capturas de Mesen muestran el render real. La prueba sintética del final
no demuestra progresión natural hasta él. Las revisiones de lectura aquí son
visuales a escala nativa, sin OCR. Una transcripción a partir de capturas
conocidas no equivale a un ensayo ciego formal de todos los glifos; queda
abierto el control global de reconocimiento independiente del contexto.

## Integridad y estados

| Control | Resultado |
| --- | --- |
| Build HF16 SHA-256 | `1be7103b2c0c5c4577a89706560115196357c8b43db35b835e184a459f68b95a` |
| BPS JP → HF16 SHA-256 | `bd2f725cd49bfd51aaaf61e6aeac24560afd0aba02cdff22d1fe88ef10df1c2a` |
| BPS aplicado a otra copia de la base | Idéntico byte por byte, PASS |
| Checksum WS almacenado y recalculado | `0x148B`, PASS |
| Diff HF15 → HF16 | 125 bytes; únicamente recurso `E000:D180–D2BA` y checksum; inesperados 0 |
| 25 punteros, cinco pausas, máximo 13 celdas | PASS |
| Integración y ejecución del pasaje modificado | PASS, acceso sintético |
| Fuente nativa, tamaño y márgenes de los renglones modificados | PASS en el alcance revisado; atlas y consumidor intactos |
| Legibilidad y diseño de renglones 10–20 mostrados | PASS para las capturas revisadas; texto central sin recorte ni superposición |
| Revisión lingüística global, Stage Clear, fases tardías, créditos, guardado en frío, recorrido natural final | NOT_VALIDATED |
| `FINAL_APPROVED` | No; controles obligatorios abiertos |

La validación binaria se reproduce con `source/build_phase4w_hf16.py` y
`source/validate_hf16.py` sobre la ROM original. El BPS acumulativo de HF16 se
aplica **directamente a esa ROM japonesa**. No se distribuye ninguna ROM
comercial o aplicada. Ahorro de tokens: no medido.

## Siguiente trabajo concreto

Trazar el consumidor y la pantalla de Stage Clear, con acceso acotado y
comparación JP/HF16; censar posibles textos japoneses en las transiciones y
créditos. Resolver la cabecera ornamental derecha mediante banco, tilemap y
paleta antes de redibujar. Revisar los matices condensados del final sin perder
sus 25 entradas y pausas, y cerrar el recorrido natural y la persistencia en
frío antes de cualquier RC.
