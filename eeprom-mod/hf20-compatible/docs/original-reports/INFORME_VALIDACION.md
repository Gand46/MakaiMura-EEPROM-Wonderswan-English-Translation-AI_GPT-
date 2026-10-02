# HF20 + EEPROM v1: integración y validación

Reconstrucción y nueva ejecución: 29 de septiembre de 2026 en Bogotá (30 UTC). La interrupción anterior borró archivos temporales; se recuperaron las fuentes originales y se reconstruyó exactamente el mismo destino ya registrado en el historial. Las evidencias de este paquete se generan de nuevo, no se presentan como archivos recuperados de aquella sesión.

## Corrección

El mod EEPROM r2 y HF20 comparten base JP, pero el código de EEPROM antiguo pisa `0x14FC90–0x14FF51`, usado por traducción: 547 bytes solapados, 536 valores incompatibles. El BPS antiguo rechaza HF20 por CRC; forzar su aplicación destruiría esos recursos.

Se trasladó el principal a `5000:E200`, manteniendo los 127 selectores del espejo SRAM, los cinco hooks y la lógica diferencial r2. Adaptadores conservan el segmento original de las llamadas nativas y la correspondencia CALL/RET y CALL FAR/RETF.

| Recurso añadido | Rango ROM | Bytes |
| --- | --- | ---: |
| Principal con adaptadores locales | `15E200–15E591` | 914 |
| Extensión OPTIONS | `15DF38–15E0D4` | 413 |
| Adaptadores en banco nativo | `14FF60–14FF97` | 56 |

Todas las zonas eran FF en HF20. Precondiciones, banco y límites se comprueban antes de escribir. **23.378 bytes modificados por la traducción preservados, cero sobrescritos**. La integración difiere en 1.624 bytes frente a HF20, incluido el checksum, todos previstos. No se modifican las rutinas nativas de teclado/render/inicialización, sólo sus puntos de conexión.

El espejo nativo contiene 645 bytes en WRAM `0370–05F4`; la transferencia usa 646 bytes con padding. Controles del mod en `05F6–05FF`. Tamaño ROM: 2.097.152 bytes; save type `20`; checksum **5D3B**.

## Identidad y reproducción

| Componente | SHA-256 |
| --- | --- |
| JP | `ac0c793b30d2de19ff6504d5a205e33f42aeeac724e7c284b48f48fbfbe53ed8` |
| HF20 | `885eb8268ad8594c1ee5e229db22b0f639da5498a22f262e0d4c0884a1401b51` |
| EEPROM r2 original | `f5652123b1eee5541a4c761c4818e4872a1ca9f00ce7c106708ee7d5f7044217` |
| Integración vigente | `abd2440a261dfd8aa1a01f215c829ea08617536e48909c9be54dbe26e6c4b713` |
| BPS desde JP | `bf4742141bbf7f9427c9430aa653d8b92fc83028547af3cb64d7b576a599254f` |
| BPS desde HF20 | `ecd8296f46be822e400adab0aeb9552c5605d828fb2b3c99c56a3e594f91c2fe` |

Se reconstruyen primero las fuentes HF20, se ensamblan los bloques EEPROM y se aplican precondiciones explícitas. Los BPS se reaplican con verificador independiente y deben producir los mismos bytes. Entradas incorrectas, un bit cambiado, BPS truncados/corruptos se rechazan. `RELEASE_VERIFICATION.json` registra la reconstrucción desde una extracción limpia. No se exige una cadena de parches al usuario.

## Runtime y persistencia

Mesen 2.1.1 Linux x86_64, SHA `ae43f1438282aaaff90a009aa8ada648bc5d631b070656285d7de9cbff513b41`, perfil `{}`, `--testRunner`, Lua, libstdc++ del host. Cada ejecución usa copias aisladas. GNU binutils/Python para construcción; Pillow para igualdad gráfica. Los logs incluyen las advertencias nativas de memoria no inicializada; no se usa un núcleo modificado para ocultarlas.

La batería definida contiene **55 ejecuciones**, verificadas por `validation/verify_results.py`; resultados actuales en `VALIDATION_SUMMARY.json` y `evidence/runtime/`.

