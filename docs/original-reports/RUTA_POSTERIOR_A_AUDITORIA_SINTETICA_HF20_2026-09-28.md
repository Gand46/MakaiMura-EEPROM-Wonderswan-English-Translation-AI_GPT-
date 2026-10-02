# Ruta posterior al censo sintético HF20

El nuevo catálogo permite iniciar directamente los modos `0x00–0x11` y reproducir los diálogos `0x0380/0x03B0`; HF20 continúa como base verificada. Las fechas son ventanas de trabajo propuestas, no automatizaciones.

| Próxima ventana | Acción verificable |
| --- | --- |
| 29 sep: fin de fase | Desde uno de los 18 checkpoints, rastrear escrituras de `0x1B74` y `0x1E33` al final del nivel o del jefe. Capturar JP/HF20 en igual condición. Clasificar Stage Clear o ausencia de pantalla explícita antes de traducir. |
| 30 sep: orientación y confirmación | Para modo `0x0A`, instrumentar lectura de `0x1B92`/actor en `9000:8837–889E` y construir un checkpoint coherente. Para el borrado `0x0110`, seguir la acción de menú hasta YES/NO y comprobar datos tras cierre/carga en frío. |
| 1–2 oct: barrido tardío | Muestrear avance y señales con texto dentro de cada modo, más ramas de créditos y escenas que no cubren f3800/f4200. Guardar JP/HF20/nueva versión cuando haya un cambio. |
| Cierre | Revisión global de lenguaje, tipografía, funcionamiento, BPS y checksum; sólo entonces evaluar RC. |

No repetir el poke al final de fotograma que fue sobrescrito en `0x1B92=288`. La siguiente prueba debe cambiar el momento de inyección o aportar un estado coherente anterior.
