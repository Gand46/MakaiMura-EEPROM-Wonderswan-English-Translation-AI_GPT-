# Ruta posterior a HF19 — Makai-Mura EN-US

HF19 cierra la confirmación visible de borrado de datos de enemigos bajo entrada sintética `0x0110`; la ruta de menú normal y persistencia siguen abiertas. Las ventanas son propuestas de trabajo, no automatizaciones.

| Ventana propuesta | Investigación y criterio |
| --- | --- |
| 28–29 sep: confirmación de biblioteca | Trazar el retorno de entrada `4000:23CE–23F8` que asigna `0x0110` cuando `AL=0x0E`; navegar desde el menú principal hasta esa acción en JP/HF19. Probar YES y NO con un guardado de prueba, cierre y carga en frío, sin atribuir esos resultados a la entrada sintética. |
| 30 sep–2 oct: Stage Clear | Instrumentar fin de fase desde juego `0x0070/0x0080`. Capturar JP/HF19 con igual condición, clasificar texto y consumidor, traducir sólo restos confirmados, y registrar imágenes nativas antes/después. |
| 3–4 oct: barrido residual | Extender el censo aislado a estados no muestreados y fases tardías; revisar créditos y ramas. El barrido de 28 estados actual encontró el aviso `0x0110`, pero no prueba ausencia de japonés en los demás. |
| 5–6 oct: compuerta de versión | Revisar recorrido natural, persistencia en frío, regresión global, BPS y checksum. Sólo considerar RC cuando las compuertas obligatorias estén aprobadas. |

La traza de orientación `0x1A8837–0x1A889E` consulta `0x1B90/0x1B92` y al actor `0x1A08`; los ensayos de teletransporte/freeze no demostraron acceso normal a `0x0171`. Se mantiene abierto sin repetir esas condiciones como si fueran progresión jugada. Cada nueva corrección tendrá capturas JP/anterior/nueva, procedencia de acceso y censo de píxeles.
