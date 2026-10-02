# Makai-Mura WonderSwan EN-US — HF20

Versión de desarrollo, no RC. HF20 corrige a `INDEX` el encabezado del primer índice del libro, ilegible en HF19, y conserva la trayectoria acumulativa HF1–HF19.

Aplicar `patches/Makaimura_EN_US_Phase4W_HF20_CUMULATIVE_FROM_JP.bps` **directamente** a la ROM japonesa original de 2 MiB cuyo SHA-256 es `ac0c793b30d2de19ff6504d5a205e33f42aeeac724e7c284b48f48fbfbe53ed8`. No aplicar sobre HF19. La ROM resultante debe tener SHA-256 `885eb8268ad8594c1ee5e229db22b0f639da5498a22f262e0d4c0884a1401b51`.

Windows: `BUILD_HF20.bat CLEAN_JP.ws`. macOS/Linux: `./build_hf20.command CLEAN_JP.ws`. Requieren Python 3 y generan una ROM privada local y BPS acumulativo. El ZIP distribuye fuentes, parche, informes, hashes y registros gráficos, sin ROM ni BIOS.

Ver `REPORT_HF20_ARTHUR_INDEX_DESIGN_2026-09-28.md`, `MESEN_HF20.md` y `RUTA_PROGRAMADA_MAKAIMURA_DESDE_HF20_2026-09-28.md`.
