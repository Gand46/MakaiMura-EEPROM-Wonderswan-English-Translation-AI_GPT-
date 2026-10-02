# Validación 4.1E-r2 — corrección de OPTIONS

Fecha: 14 de septiembre de 2026. ROM ensayada:
`f5652123b1eee5541a4c761c4818e4872a1ca9f00ce7c106708ee7d5f7044217`.

## A/B visual

Se reprodujo el defecto en la 4.1E anterior usando Mesen 2.1.1 y el dump avanzado.
No se corrigió una captura: se modificó la ROM y se volvieron a capturar sus pantallas.

Ocho capturas en los frames 3680, 3730, 3810, 3860, 3910, 3950, 3990 y 4030 comparan
la ROM original y r2 con la misma secuencia y save lógico. Se ejercitaron LEVEL,
PLAYER y BUTTON CONFIG, incluyendo JUMP/SHOT y START mantenido fuera de EXIT.

**0 píxeles diferentes en cada comparación (224×144, 32.256 píxeles).**
Se excluyen sólo los 13 píxeles verticales de la barra de estado de Mesen, no el juego.

Al cancelar ERASE con B: **0 píxeles diferentes respecto de OPTIONS antes del diálogo**.
En confirmación se muestran dos líneas superiores (y=36 y y=46), sin extender EXIT
hacia abajo ni ocultar los valores nativos. Las capturas son auténticas de Mesen.

## Borrado y cancelación

Fixture avanzado SHA-256:
`95285ceb6032135ec4f894e7095c9c0eb4e14ec6d1ae63fde96ca81af5e9bdfe`.
Se trabaja en COPIAS. El fichero adjunto no se modifica.

- OPTIONS y EXIT normales: 0 comandos de programación EEPROM.
- START corto: 0 comandos; no abre ERASE.
- HOLD START en EXIT: abre confirmación, todavía 0 comandos.
- START sin soltar + A: no acepta YES; exige liberación previa.
- B/NO: 0 comandos; la copia EEPROM coincide byte por byte con el fixture.
- START+A en modo normal: no abre ERASE.
- A/YES después de soltar: reset nativo + 96 comandos de programación de palabra.
- Contador de Mesen: 192 accesos de byte escritos. **No son 192 ciclos físicos**;
  se midieron además las ejecuciones de OUT WRITE en `4000:FDA2`: 96.
- Tras DONE: mirror/EEPROM diff=0.
- Segundo ERASE sin cambios: 0 comandos adicionales; total se mantiene en 96.
- Los bytes EEPROM 0x0285–0x07FF permanecen iguales al fixture.

## Normalización nativa de 0x001B

La rutina original `4000:13AF–13B8` calcula `save[0x001B] = PLAYER - 1` al dibujar
OPTIONS. Por eso un fresh al arranque tiene 0 allí y un fresh ya mostrado en OPTIONS
con PLAYER=3 tiene 2. No es información histórica resucitada.

La primera variante de esta revisión detectó diff=1 después del borrado por ese motivo.
La entrega final hace el commit después de dicha normalización nativa, no antes.

Fresh inmediatamente tras boot, 645 bytes:
`b506329de5725741f30d7054c9a47aa7c86687f493baa7448285e63421bb1b39`.
Fresh normalizado dentro de OPTIONS:
`3e095155411e42a9c01831a7a6721e18dee7ed98ff4f53e5cea686a073fd8a12`.
La única diferencia es 0x001B: 00 → 02. No se afirma que ambos momentos sean idénticos.

Tras cerrar Mesen y volver a abrir la EEPROM borrada, el mirror de 645 bytes coincide
exactamente con el fresh normalizado. El nuevo juego llega a pausa mostrando
**STAGE 1-A / ARTHUR x3**. No se realizó un nuevo SAVE durante esa comprobación.

## Regresiones

START corto en pausa: RETURN, 0 escrituras. HOLD START: guarda, permanece pausado y
mirror/EEPROM diff=0. Segundo HOLD sin cambios: 0 escrituras adicionales.
En la prueba avanzada el primer HOLD registró 22 accesos de byte (no una cifra de
ciclos eléctricos); el total no subió al segundo HOLD.

A/B/ambos grupos direccionales en pausa sin START: no activan SAVE y holdCounter=0.
No se afirma haber probado individualmente los efectos de los 49 Tips.

Tip 10: se usó una COPIA sintética del fixture con bit 1 de 0x022B activado, para
habilitar la ruta nativa conocida. Original y r2 pasan de OPTIONS 0050 a STAGE SELECT
0032 mediante Y2+Y4 sobre EXIT. Sus tres capturas comparadas son idénticas, y la EEPROM
r2 permanece sin modificar. No se cambió esa bandera en el archivo del usuario.

EXIT + A conserva el comportamiento original, sin escrituras EEPROM.

## Tiempos y entorno

11 ejecuciones finales registradas: todas código 0. Cada proceso tuvo límite interno
Mesen y supervisor externo. Duraciones y órdenes exactas en `results_summary.json`.
Las ejecuciones finalizadas duran entre 0,460 y 12,950 s, con topes de 15–38 s.

Una batería agrupada anterior se interrumpió bajo un límite exterior de 180 s; no se
utiliza como PASS. Su Lua de regresión solicitaba stop/captura repetidamente al terminar.
Se protegió la salida con un latch de fin y se repitió UNA vez: código 0 en 5,079 s.
Los resultados anteriores se conservaron en el directorio de trabajo, sin sustituir
con ellos la evidencia final. No quedan procesos de prueba ejecutándose.

Mesen Linux del adjunto, SHA-256:
`ae43f1438282aaaff90a009aa8ada648bc5d631b070656285d7de9cbff513b41`.
Perfil portátil mínimo y `--testRunner`, sin DISPLAY. Se precarga la libstdc++ del
host (ruta en run.json), NO un interposer que omita errores del núcleo. Las advertencias
de RAM no inicializada figuran en los logs; también aparecen con la ROM original.

## Reproducibilidad y límites

Se reconstruyó el destino desde las fuentes incluidas y desde la ROM original.
BPS acumulativo y BPS incremental 4.1E→r2 se aplicaron de nuevo con CRC y hash final
verificados. Ambos dan exactamente la ROM f5652123…44217.

No se efectuaron ensayos eléctricos ni apagados físicos. El backend heredado conserva
sus límites: actualización diferencial no atómica, sin journal ni verificación final
read-back con error visible; una espera agotada no cancela explícitamente SAVED/DONE.
Los resultados de Mesen no acreditan tolerancia a pérdidas de alimentación ni duración
real de una EEPROM concreta.
