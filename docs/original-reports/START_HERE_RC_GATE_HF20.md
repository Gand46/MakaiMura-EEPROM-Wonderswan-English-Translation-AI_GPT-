# HF20 — estado vigente

Lea primero `REPORT_RC_GATE_HF20_2026-09-28.md`. **HF20 es una compilación interna para pruebas; no RC.** Esta auditoría revisó 241 entradas de cinco tablas activas, 40 fotogramas de créditos, 30 estados comparativos y persistencia en frío del contador de muertes. Corrige el registro de `0x0133`: es una secuencia que llega a los créditos.

Para reconstruir, aporte una ROM japonesa legítima con SHA-256 `ac0c793b30d2de19ff6504d5a205e33f42aeeac724e7c284b48f48fbfbe53ed8` y use `BUILD_HF20.bat` en Windows o `build_hf20.command` en macOS/Linux. El BPS acumulativo `patches/Makaimura_EN_US_Phase4W_HF20_CUMULATIVE_FROM_JP.bps` se aplica directamente a esa ROM. Los archivos históricos no cambian la decisión vigente.

El recorrido completo manual no es condición pendiente de este entorno. Para la compuerta RC, continúe únicamente con el disparador sintético de salida de fase, el censo de los demás recursos gráficos/textuales y su QA representativa. Vea `RUTA_RC_SINTETICA_DESDE_HF20_2026-09-28.md`.
