# HF20 translation + cartridge EEPROM v1

This adapts the EEPROM 4.1E-r2 modification to the exact HF20 translation without overwriting translated bytes. It is a **development/test integration** and does not promote HF20 to release candidate.

| Input | BPS | Output |
| --- | --- | --- |
| Clean JP, `ac0c793b30d2de19ff6504d5a205e33f42aeeac724e7c284b48f48fbfbe53ed8` | `patches/Makaimura_HF20_EEPROM_v1_FROM_JP.bps`, SHA-256 `bf4742141bbf7f9427c9430aa653d8b92fc83028547af3cb64d7b576a599254f` | `abd2440a261dfd8aa1a01f215c829ea08617536e48909c9be54dbe26e6c4b713` |
| Exact HF20, `885eb8268ad8594c1ee5e229db22b0f639da5498a22f262e0d4c0884a1401b51` | `patches/Makaimura_HF20_EEPROM_v1_FROM_HF20.bps`, SHA-256 `ecd8296f46be822e400adab0aeb9552c5605d828fb2b3c99c56a3e594f91c2fe` | Same `abd2440a261dfd8aa1a01f215c829ea08617536e48909c9be54dbe26e6c4b713` |

Both inputs are 2,097,152 bytes. Apply only the BPS matching the input. The first is the recommended **direct cumulative JP→HF20+EEPROM** patch. The second updates an existing exact HF20 copy. Neither requires applying the old 4.1E-r2 patch. Output save type is `0x20` (2 KiB cartridge EEPROM) and WS checksum `0x5D3B`. Verify output SHA-256 before use.

A BPS-compatible patcher with CRC verification works; the preserved `.bat` launchers work with Python on PATH, and `.command` launchers are supplied for macOS/Linux but were not executed on macOS here. From this directory:

```sh
python3 source/apply_patch.py /private/original.ws patches/Makaimura_HF20_EEPROM_v1_FROM_JP.bps /private/HF20_EEPROM.ws
python3 source/convert_save.py /private/HF20.sav /private/HF20_EEPROM.eeprom
```

The save converter copies 2,048 bytes from an exact 32,768-byte HF20 SRAM save without changing its source; it does not repair a damaged record. `.ieeprom` is the console's internal EEPROM, not the cartridge save. Use the output ROM's basename for its `.eeprom` in the emulator's save directory. SAVE/ERASE controls are as described in the [original mod](../original-jp/README.md). No autosave or savestate persistence is added.

## Rebuild from sources

Keep this folder under the Makai-Mura repository root. `source/build_combined.py` imports root `../../source/build_phase4w_hf20.py` and its verified historical BPS dependencies, assembles the EEPROM shims from `source/eeprom/`, and checks that translated bytes are untouched. Run from this folder:

```sh
python3 source/build_combined.py /private/original.ws --out /private/new-hf20-eeprom-build
```

Requires Python 3 and GNU i386 binutils `as`, `ld`, `objcopy`, `nm` (historically tested on Linux x86_64). `BUILD.bat` invokes this builder on Windows when dependencies are available; it was not executed on Windows in this packaging run. Rebuilding and comparing the reorganized folder with the supplied BPS could not run here without a clean JP ROM. The supplied audit documents an earlier clean extraction build, independent BPS replay and matching output hash.

Runtime test scripts remain in `validation/`. To rerun the full 55-case suite privately on Linux, supply Mesen 2.1.1, Pillow, `g++`, the exact JP ROM and a **private 2,048-byte EEPROM test seed**:

```sh
python3 validation/run_suite.py --jp /private/original.ws --mesen /private/Mesen --seed /private/hf20_test_seed.eeprom --out /private/new-validation
```

The supplied historical report records six cold-load checks, 132 identical screen comparisons and bounded synthetic scenes; see `docs/original-reports/INFORME_VALIDACION.md` and [validation scope](docs/VALIDATION.md). The save fixture and raw RAM/save dumps are intentionally omitted from the public folder. Full translation Stage Clear and global text/visual approval remain open. Physical cartridge electrical behavior and power-loss tolerance are untested.
