# Reproducción de la auditoría HF20

Requisitos: Python 3, Pillow para los mosaicos, Mesen 2.1.1 y `mesen_visualization_source_v1.1.0` proporcionados aparte. Use una ROM japonesa de 2 MiB cuyo SHA-256 sea `ac0c793b30d2de19ff6504d5a205e33f42aeeac724e7c284b48f48fbfbe53ed8`. No se adjunta ninguna ROM ni BIOS. Las instrucciones siguientes se ejecutan desde la raíz extraída de este paquete.

```text
python3 source/validate_hf20.py /ruta/Makai_Mura_JP.ws
python3 source/build_phase4w_hf20.py /ruta/Makai_Mura_JP.ws /ruta/HF20_PRIVATE.ws /ruta/HF20.bps
python3 source/audit_active_e000_hf20.py /ruta/HF20_PRIVATE.ws
python3 source/run_hf20_state_matrix.py --jp /ruta/Makai_Mura_JP.ws --hf20 /ruta/HF20_PRIVATE.ws --mesen /ruta/Mesen --visual /ruta/mesen_visual.py --output qa/state_matrix_hf20
python3 source/analyze_hf20_state_matrix.py --input qa/state_matrix_hf20
```

Para créditos JP/HF20, ejecute dos capturas con `source/qa_credit_sweep_hf20.lua` y el comando `capture` de `mesen_visual.py` documentado en `MESEN_HF20.md`. Cada una dura 24.000 fotogramas y produce 40 PNG cada 600; `source/analyze_credit_sweep_hf20.py` compara las parejas. Los PNG y JSON completos utilizados ya están en `evidence/rc_gate_hf20/raw_credits/` y `raw_states/`. El atlas diagnóstico de créditos no es una captura del juego.

La prueba de guardado frío usa una copia **privada y de nombre nuevo** de HF20 para aislar su `.sav`: ejecutar `source/qa_arthur_hf7.lua` para el contador inicial, cerrar Mesen, ejecutar `source/qa_gameover_probe.lua` hasta f9600 sobre la misma copia, cerrar Mesen y volver a ejecutar `source/qa_arthur_hf7.lua` en otro proceso. El valor observado fue `000000→000003`. El guardado de prueba y el registro visual se incluyen; un savestate por sí solo no demostraría persistencia.

Para comprobar el paquete, `sha256sum -c SHA256SUMS` en Linux/macOS con coreutils. El `.bat` del build está para Windows; la auditoría de Mesen aquí se ejecutó en Linux, sin afirmar prueba de `.bat` en Windows o `.command` en macOS.
