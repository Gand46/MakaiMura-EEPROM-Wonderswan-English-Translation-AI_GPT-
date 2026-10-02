# Makai-Mura EN-US — auditoría sintética sobre HF20

La ROM y el parche siguen siendo **HF20**. Esta entrega añade un método reproducible para inicializar 18 modos de fase, un censo de ocho estados altos, capturas nativas JP/HF20 y un informe de alcance. No es RC ni crea HF21.

Para aplicar la traducción, usar **sólo** `patches/Makaimura_EN_US_Phase4W_HF20_CUMULATIVE_FROM_JP.bps` sobre la ROM japonesa original de 2 MiB y SHA-256 `ac0c793b30d2de19ff6504d5a205e33f42aeeac724e7c284b48f48fbfbe53ed8`. Resultado esperado SHA-256 `885eb8268ad8594c1ee5e229db22b0f639da5498a22f262e0d4c0884a1401b51`.

Fuentes completas y build: `BUILD_HF20.bat CLEAN_JP.ws` en Windows, `./build_hf20.command CLEAN_JP.ws` en macOS/Linux, con Python 3. Ejecutado en Linux; otros sistemas no ensayados en esta sesión. Consultar `REPORT_AUDITORIA_SINTETICA_HF20_2026-09-28.md`, `MESEN_SINTETICO_HF20.md` y la nueva ruta de pendientes. El ZIP no contiene ROM, BIOS ni emulador.
