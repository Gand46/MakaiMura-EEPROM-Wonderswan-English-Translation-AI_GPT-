# Packaging verification — 2 October 2026

- Both supplied archives were inspected through their nested ZIPs; all `910` input decisions are in `ORGANIZATION_MANIFEST.csv`. ZIP `__MACOSX` resource forks were discarded during extraction.
- The original 4.1E-r2 cumulative BPS matches its separately attached copy: `76cbadf9c878f57cea71c882f17b1c457642d15ddfae11617f43f2c5d04f0d4a`. Both HF20 integration BPS files match their separately attached copies: `bf4742141bbf7f9427c9430aa653d8b92fc83028547af3cb64d7b576a599254f`, `ecd8296f46be822e400adab0aeb9552c5605d828fb2b3c99c56a3e594f91c2fe`.
- All three have valid BPS magic and internal patch CRC; declared JP source CRC `00B31FBB`, HF20 source CRC `52595A69`. Header source/target sizes are 2 MiB. These declarations have not been checked against ROM bytes in this packaging run.
- HF20 translation sources imported by the integrated builder were byte-identical to this repository's root source tree. `source/build_combined.py` import path was updated to reference that tree; the 55-case QA suite now expects an external private save fixture.
- No clean JP ROM was attached; reorganized source build, full Mesen suite and source-to-BPS byte-equivalence were NOT_RUN. The original reports record their earlier successful runs.
- Public files exclude ROMs, emulator/BIOS, SRAM, EEPROM fixtures, savestates, raw RAM dumps, macOS resource forks and raw process traces with private paths. Screenshots, source, project-specific reports and bounded result summaries are retained.
