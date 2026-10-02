# Ruta posterior a HF20 — Makai-Mura EN-US

HF20 cerró la regresión del encabezado del índice `0x0161` mediante ruta normal y capturas JP/HF19/HF20. Las fechas son ventanas propuestas de trabajo, no automatizaciones.

| Ventana propuesta | Investigación y criterio de salida |
| --- | --- |
| 29–30 sep: confirmación de biblioteca | Seguir `4000:23CE–23F8` desde el menú hasta `0x0110` sin forzar estado. Capturar JP/HF20, probar YES/NO con guardado de prueba y confirmar persistencia tras cierre y carga en frío. |
| 1–3 oct: Stage Clear | Instrumentar final de fase desde `0x0070/0x0080`; capturar condiciones iguales JP/HF20. Identificar gráfico o tabla consumidos y traducir sólo japonés confirmado con registro nativo antes/después. |
| 4–5 oct: residuales y fases tardías | Extender el censo hacia créditos, ramificaciones y estados finales. Revisar `0x016B` únicamente por ruta natural, ya que la inyección aislada corrompe VRAM en JP. |
| 6–7 oct: compuerta global | Recorrido jugado, guardado frío, consistencia lingüística/diseño, BPS y checksum. Considerar RC sólo si las compuertas obligatorias tienen evidencia. |

Cada corrección nueva conservará fuente acumulativa, BPS directo desde JP y PNG nativos JP/versión anterior/nueva con clasificación explícita de acceso.
