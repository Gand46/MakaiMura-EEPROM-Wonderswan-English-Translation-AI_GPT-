# Makai-Mura WonderSwan — HF15, corrección de narración final

Fecha: 2026-09-27. Destino EN-US. **Versión de desarrollo, no RC.**

## Defecto encontrado y corrección

La inicialización del final en `4000:5C80` establece un contador de **25**
entradas (`mov word [bx+11h],0019h`). El consumidor `4000:5F28` recorre esas
25 entradas desde `E000:D180` mediante `D000:08E8`. En la ROM japonesa, la
tabla `E000:0458` tiene 25 punteros y cinco pausas vacías en los índices
**4, 9, 14, 20 y 24**. HF13/HF14 sustituyó esa tabla por una traducción de
solo **14 entradas**. El motor continuaba leyendo 11 punteros adicionales
fuera del recurso, lo que producía glifos y mosaicos invasores en la escena.

HF15 reconstruye `E000:D180–D2BA` con 25 entradas inglesas y las cinco
pausas originales. Se traduce también el último párrafo japonés, que faltaba:
el castillo y el velo nocturno caen al llegar la luz, y Arthur y la princesa
parten hacia casa. Cada línea usa 13 celdas como máximo, con los glifos
8×16 nativos; no se cambia el atlas ni la rutina de dibujo. La traducción
editable está en `source/build_phase4w_hf15.py`. La escena no accede ahora
fuera de la tabla.

## Evidencia en Mesen

La prueba sintética entra por el estado de inicialización `0x0134`, no por el
estado intermedio `0x0034`. Ese detalle carga los fondos y las paletas antes
del texto. Se capturaron los **25 pasos** de narración y, a continuación, las
**13 tarjetas** de personajes en la ROM HF15, a 224×157 píxeles nativos.
`evidence/HF15_ENDING_RUNTIME_CONTACT.png` y
`evidence/HF15_CAST_RUNTIME_CONTACT.png` reúnen esas capturas, con fotogramas
registrados en los JSON de `build/`.

La comparación `evidence/HF14_HF15_ENDING_VISUAL_COMPARISON.png` muestra el
mismo fotograma 2600: HF14 invade las figuras con caracteres; HF15 muestra
`SUNLIGHT CAME` y el siguiente párrafo sin esos mosaicos. La animación de
desplazamiento deja fragmentos transitorios en los bordes superior e inferior,
también presentes en la escena japonesa; las líneas centrales se leen y no
desbordan horizontalmente. Las 13 capturas de tarjetas de HF15 son idénticas
byte a byte a las de HF14. La tarjeta de la princesa conserva `B88 W58 H90`.

| Comprobación | Resultado |
| --- | --- |
| ROM japonesa base SHA-256 | `ac0c793b30d2de19ff6504d5a205e33f42aeeac724e7c284b48f48fbfbe53ed8` |
| HF14 SHA-256 | `d4f891ce248bbb49107c1c4825e245c132c00b97a5b61a5b256723db716181c0` |
| HF15 SHA-256 | `448113002b885d24d1b39d41bbfb35c77f9d961befb5c67777b9afa367d45456` |
| BPS acumulativo JP → HF15 SHA-256 | `cfc23cafe59e8d8ecdbb18c8a09f1bdf4ce21c2f347eea3ac97fc1b53e4b217c` |
| BPS aplicado frente a ROM reconstruida | Idéntico byte por byte, PASS |
| Checksum WonderSwan almacenado/recalculado | `0x14F4`, PASS |
| Diferencia HF14 → HF15 | 277 bytes, solo `E000:D180–D2BA` y checksum |
| Contador/punteros/terminadores | 25/25, pausas 4, 9, 14, 20, 24, PASS |
| Narración y tarjetas en Mesen | 25/25 y 13/13 capturadas, salida 0 |

Los diálogos de rescate (23 entradas) y variante (15) se habían integrado en
HF12/HF13; en esta etapa también se accedió a ambos por sus estados de
inicialización `0x0380` y `0x03B0`, y se constató texto inglés legible en las
capturas de muestra. Sus recursos y consumidores no cambiaron en HF15.

## Alcance y siguientes superficies

La aprobación visual anterior corresponde a **rutas sintéticas controladas**
de narración y tarjetas. Quedan pendientes el recorrido natural de las
ramas, Stage Clear/transiciones, Game Over/Continue, fases tardías y censo
global de créditos/gráficos. La cabecera del INDEX requiere revisión aparte:
su lado derecho ya parecía ilegible en la ROM japonesa con la misma ruta.
No se declara traducción completa ni release candidate.

## Reproducción

```text
python3 source/build_phase4w_hf15.py CLEAN_JP.ws HF15_PRIVATE.ws HF15_CUMULATIVE_FROM_JP.bps
python3 source/validate_hf15.py CLEAN_JP.ws
```

En Windows: `BUILD_HF15.bat CLEAN_JP.ws`. En macOS:
`build_hf15.command CLEAN_JP.ws`. `MESEN_HF15.md` documenta la captura Linux
sin `DISPLAY` con el perfil portátil `settings.json`. El BPS entregado se
aplica **directamente a la ROM japonesa limpia** de 2 MiB; no se distribuye
ninguna ROM comercial o aplicada.