| Caso | Evidencia y criterio |
| --- | --- |
| Migración SRAM HF20 | Conversión no destructiva; carga de los mismos 645 bytes, cero escrituras al arrancar. |
| SAVE | START corto reanuda sin escribir; HOLD escribe, permanece pausado y deja diff=0. Segundo HOLD sin cambios: cero escrituras adicionales. Primer fixture: 16 accesos de byte en Mesen, no una medida de ciclos eléctricos. |
| Cancelación/ERASE | B cancela sin modificar EEPROM y restaura OPTIONS píxel por píxel. START corto, teclas mixtas y A antes de liberar START no borran. YES reinicia el registro. Primer borrado: 36 comandos de palabra/72 accesos de byte; segundo: cero adicionales. Cola `0285–07FF` conservada. |
| EEPROM nueva | Ceros/FF inicializan sólo RAM; no se graba al arrancar. Primer SAVE desde FF persiste y conserva la cola no usada. |
| Compatibilidad r2 | Se genera un guardado con r2 reconstruida y se carga con HF20+EEPROM. El SAVE del mismo fixture produce EEPROM idéntica en ambas. |
| Seis cargas frías | SAVE, ERASE, r2, primer SAVE FF, modo tardío y selección Tip 10: procesos cerrados/reabiertos, 645 bytes idénticos, cero escrituras al cargar. No son pruebas con savestates. |
| CONTINUE explícito | HF20 y EEPROM, con datos equivalentes, llegan al mismo estado/modo y render. Sólo se añade el mensaje previsto en pausa. |
| OPTIONS y Tips | Valores, botones y EXIT preservados. A/B/direcciones no activan SAVE. Tip 10 se desbloqueó únicamente en una copia del fixture (bit1 de 022B) para recorrer su consumidor nativo. |
| Escenas | Índice inicial y desplazado; biblioteca; orientación; aviso de enemigos; diálogos; 25 entradas del final; créditos completos hasta f24000; modos 00/0A/11. |

Las escenas forzadas y el desbloqueo del fixture son **PASS_SYNTHETIC** en su alcance. Menús mediante botones: SCRIPTED_NATURAL. Seis comprobaciones de archivo más nuevo proceso acreditan persistencia real en Mesen. No se afirma progreso natural completo.

Los casos heredados `continue_saved/late/checkpoint` sólo comprueban entrada al juego y pausa con su secuencia rápida. La selección explícita de CONTINUE se prueba en `actual_continue_checkpoint` frente a `actual_continue_hf20`. Abrir un modo por WRAM o elegir Stage 2 con Tip 10 no certifica un checkpoint ordinario nuevo: con esos datos, ambos builds vuelven a Stage 1-A. El mod conserva el comportamiento nativo; no guarda la posición exacta de un savestate.

En la sesión interrumpida hubo un fallo de temporización del script al pulsar START durante una transición. Se conservó la lección: la prueba de selección de fase ahora espera el estado de pausa y libera START antes de mantenerlo. No se vuelve a contabilizar el intento perdido como ejecución nueva ni como PASS.

## Regresión visual

El verificador compara **132 pares sin diferencias** en el área completa del juego. Excluye sólo la barra de Mesen: 224×144 horizontal o 144×224 vertical, sin perder la parte inferior de las imágenes verticales. No cuenta duplicados finales. La diferencia intencional de pausa se limita a `x92–131,y120–127`.

Las capturas nativas permiten revisar `SAVED`, `ERASE SAVE`, `A YES / B NO` y `DONE`, construidos con glifos propios del juego; se conservan los cuatro renglones, valores y marco de OPTIONS. La evidencia de traducción se compara en los mismos fotogramas que HF20. Una animación parcialmente desplegada e idéntica no se convierte en aprobación global nueva de legibilidad. `evidence/RESUMEN_GRAFICO.png` reúne capturas reales, sin repintado.

## Alcance de la aprobación

Integridad, checksum, fuentes acumulativas, BPS, persistencia ensayada y regresión: **PASS en el alcance registrado**. Escenas inyectadas: **PASS_SYNTHETIC**. La igualdad de todos los bytes traducidos y las capturas probadas no equivale a garantía absoluta sobre cada evento del juego.

Cartucho físico, apagado durante escritura y desgaste: **NOT_VALIDATED**. Se hereda el driver r2 sin journal ni atomicidad; un timeout no muestra error, por lo que SAVED/DONE no constituye read-back de hardware. En Mesen sí se verificaron los bytes escritos y la carga posterior. No apagar durante SAVE/ERASE.

HF20 conserva sus compuertas globales de Stage Clear y censo completo; esta integración no declara RC global ni añade recorrido manual completo como pendiente. No hay ROM/BIOS/emulador en el paquete. Ahorro de tokens: no medido.
