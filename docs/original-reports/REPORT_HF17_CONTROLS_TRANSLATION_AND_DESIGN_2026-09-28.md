# Makai-Mura WonderSwan — HF17: aviso y controles

Fecha: 2026-09-28 UTC. Destino: EN-US. **Versión de desarrollo para pruebas, no RC.** Partida de la ROM japonesa limpia y fuentes acumulativas HF1–HF17; la ROM no se distribuye.

## Identidad y resultado

| Componente | SHA-256 / dato |
| --- | --- |
| JP original, 2 MiB | `ac0c793b30d2de19ff6504d5a205e33f42aeeac724e7c284b48f48fbfbe53ed8` |
| HF16 de referencia | `1be7103b2c0c5c4577a89706560115196357c8b43db35b835e184a459f68b95a` |
| HF17 resultante | `90cc07da4db2909d47f131134564d3b1b796823f16f1d30200b17d9059f10715` |
| BPS acumulativo JP→HF17 | `9191d203b97a078af7a7f23476d3094013090e118828b38a1dd475dcf2e89011` |
| Checksum WS | `0x62DE` válido |
| Mesen 2.1.1 Linux | SHA-256 `ae43f1438282aaaff90a009aa8ada648bc5d631b070656285d7de9cbff513b41` |

## Traducciones integradas

| ID gráfico | Original visible | HF17 visible | Evaluación |
| --- | --- | --- | --- |
| `ORIENTATION_NOTICE` | `本体の方向を縦型に持ち直して下さい。` | `HOLD THE / CONSOLE / UPRIGHT` | Se conserva la instrucción de sostener la consola en orientación vertical. Tres líneas de ocho celdas, 8×16 px, con margen en el panel. |
| `CONTROL_MOVE` | `移動` | `MOVE` | Placa ensanchada para dar margen a cuatro letras sin pisar el borde. |
| `CONTROL_ATTACK` | `攻撃` | `ATTACK` | Placa de seis letras en la posición del botón. |
| `CONTROL_JUMP` | `ジャンプ` | `JUMP` | Placa alineada bajo ATTACK; se eliminó el primer glifo japonés que invadía la izquierda. |

Se reutiliza la geometría **nativa** de las letras latinas 8×16 del banco `SEGF` (función `glyph_8x16`), con remapeo de los índices de paleta del fondo, trazo y antialias a las dos superficies. No se usa una fuente genérica. El render redibuja sólo las tres placas de controles necesarias para acomodar la tipografía completa; los iconos, el panel, el marco exterior y `PUSH ANY BUTTON` conservan su composición. Se inspeccionó la captura nativa antes de aprobar lectura de `HOLD THE`, `CONSOLE`, `UPRIGHT`, `MOVE`, `ATTACK` y `JUMP`; la hoja comparativa es sólo una ayuda visual.

## Integración y límites del cambio

Dos mapas de 28×18 celdas parten de `0x307E0` y `0x30BD0`; el primero recibe también las nuevas placas. Los gráficos privados se codifican en IDs `0x1AE..0x1FE` a partir de `0x322A0` hasta `0x327AF`. Ninguno de esos IDs estaba referenciado por los **cuatro mapas estáticos** de este banco antes del cambio. Se conserva el atributo de cada palabra del mapa; la celda `r10,c6` con bit `0x4000` requiere compensar su inversión vertical después de la rotación de pantalla. La comprobación de píxeles detectó y eliminó los dos puntos que ese atributo había movido fuera del área prevista.

Entre HF16 y HF17 cambian **1518 bytes**. `validate_hf17.py` determinó `unexpected_changed_offsets=0`: sólo mapas delimitados, gráficos privados y dos bytes de checksum. Los bancos ajenos permanecen byte a byte iguales. Esto verifica aislamiento de los recursos estáticos y de las pantallas muestreadas; no equivale a una prueba exhaustiva de todos los consumidores dinámicos del banco.

## Registro gráfico y pruebas

| Prueba | Método / resultado |
| --- | --- |
| Aviso JP/HF16 | `SYNTHETIC_STATE` `0x0171` en WRAM al frame 180. La captura f900 es idéntica en ambas ROMs, demostrando las cuatro áreas japonesas residuales en HF16. |
| Aviso HF17 | El mismo método en Mesen. Captura nativa 157×224; letras legibles y marcos completos. `evidence/controls_HF17/` contiene JP, HF16, HF17 y la comparación gráfica. |
| Alcance por píxel | En frames 240, 360, 600 y 900 los cambios se confinan a aviso `(32,40,104,104)`, MOVE `(8,170,56,192)`, ATTACK `(80,170,140,190)` y JUMP `(64,190,140,209)`; **cero píxeles distintos fuera** de esas cuatro cajas en cada frame. Registro exacto en `GRAPHICAL_RECORD_HF17.json`. |
| Salida de instrucciones | Se pulsa A en f960–965 desde `0x0171`. Tanto HF16 como HF17 llegan a `0x0080` en f1000 y mantienen ese estado en f1300. Capturas f1000/f1300 idénticas. Esto prueba salida tras **entrada sintética**, no entrada natural. |
| Regresión sintética | Capturas f900 idénticas HF16/HF17 en estados `0x0130` (título), `0x0165`, `0x0166`, `0x0169` (biblioteca), `0x0133` (créditos) y `0x01B0` (juego). |
| Regresión de menú | Ruta `SCRIPTED_NATURAL` START→OPTIONS→BUTTON CONFIG. Ocho capturas f520–3000 idénticas HF16/HF17. No apareció `0x0171` en esa ruta. |
| BPS | `validate_hf17.py` pasa. Reaplicación con el verificador del proyecto e **implementación BPS independiente** del paquete WS Patch Tools v0.1.1: salida idéntica al build, 2 MiB; la base alterada rechazada por CRC. |
| Lanzadores | `build_hf17.command` ejecutado en Linux: generó la ROM y BPS esperados y pasó `validate_hf17.py`; se retiró la ROM privada del paquete. `BUILD_HF17.bat` está incluido para Windows, pero no se ejecutó aquí porque no hay `cmd.exe` ni Wine. El `.command` no se ha ejecutado en macOS. |

La traza estática halló un **posible disparador jugable**, aún sin ejecución demostrada: el código del banco físico `0x1A0000`, desplazamiento `0x887B`, asigna estado `0x0171` y `0x1B74=0x000A` tras comparaciones de posición y condiciones del jugador. En `4000:0DCD–0E0F` también se elige `0x0171` cuando `0x1B74=0x000A`; otros valores llevan a `0x0131/0x0132`. Estos sitios acotan la próxima traza, pero no prueban qué movimiento natural los alcanza. `RUNTIME_CONFIRMED`, `LEGIBILITY_APPROVED`, `TYPOGRAPHY_APPROVED` y `DESIGN_APPROVED` se refieren al render sintético en HF17; `FUNCTIONAL_APPROVED` se limita a la salida con A. No se extienden a una progresión natural o al juego completo.

## Pendientes después de HF17

1. Instrumentar los sitios `0x1A887B` y `4000:0DCD–0E0F` para documentar la ruta natural al aviso y cualquier variante de configuración de botones.
2. Alcanzar Stage Clear y transiciones de forma instrumentada, comparar JP/HF17 y traducir las variantes que conserven japonés.
3. Completar el censo de fases tardías, ending y créditos; las muestras de créditos observadas en HF16 ya eran latinas en JP, pero no son cobertura global.
4. Revisar guardado/carga en frío y el resto de la regresión de larga duración antes de hablar de RC.

No se calcula porcentaje global porque el universo de gráficos/textos todavía no está cerrado.
