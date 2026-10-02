# Packaging verification (2 October 2026)

- Attached BPS and archived HF20 BPS: byte-identical, 28,938 bytes; SHA-256 `3fc350fd39cd1c15608c4e9e791487b9d2f8aa535a73482472e11d4c337a796a`.
- BPS magic `BPS1`, header source/target 2,097,152 bytes, patch CRC32 `1CD2CF17` verified locally; source CRC32 `00B31FBB`, target CRC32 `52595A69` declared by BPS, not checked against ROM bytes here.
- The supplied HF20 audit records a prior independent replay and rebuilt result. **Source-to-BPS byte equivalence was not rerun on the reorganized tree**, because no clean Japanese ROM was supplied here.
- 1257 input file decisions are recorded in `ORGANIZATION_MANIFEST.csv`; source files and necessary legacy BPS dependencies retained.
- Excluded private save/EEPROM files and raw trace files containing private absolute workspace paths. No ROM or BIOS supplied in either analyzed archive.
