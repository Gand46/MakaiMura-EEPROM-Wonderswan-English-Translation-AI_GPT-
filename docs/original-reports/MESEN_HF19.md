# Captura HF19 en Mesen 2.1.1

Con el Mesen Linux x64 2.1.1 suministrado (perfil portátil `settings.json` `{}`), ejecutar el capturador `mesen_visualization_source_v1.1.0/scripts/mesen_visual.py` con ROM privada HF19 y `source/qa_state_survey.lua`, variable `QA_STATE=272` (`0x0110`). El script introduce ese estado en WRAM al fotograma 180 y captura los fotogramas 240, 360, 600 y 900 en **224×157** píxeles nativos. Usar la misma secuencia con JP y HF18 para la hoja comparativa; `source/qa_graphical_records_hf19.py` genera el censo de píxeles. Las capturas verificadas están incluidas en `evidence/enemy_library_erase_HF19/`.

El script `source/qa_prompt_exit_hf19.lua` ensaya A o B tras entrar por estado sintético. Ambos ensayos llegaron a `0x0030` en las condiciones de prueba; no validan el borrado persistente ni la ruta natural de acceso al diálogo. La ejecución de `.command` se ensayó en Linux. El `.bat` no se ejecutó en Windows ni el `.command` en macOS.
