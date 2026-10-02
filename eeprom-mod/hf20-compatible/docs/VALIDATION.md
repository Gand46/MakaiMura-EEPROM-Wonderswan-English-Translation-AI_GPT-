# HF20-compatible EEPROM validation scope

The supplied 29 September 2026 report documents the clean JP→HF20+EEPROM build, both patch replay paths, precondition checks, no translated bytes overwritten, 55 Mesen executions, six cold loads and 132 identical native game-area comparison pairs. Normal menus were reached with scripted buttons; injected scenes and Tip 10 fixture access are labeled PASS_SYNTHETIC. Actual CONTINUE was compared against equivalent HF20 data; a synthetic stage selection does not prove a naturally saved new checkpoint.

This repository preparation verifies patch bytes, checksums and source import paths. It does **not** rerun ROM construction or Mesen runtime because no clean Japanese ROM was supplied with this task. The historical test seed and output EEPROM/SRAM files are omitted from the public package. `validation/run_suite.py` and `verify_results.py` now accept `--seed` for a private 2,048-byte fixture instead of reading an embedded save.

The HF20 translation's Stage Clear and complete text/graphic census remain NOT_VALIDATED; global visual/linguistic approval and RC status are unchanged. Physical EEPROM write timing, wear and interrupted-write recovery are NOT_VALIDATED.
