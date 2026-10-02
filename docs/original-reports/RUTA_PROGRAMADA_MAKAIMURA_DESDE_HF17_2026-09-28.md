# Ruta posterior a HF17 — Makai-Mura WonderSwan EN-US

El hito gráfico de orientación y controles está integrado en HF17 y tiene capturas JP/HF16/HF17. La ruta natural al aviso continúa abierta. Las fechas siguientes son ventanas propuestas de trabajo, no una automatización.

| Hito / ventana propuesta | Acción y cierre exigido |
| --- | --- |
| 28–29 sep: acceso al aviso | Instrumentar `0x1A0000:887B` y `4000:0DCD–0E0F`: la primera rutina escribe `0x0171` y modo `0x000A`, y la segunda elige esa pantalla cuando detecta dicho modo. Identificar las coordenadas/condiciones reales y capturar la ruta HF17 y salida; marcar `SCRIPTED_NATURAL` sólo cuando se observe. No rehacer la corrección visual ya aprobada sin una discrepancia concreta. |
| 30 sep–2 oct: Stage Clear | Instrumentar desde `0x0070/0x0080` hasta evento de fin de fase; capturar JP/HF17 a la misma condición, registrar variantes y consumidores antes de modificar texto/gráficos. Parchar y comprobar composición, transición siguiente, BPS/checksum. |
| 3–4 oct: barrido residual | Escenas tardías, derrota/reintentos, biblioteca, final y créditos. Vincular cada candidato JP con captura/consumidor; revisar glosario y lectura visual. Registrar explícitamente superficies no alcanzadas. |
| 5–6 oct: regresión de candidato | Rutas naturales y sintéticas diferenciadas, guardado+carga en frío, emulación, fuentes acumulativas, BPS desde JP y prueba independiente. Sólo proponer RC con las compuertas obligatorias en PASS. |

Cada traducción nueva llevará captura original JP, captura del build anterior, captura nueva a tamaño nativo, referencia de emulador/build/estado y un censo de píxeles fuera de las zonas previstas. El archivo `evidence/controls_HF17/GRAPHICAL_RECORD_HF17.json` es el patrón de HF17. La investigación se corta tras intentos acotados y pasa a traza/estado sintético cuando la ruta natural no progresa; una inyección nunca se presenta como victoria jugada.
