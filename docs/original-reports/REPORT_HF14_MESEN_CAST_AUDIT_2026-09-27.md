# Makai-Mura WonderSwan — auditoría Mesen y traducción HF14

Fecha: 2026-09-27. Destino EN-US. **HF14 de desarrollo**; no se ha certificado
la traducción completa ni se concede aprobación visual global.

## Mesen y la documentación del proyecto

Se examinó `mesen_visualization_source_v1.1.0` y se ejecutó Mesen 2.1.1 Linux
x64 proporcionado con el proyecto. El intento HF13 anterior falló con
`XOpenDisplay failed` por no tener el perfil portátil. `prepare_mesen.sh`
instaló `settings.json` (`{}`) junto a `Mesen` y `probe_mesen.sh` cargó
activamente HF13: exit 0, `test_runner_ready_without_display=true`. ELF
SHA-256 `ae43f1438282aaaff90a009aa8ada648bc5d631b070656285d7de9cbff513b41`.
La ejecución GUI sigue sin servidor de pantalla ni Xvfb, pero el test runner
captura el framebuffer sin `DISPLAY`.

El tutorial de visualización asume 224×144 o 237×144 para
`--normalize-wonderswan`. La ROM produjo **224×157** con una franja inferior
de 13 píxeles. La normalización rechazó correctamente esa geometría;
**omitiendo la opción** se validó el PNG completo (`passed=true`), sin recorte.
Las órdenes exactas están en `MESEN_HF14.md`; los JSON de ejecución están en
`build/hf14_*.json`. Los envoltorios `.sh` se invocaron mediante `bash` porque
el ZIP extraído no conservó permiso ejecutable en este entorno.

## Etapa de traducción integrada

El código `4000:5E18` carga el atlas `E000:01DE` (selector de banco 3) durante
la rutina final. El consumidor `4000:60A8` (`ROM 0x1460A8`) recorre la tabla
`E000:0579`, con 13 punteros `E000:0594–06DA`. El recurso original combina un
nombre inglés y una segunda línea fonética japonesa. La tarjeta 11 añade una
tercera línea latina, `B88 W58 H90`.

HF14 conserva literalmente los nombres ingleses existentes: ZOMBIE, GHOST,
FRANKEN ZOMBIE, GHOST FORTRESS, DAGON, EFREETI, NIGHTMARE, RANGDA, TIAMAT,
AZAZEL, RED ARREMER, PRINCESS PRIN PRIN y KNIGHT ARTHUR. Se retira la lectura
japonesa de los **13 registros activos**, se preservan las medidas latinas
de la princesa, y se rellenan con `FF` los bytes sobrantes de cada registro.
Ningún puntero, atlas, glifo o consumidor se cambia. El atlas original aún
contiene glifos japoneses sin referencia en esas 13 filas; no se afirma que
todos los activos gráficos de la ROM estén traducidos.

La hoja `evidence/HF14_CAST_NATIVE_FONT_PREVIEW_NOT_RUNTIME.png` recompone los
glifos 8×16 originales en el ancho de 224 píxeles. Todas las líneas activas
caben en ese ancho; la más larga ocupa 18 celdas (144 píxeles) más su margen.
Es una **vista diagnóstica**, no una captura de pantalla del juego.

## Pruebas de integridad y ejecución

| Comprobación | Resultado |
| --- | --- |
| ROM japonesa base SHA-256 | `ac0c793b30d2de19ff6504d5a205e33f42aeeac724e7c284b48f48fbfbe53ed8` |
| ROM HF13 anterior SHA-256 | `a3cc32242c5dd0812e1caa8639fc9adbbbbf694b00d69a34610534716d2858e6` |
| ROM HF14 reconstruida SHA-256 | `d4f891ce248bbb49107c1c4825e245c132c00b97a5b61a5b256723db716181c0` |
| BPS acumulativo JP → HF14 SHA-256 | `30dd30ea6eb629e0d816457b205985b37422df613a44f4104172c6e0924ec447` |
| Aplicación BPS frente a reconstrucción | Idéntica byte por byte, PASS |
| Checksum WonderSwan almacenado y recalculado | `0x6C93`, PASS |
| Diferencia HF13 → HF14 | 175 bytes, solo `E000:0594–06F4` y checksum |
| 13 punteros y nombres; 13 lecturas japonesas activas retiradas | PASS |
| Arranque HF14, INDEX y rutina final forzada en Mesen | Exit 0; capturas válidas 224×157 |

El arranque HF13 y HF14 y la captura de INDEX son idénticos a nivel PNG en
los mismos fotogramas. La entrada temporal a la rutina final mediante
`source/qa_force_ending.lua` llegó hasta el fotograma 7200 sin bloqueo y
mostró la secuencia de retratos. **Las tarjetas de texto no se vieron en estas
capturas forzadas**; HF13 y HF14 también produjeron la misma captura temprana
de retratos. Esta prueba acredita carga y ejecución de la ruta, pero **no**
`VISUAL_APPROVED` ni `LEGIBILITY_PASS` de los nombres en la pantalla final.
La prueba de estilo disponible es estructural y de glifos nativos. Una ruta
natural o un estado de juego legítimo de la escena final sigue pendiente.

La cabecera derecha de INDEX parece ilegible tanto en la ROM japonesa como en
HF14 bajo la misma ruta de Mesen. Es un hallazgo visual reproducible que
requiere investigación separada; no se atribuye a los 175 bytes de HF14.
Tampoco se han visto en juego las tres escenas de diálogo integradas en
HF12/HF13; sus chequeos binarios siguen válidos, pero su ritmo, envoltura y
contraste están pendientes. Quedan por censar Stage Clear, Continue/Game Over,
créditos y otras rutas tardías antes de una versión candidata.

## Reproducción

```text
python3 source/build_phase4w_hf14.py CLEAN_JP.ws HF14_PRIVATE.ws HF14_CUMULATIVE_FROM_JP.bps
python3 source/validate_hf14.py CLEAN_JP.ws
python3 source/render_cast_cards.py HF14_PRIVATE.ws cast_preview.png
```

Aplicar el **BPS acumulativo directamente** a la ROM japonesa limpia; no se
distribuye la ROM comercial. El historial HF11–HF13 se conserva en el paquete
para reproducibilidad, pero no se encadena al instalar HF14.
