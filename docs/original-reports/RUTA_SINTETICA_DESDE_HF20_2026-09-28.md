# Ruta programada desde HF20 — solo verificaciones sintéticas

Este plan sustituye los plazos y compuertas de recorrido completo de documentos históricos. En este entorno, el recorrido completo no se ejecutará ni figura como pendiente. Cada fase usa JP y HF20 desde la misma condición sintética, capturas nativas, traza de estado/consumidor y revisión de tipografía/diseño.

| Orden | Trabajo ejecutable | Cierre comprobable |
| --- | --- | --- |
| 1. Salida de fase | Identificar en Mesen el banco activo y una condición real de final de tramo o jefe. Inyectar esa condición **antes de su lectura**, registrar PC/WRAM, transición, selector y pantalla intermedia si existe. Repetir JP/HF20. | Capturas antes/durante/después y cambio de estado causado por el consumidor; clasificar «Stage Clear» explícito, transición sin texto o resto japonés. |
| 2. Variantes | Repetir el disparador confirmado para los modos pertinentes, con checkpoints sintéticos coherentes. | Matriz modo/estado/imagen; cada texto japonés confirmado se traduce y verifica en pantalla. |
| 3. Integridad HF siguiente | Solo si hay cambio binario: reconstruir desde JP, comprobar checksum WS, BPS acumulativo y round-trip, límites gráficos, Mesen y regresión de escenas previas. | Fuentes, `.bat`/`.command`, BPS, manifiesto, gráfica antes/después; sin ROM/BIOS distribuida. |

La inyección directa del selector `0x0132` y de `0x0133` ya está cubierta como control visual de HF20. El intento del objeto tipo `0x44` no activó su consumidor y no se repite sin instrumentación del banco activo. La etiqueta global RC no se infiere de este ensayo.
