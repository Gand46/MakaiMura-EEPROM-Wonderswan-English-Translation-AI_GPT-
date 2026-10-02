# Makai-Mura WonderSwan — auditoría y corrección HF13

Fecha: 2026-09-27. Idioma destino: inglés. **Estado: traducción integrada y validada estructuralmente; ejecución de las escenas y aprobación visual pendientes.** HF13 sigue siendo una versión de desarrollo.

## Hallazgo verificable

HF11 aún cargaba tres atlas japoneses en `E000` por los consumidores `4000:587C`, `4000:5A7E` y `4000:5C3A` (offsets de ROM aproximados `0x14587C`, `0x145A7E`, `0x145C3A`). Las tablas de renglones originales se usan explícitamente en el código:

| Escena | Atlas original | Tabla y consumidor | Entradas | Ejemplo leído del recurso japonés |
| --- | --- | --- | ---: | --- |
| Rescate y brazalete | `E000:000A` | `E000:028C`, instrucción `0x14594C` | 23 | `アーサー…私を助けに来てくれたのですね。` |
| Variante sin brazalete | `E000:00A0` | `E000:039F`, instrucción `0x145B4B` | 15 | `アーサーどうして腕輪を探して来てくれなかったのですか？` |
| Narración final | `E000:0118` | `E000:0458`, instrucción `0x145F30` | 14 | `アーサーは秘めたる力を持つ「女神の腕輪」を身に着け…` |

Son **52 entradas estructurales**, incluidas las pausas vacías. La asociación consumidor → atlas → tabla → tokens es una prueba de que son recursos de texto usados por el juego; el barrido Shift-JIS general no sirve para este formato de atlas propio. Se identificaron además katakana en el banco `E000:01DE` emparejado con nombres latinos: queda para trazado y revisión posterior. El banco `E000:0252` emplea glifos latinos; esta observación no certifica todos sus consumidores.

## Corrección integrada

HF12 aloja el primer diálogo en `E000:CD00–CE..`; HF13 añade la variante y narración en `E000:CF00–D244`. El cargador `D000:087B` lee un selector de atlas y el número de glifos; se cambian **solo** los tres selectores de `E000:0000–0005` y las tres instrucciones `mov si` que entregan las tablas al renderizador. Las demás tablas originales se conservan. Los 52 renglones mantienen sus índices y terminador `FF`.

Las traducciones editables están en `source/build_phase4w_hf12.py` y `source/build_phase4w_hf13.py`. Se fijó un máximo de **13 celdas por línea**, igual al máximo medido de las escenas japonesas (13, 14 y 13 respectivamente; se usa el límite menor). La fuente usa exclusivamente glifos latinos y signos originales de `F000`, con la misma cuadrícula 8×16 del renderizador. No se creó ni sustituyó un tipo de letra. Las vistas `evidence/*PREVIEW_NOT_RUNTIME.png` muestran los píxeles exactos del banco nativo en una hoja diagnóstica; **no son capturas del juego**.

Se mantienen `AZAGOL` para アザゴル y `GODDESS BRACELET` como nombre compacto para 女神の腕輪. El título japonés 魔帝 y ciertos matices se condensaron por el campo de 13 celdas; requieren revisión lingüística contextual al ver la escena. Las pausas se redistribuyeron en la primera escena para permitir inglés legible sin ampliar el campo.

## Resultado binario

| Comprobación | Resultado |
| --- | --- |
| ROM japonesa de entrada | SHA-256 `ac0c793b30d2de19ff6504d5a205e33f42aeeac724e7c284b48f48fbfbe53ed8` |
| HF13 reconstruido | SHA-256 `a3cc32242c5dd0812e1caa8639fc9adbbbbf694b00d69a34610534716d2858e6` |
| BPS **acumulativo JP → HF13** | SHA-256 `d08c61a782b71f0fc4f85784a8bca0a402b25f17b5e50a477dc513518ef9a7c1` |
| Aplicación BPS frente a reconstrucción | Idéntica byte por byte, PASS |
| Checksum WonderSwan | `0xDFA2` almacenado y recalculado, PASS |
| Cambios HF11 → HF13 | 830 bytes; tres selectores, tres operandos de consumidor, tres recursos privados, checksum; fuera de rangos previstos: cero |
| Regresión estructural | Bancos de historia 3 y 4, tabla original de texto, recurso y consumidor HF12, estructuras compartidas D000, y glifos A–Z originales preservados |

Ejecutar en Windows/macOS/Linux con Python 3:

```text
python3 source/build_phase4w_hf13.py CLEAN_JP.ws HF13_PRIVATE.ws HF13_CUMULATIVE_FROM_JP.bps
python3 source/validate_hf13.py CLEAN_JP.ws
```

En Windows se puede sustituir `python3` por `py -3`. El BPS entregado se aplica **a la ROM japonesa original**, no a HF11 o HF12. El proyecto fuente conserva los BPS históricos necesarios para reproducir HF11; la ROM comercial y la ROM aplicada no se distribuyen.

## Validación de diseño y trabajo abierto

Se comprobó en los bytes de ROM: glifos nativos A–Z intactos; signos nativos `.` y `?`; tabla de caracteres, punteros y terminadores válidos; máximo de 13 celdas; otras tablas preservadas. La lectura directa de las hojas diagnósticas es clara, pero no se otorga `RUNTIME_CONFIRMED`, `VISUAL_APPROVED` ni `LEGIBILITY_PASS` a estas escenas hasta verlas dentro del juego.

Mesen 2.1.1 suministrado no pudo iniciar aquí: `System.Exception: XOpenDisplay failed`. No se generó savestate ni captura runtime nueva. En la próxima sesión con pantalla/emulador, usar estado o inyección mínima para las tres ramas, capturar escalas nativas y revisar saltos de línea, ritmo, paleta, clip, superposición y regresión del INDEX bloqueado (capturas HF11 divergentes).

Pendientes prioritarios: (1) texto de katakana restante en banco E000:01DE y su propósito; (2) Stage Clear/transiciones, Game Over/Continue, fases tardías y créditos mediante trazado de consumidores o captura sintética; (3) pulido de términos y lectura real de ARTHUR, USE PASSWORD, INDEX y diálogo; (4) censo integral con estado por superficie. **No se afirma que la traducción global esté terminada ni que HF13 sea RC.**
