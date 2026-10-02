# Makai-Mura (WonderSwan) — English translation, Phase4W HF20

**Status: development/test build; not a release candidate or final translation.** This repository contains the cumulative EN-US localization source for the Japanese WonderSwan game and the evidence available on 28 September 2026. HF20 repairs the first book's unreadable contents heading to `INDEX` using the original 8×16 Latin glyphs. No ROM or game save is included. The independently distributed BPS applies directly to the verified Japanese original; do not patch HF19 or another intermediate build.

## Requirements and patching

| File | Size | SHA-256 | Status |
| --- | ---: | --- | --- |
| Japanese original ROM, supplied privately | 2,097,152 bytes | `ac0c793b30d2de19ff6504d5a205e33f42aeeac724e7c284b48f48fbfbe53ed8` | Hash documented in the supplied HF20 audit; original not available for this packaging run |
| HF20 result, kept private | 2,097,152 bytes | `885eb8268ad8594c1ee5e229db22b0f639da5498a22f262e0d4c0884a1401b51` | Hash documented in the supplied HF20 audit |
| `MakaiMura-Phase4W-HF20-CUMULATIVE_FROM_JP.bps` | 28,938 bytes | `3fc350fd39cd1c15608c4e9e791487b9d2f8aa535a73482472e11d4c337a796a` | SHA-256 computed from the attached patch in this packaging run |

Check the SHA-256 of your legally obtained clean Japanese ROM, then apply the release BPS using a BPS-compatible patcher with source CRC verification. The BPS header declares 2,097,152-byte input and output, source CRC32 `00B31FBB`, target CRC32 `52595A69`. Check the patched private ROM against the documented HF20 SHA-256 above. Do not redistribute the original or patched ROM.

## Building from source

Python 3 is needed for the cumulative build; no external Python package is required by `source/build_phase4w_hf20.py` and `source/validate_hf20.py`. The chain calls the earlier builders and reads **three historical BPS inputs** from `reference/`. They are real build dependencies, not the patch users should install. Historical validators also read three BPS files from `patches/`.

From the repository root, with the correct clean Japanese ROM in a private location:

```sh
python3 source/build_phase4w_hf20.py /private/path/original.ws /private/path/HF20_PRIVATE.ws /private/path/HF20_CUMULATIVE_FROM_JP.bps
python3 source/validate_hf20.py /private/path/original.ws
sha256sum /private/path/HF20_PRIVATE.ws /private/path/HF20_CUMULATIVE_FROM_JP.bps
```

The builder creates a new BPS directly from the Japanese input, checks its replay, and rejects wrong historical preconditions. Compare the generated BPS SHA-256 with the distributed value above and compare the generated ROM SHA-256 with the documented HF20 result. The preserved `BUILD_HF20.bat CLEAN_JP.ws` and `./build_hf20.command CLEAN_JP.ws` write private output in the repository root; move or delete it before publishing any repository changes. Python source was syntax checked on Linux for this package. The supplied audit reports an earlier build and independent BPS replay on Linux. The clean ROM was unavailable during this packaging run, so the reorganized tree was not rebuilt here. The Windows batch file and macOS command launcher were not executed here.

Some QA scripts need Pillow and Mesen 2.1.1 with an external visualization helper; see the original `MESEN_HF20.md` and `REPRODUCCION_RC_GATE_HF20.md`. These third-party tools are not bundled.

## Repository layout

- `source/`: all 82 original Python/Lua builder, extractor, audit and QA files, with paths unchanged.
- `reference/`: three legacy cumulative BPS inputs required by the HF1/HF2/HF11 builder chain.
- `patches/`: three legacy BPS files used by older verification scripts, not the HF20 installation patch.
- `docs/TECHNICAL_FINDINGS.md`: address map, consumers, confidence and source citations.
- `docs/VALIDATION.md`: exact scope and open gates.
- `docs/original-reports/`: the game-specific supplied reports, glossary, emulator instructions and historical route notes, in their original language, retained as primary evidence.
- `docs/records/` and `evidence/`: selected validation records and captures. Raw execution traces with private paths and save data were excluded.
- `docs/ORGANIZATION_MANIFEST.csv`: original-to-public mapping and exclusion reasons for every inventoried file.

## Architecture and findings

The translation combines native glyph rendering, custom atlas tables in `E000`, targeted `mov si` consumer changes, private Demon INDEX data, tile-map edits for controls, and baked tile replacement for confirmation screens. It retains the original 8×16 font grid and computes the WonderSwan header checksum. The earlier patch-derived build stages are necessary for reconstruction; they are not a chain users apply. **[Technical findings, memory map and text consumer table](docs/TECHNICAL_FINDINGS.md)** record exact addresses, methods and their evidence, including uncertain routes.

## Validation and known issues

The attached BPS is byte-identical to the one in the HF20 audit, and its own CRC is valid. The supplied audit documents a prior byte-exact build/BPS replay, checksum `0x5962`, 241 entries in five active `E000` tables, 40 sampled credit frames, a 30-state synthetic matrix, and limited cold-save persistence for the death counter. These are bounded results. Stage exit / a separate “Stage Clear” screen, the complete text and graphic resource census, and global linguistic and visual review remain **NOT_VALIDATED**. `FINAL_APPROVED=false`; HF20 is not an RC. [Validation details](docs/VALIDATION.md).

## Credits and licensing

No developer name or open-source license for the localization sources was established by the supplied materials. Do not assume reuse rights beyond the project owner's authorization. Original game rights remain with their respective owners. The Mesen and visualization binaries, BIOS, save files and commercial ROM are not distributed here. The original glossary and reports are retained without invented attribution.

## Optional cartridge EEPROM modification

The separate [SRAM-to-EEPROM mod](eeprom-mod/README.md) contains two builds: an EEPROM-only variant for the clean Japanese ROM and an HF20-compatible translation plus EEPROM variant. These have distinct cumulative BPS patches and output hashes. Choose the correct one; do not apply the older EEPROM-only patch to HF20. The mod's validation does not close HF20's global translation gates.
