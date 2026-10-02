# Makai-Mura WonderSwan — HF19, aviso de borrado de biblioteca

Fecha: 2026-09-28 UTC. Traducción EN-US. **Build de desarrollo, no RC.** La base japonesa y el build HF18 coinciden con sus SHA-256 documentados; HF19 se reconstruye desde la ROM japonesa original mediante las fuentes acumulativas.

## Descubrimiento y traducción

Un barrido de **28 estados inicializados por separado** en Mesen encontró una confirmación japonesa no traducida al inicializar `0x0110`. Se lee `敵ライブラリーの情報を全て消去してもいいですか？`: pregunta si se puede borrar toda la información de la biblioteca de enemigos. En HF18, la captura es idéntica a JP.

| Texto visible JP/HF18 | Texto HF19 | Ajuste semántico |
| --- | --- | --- |
| `敵ライブラリーの情報を全て消去してもいいですか？` | `ERASE ALL / ENEMY DATA?` | Conserva la confirmación de borrado total y que los datos son de enemigos; el contexto de biblioteca lo aporta el menú. |

`YES` y `NO` eran ingleses y no se modificaron. El texto nuevo se compone en dos líneas de 9 y 11 caracteres/celdas dentro de zonas originales de 12 y 13 celdas. Se reutilizan los glifos latinos nativos 8×16 de la ROM japonesa (`SEGF`) con remapeo de índices de paleta; no se introduce una fuente externa ni se altera el atlas compartido.

## Recurso y aislamiento

La traza de escritura a VRAM al inicializar `0x0110` encontró una copia de **0xEC0 bytes** desde `C000:0405` hasta WRAM `0x2800–0x36BF` por `4000:F985`. El mensaje está horneado en cuatro tramos de ese gráfico: índices de teselas `94–105`, `118–129`, `140–152` y `162–174`, offsets ROM `0x1C09E5–0x1C0AA4`, `0x1C0B65–0x1C0C24`, `0x1C0CC5–0x1C0D94` y `0x1C0E25–0x1C0EF4`. Las rutas muestreadas de Continue `0x0112` y menú `0x0131` usan recursos de origen distintos; esto no pretende probar que ninguna ruta dinámica futura reutilice la región.

Antes de escribir, el builder exige SHA HF18 y cuatro hashes de las teselas japonesas originales, idénticas en JP y HF18. La modificación HF18→HF19 tiene **595 bytes distintos**, todos en esos cuatro tramos y el checksum; `source/validate_hf19.py` encontró **0 offsets inesperados**.

| Componente | SHA-256 / resultado |
| --- | --- |
| JP original, 2 MiB | `ac0c793b30d2de19ff6504d5a205e33f42aeeac724e7c284b48f48fbfbe53ed8` |
| HF18 previo | `0ee826c9d1c98b3b2e02a525dd9a089a961be48e0cea5c9a2d55b8421e807c25` |
| HF19 | `a924932e2aac1f3350badb3f82fe946d716a6abd1474e4cbd3bc86214227e22b` |
| BPS acumulativo JP→HF19 | `b7cc60569242f95881439ab3fa541a350ecd203c122dc98b9c49161ea7194059`; 28,867 bytes |
| Checksum WonderSwan | `0x3955`, almacenado y recalculado |

El BPS directo desde JP se reprodujo byte por byte con `ws_patch_tools.bps.apply` del paquete independiente WS Patch Tools v0.1.1; una base alterada fue rechazada por CRC. No se distribuye ROM comercial.

## Registro visual y función

Mesen 2.1.1 Linux x64, SHA-256 `ae43f1438282aaaff90a009aa8ada648bc5d631b070656285d7de9cbff513b41`, inicializó sintéticamente `0x0110` al frame 180. Las capturas JP/HF18/HF19 de los frames **240, 360, 600 y 900** son nativas **224×157**. JP/HF18 son idénticas. HF18/HF19 difieren en **1.459 píxeles dentro del texto y 0 fuera** en cada frame; el marco, adornos y botones mantienen sus píxeles. La lectura directa a escala nativa confirma `ERASE ALL / ENEMY DATA?` sin recorte. Ver `evidence/enemy_library_erase_HF19/GRAPHICAL_RECORD_HF19.json` y la hoja `JP_HF18_HF19_PROMPT_COMPARISON.png`.

Desde la entrada sintética, pulsar A o B en frames 320–324 lleva ambos builds HF18/HF19 a `0x0030` en frame 360; la captura de salida en frame 600 es idéntica. Esta prueba **no demuestra** el camino natural al aviso ni si YES borra datos; el estado carece del contexto de selección/guardado anterior. Capturas de Continue `0x0112`, menú `0x0131` y orientación `0x0171` a frame 900 son idénticas HF18/HF19.

| Control | Estado y alcance |
| --- | --- |
| `DISCOVERED`, `TRANSLATED`, `INTEGRATED`, `RUNTIME_CONFIRMED` | PASS para el aviso bajo entrada sintética |
| `LINGUISTIC_APPROVED`, `TYPOGRAPHY_APPROVED`, `LEGIBILITY_APPROVED`, `DESIGN_APPROVED`, `VISUAL_APPROVED` | PASS para el texto y composición observados en 224×157; identificación de glifos basada en atlas nativo y lectura directa |
| `FUNCTIONAL_APPROVED` | PASS limitado a salida sintética A/B sin regresión frente a HF18; selección natural YES/NO y persistencia: NOT_VALIDATED |
| Stage Clear, orientación natural, fases tardías, guardado+carga en frío | NOT_VALIDATED |
| `FINAL_APPROVED` global | NOT_VALIDATED; sigue en desarrollo |

El `.command` se ejecutó en Linux para recompilar y validar. El `.bat` no se probó en Windows y el `.command` no se probó en macOS. Ahorro de tokens: no medido.
