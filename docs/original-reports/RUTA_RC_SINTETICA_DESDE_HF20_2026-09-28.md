# Cierre sintético de la compuerta RC

No se programa un recorrido completo en este entorno. Las 241 entradas de cinco tablas `E000`, los créditos hasta f24000 y la persistencia del contador de muertes ya tienen prueba; se reutilizan sus registros mientras HF20 no cambie.

| Prioridad | Prueba acotada | Criterio de cierre |
| --- | --- | --- |
| 1. Fin de fase | Trazar en Mesen el banco ejecutado y una condición de fin de tramo/jefe **antes de su lectura**. Crear checkpoint sintético coherente y comparar JP/HF20 hasta el estado siguiente. | PC, RAM, fotogramas y pantalla de transición reproducibles; clasificar si existe texto «Stage Clear» y cada variante. Si hay japonés, corregir y validar. |
| 2. Censo de gráficos/texto restante | Relacionar atlas, tablas y gráficos no cubiertos por los cinco consumidores `E000` con llamadas o acceso en ejecución. Clasificar los candidatos CP932 como datos, recursos inactivos o texto activo. | Universo por familia y consumidor; japonés activo confirmado pendiente = 0, ambigüedades clasificadas, revisión visual representativa. |
| 3. Calidad global | Revisar semántica, términos y glifos de las familias restantes a escala nativa; ensayar otras banderas de guardado si intervienen en progreso. | Sin defectos BLOCKER/MAJOR; controles obligatorios PASS o N/A justificado y registro gráfico. |
| 4. Etiqueta RC | Solo tras las anteriores: reconstruir desde JP, verificar checksum, diff permitido, BPS directo y regresión de pantallas. | `FINAL_APPROVED` derivado de todos los controles aplicables; paquete completo sin ROM/BIOS. |

El marcador sintético `0x44` usado antes no fue leído por el consumidor en el contexto de juego probado; no se repite idéntico. La inyección directa a `0x0132` es un control visual del selector y no cuenta como prueba causal de fin de fase.
