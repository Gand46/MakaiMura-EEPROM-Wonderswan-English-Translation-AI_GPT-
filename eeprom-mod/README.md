# Makai-Mura SRAM-to-cartridge-EEPROM mod

These are **two separate 2 KiB cartridge EEPROM builds**, organized within the HF20 translation repository. Neither build contains an original or patched ROM. The clean Japanese ROM is 2,097,152 bytes, SHA-256 `ac0c793b30d2de19ff6504d5a205e33f42aeeac724e7c284b48f48fbfbe53ed8`. Check the hash before patching.

| Variant | Input | Direct cumulative BPS to apply | Output SHA-256 | Status |
| --- | --- | --- | --- | --- |
| [Original Japanese game + EEPROM 4.1E-r2](original-jp/README.md) | Clean JP `ac0c793b30d2de19ff6504d5a205e33f42aeeac724e7c284b48f48fbfbe53ed8` | `original-jp/patches/Makaimura_Phase4_1E_r2_CUMULATIVO_ORIGINAL.bps` | `f5652123b1eee5541a4c761c4818e4872a1ca9f00ce7c106708ee7d5f7044217` | Tested development mod; no hardware electrical certification |
| [HF20 translation + EEPROM v1](hf20-compatible/README.md) | Clean JP `ac0c793b30d2de19ff6504d5a205e33f42aeeac724e7c284b48f48fbfbe53ed8` | `hf20-compatible/patches/Makaimura_HF20_EEPROM_v1_FROM_JP.bps` | `abd2440a261dfd8aa1a01f215c829ea08617536e48909c9be54dbe26e6c4b713` | Tested integration; HF20 translation still not RC |

For a ROM **already patched to exact HF20** (`885eb8268ad8594c1ee5e229db22b0f639da5498a22f262e0d4c0884a1401b51`), an optional BPS `hf20-compatible/patches/Makaimura_HF20_EEPROM_v1_FROM_HF20.bps` produces the same HF20+EEPROM output. Apply **one** patch. The EEPROM-only 4.1E-r2 patch targets JP and would collide with HF20 translation resources if forced onto HF20.

All patches are cumulative for their stated source, except the explicitly marked HF20-to-combined alternative. The ROM base is supplied locally by the user; no download links are provided. The project does not include BIOS, emulator binaries, SRAM, EEPROM saves or savestates.

The two variants have distinct source trees and test reports. `hf20-compatible/source/build_combined.py` reuses the translation builders in the repository root `source/`; this subfolder belongs inside this repository. GNU i386 binutils are required to rebuild both variants; a BPS patcher is sufficient to apply an existing patch. See the variant READMEs and [technical address map](TECHNICAL_FINDINGS.md).

Original source and reports include an MIT notice for the bundled BPS utility. That notice does not grant rights to the commercial game or automatically license all translation/mod code. No broader project license has been established by the supplied materials.
