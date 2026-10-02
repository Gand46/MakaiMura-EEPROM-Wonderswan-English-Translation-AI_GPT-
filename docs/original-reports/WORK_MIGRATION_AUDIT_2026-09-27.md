# Makai-Mura WonderSwan — auditoría de migración HF11

Fecha: 2026-09-27. Base activa: Phase4W-HF11. Estado: **base de desarrollo reproducible; cobertura global y aprobación visual pendientes**.

## Entradas y reproducción

- ROM japonesa recibida: 2,097,152 bytes, SHA-256 `ac0c793b30d2de19ff6504d5a205e33f42aeeac724e7c284b48f48fbfbe53ed8`.
- BPS acumulativo adjunto y el del paquete: idénticos, SHA-256 `3c9034c9ebd59cd93ea140d5020b2c16b527081564477d9cf96c4af4f6541984`.
- Reconstrucción con `source/build_phase4w_hf11.py`: SHA-256 `b6379ffbdb8eb5caf8bb587cbc742149b63bfc8f4ac6af920affd29f32e45ff4`; resultado del BPS idéntico byte por byte. Checksum WonderSwan almacenado y calculado: `0x6C87`.
- Los dos ZIP recibidos superan la prueba de integridad de ZIP. `source/validate_work_migration.py` repite las comprobaciones esenciales sin producir una ROM distribuida.
- Las estructuras compartidas `D000:32D0-366D` y `D000:FF77-FFFF` permanecen idénticas a HF10 y a la ROM japonesa. En HF11, 1,392 bytes cambiaron frente a HF10 en los consumidores aislados, el recurso privado `E000` y el checksum, conforme al informe de diferencias incluido.

Ejecutar desde la raíz del paquete:

```text
python3 source/validate_work_migration.py /ruta/a/Makai_Mura_JP.ws
```

## Traducción y diseño: evidencia disponible

| Superficie | Estado sustentado | Límite |
| --- | --- | --- |
| Demon INDEX, 42 nombres | Integrados; capturas de QA sintético muestran las páginas 1–42 y campos de diez celdas | El desbloqueo de los 42 fue sintético; no certifica el progreso normal ni una aprobación visual global. Abreviaturas como `GREEN MSTR`, `SKULL FLWR`, `DARK ARTHR` y `ROCK TURTL` requieren revisión de estilo. |
| Demon INDEX, entradas bloqueadas | La captura `HF11_DEMON_INDEX_LOCKED_RUNTIME.png` muestra diez interrogaciones sin sufijo visible | `HF11_DEMON_INDEX_RUNTIME.png` muestra un carácter `G` aparente junto a la tercera fila; son evidencias divergentes. Repetir captura en ROM con SHA-256 HF11 y registrar su procedencia antes de conceder PASS general. |
| Cabecera INDEX | La fuente HF10 integra glifos latinos nativos; la ruta de construcción conserva ese cambio | El informe HF10 refiere capturas y auditoría de glifos que no están en este ZIP; la captura HF11 permite inspección limitada, no sustituye la comparación pixel a pixel indicada. |
| ARTHUR / USE PASSWORD | Hay correcciones acumulativas HF8–HF9 y fuente nativa conservada en ROM | Las capturas y JSON de validación HF8/HF10 citados por scripts o informe histórico no se incluyen. Se necesita lectura directa de HF11 para aprobación visual actual. |
| Library: contenidos, ítems, registros y detalles de demonios | Los informes previos describen traducción e integración; HF11 preserva las estructuras compartidas | Este paquete carece de una matriz completa de pantalla, texto y captura para volver a certificar todas esas superficies. |
| Stage Clear, Game Over, Continue, fases tardías, final y créditos | **Sin validación suficiente** en el paquete | No se confirma texto japonés concreto ni se descarta su presencia. |

La inspección de imágenes incluidas permite leer los nombres de Demon INDEX sin desbordamiento evidente en las páginas de QA. No se encontró una **nueva frase japonesa pendiente confirmada** mediante esta auditoría. Se hizo un barrido de secuencias Shift-JIS de la ROM japonesa y HF11: produjo miles de coincidencias espurias en datos y gráficos, por lo que no se cuentan como texto. Comparación por bancos: solo `0x14`, `0x1D`, `0x1E` y `0x1F` contienen diferencias frente al original; esto prioriza consumidores aún no auditados, pero no demuestra traducción pendiente ni ausencia de ella.

## Inconsistencias del paquete recibido y ajustes de esta copia

1. El manifiesto `SHA256SUMS` original contenía una entrada de sí mismo: `sha256sum -c` fallaba solo en ese elemento. Esta copia genera un manifiesto sin autoreferencia. Los otros 62 archivos del manifiesto recibido coincidían.
2. `reference/REPORT_HF10.md` cita nueve archivos de evidencia o build HF10 que **no están presentes** en el ZIP HF11. Se conserva el informe como antecedente, sin elevar esas referencias a evidencia entregada.
3. `source/validate_hf8_glyphs.py` asume rutas antiguas `base/`, una ROM HF8 y capturas HF8 ausentes; varias rutinas Lua de QA también fijan `/mnt/data/...`. Son material histórico y no se consideran pruebas portables ejecutables desde este ZIP. La nueva verificación binaria sí usa una ruta explícita a la ROM japonesa y solo las fuentes incluidas.
4. La etapa histórica Phase4W se conserva mediante BPS de referencia. El build acumulativo es reproducible, aunque las traducciones anteriores a HF1 no cuentan aquí con un catálogo editable integral de origen, traducción y consumidor. Para edición lingüística sistemática hará falta recuperarlo o generarlo.

## Próxima comprobación eficaz

1. Ejecutar la verificación binaria; conservar hash de ROM y versión del emulador junto a cada captura.
2. Recapturar en Mesen 2.1.1 la pantalla INDEX bloqueada y contrastar ambas capturas de HF11; si aparece el carácter `G`, corregir el consumidor y validar regresión antes de generar nuevo BPS.
3. Hacer censo por consumidor de las superficies todavía abiertas: Stage Clear y transiciones, Game Over/Continue, fases tardías, ending y credits. Para cada caso registrar texto original, destino, evidencia runtime y estado `translated/integrated/runtime-confirmed/visual-approved`.
4. Revisar a escala nativa la lectura y estilo de ARTHUR, USE PASSWORD, INDEX y abreviaturas de nombres; restaurar o recapturar la evidencia histórica faltante. Aplicar correcciones comprobadas y emitir entonces un nuevo BPS acumulativo desde la ROM japonesa.

**Conclusión:** migración binaria PASS; Demon INDEX integrado con una discrepancia de capturas por resolver; traducción completa, diseño global y RC aún no demostrados. No se modifica el binario HF11 en esta auditoría.
