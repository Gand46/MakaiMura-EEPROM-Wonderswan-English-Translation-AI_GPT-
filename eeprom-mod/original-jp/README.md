# Original Japanese ROM + 2 KiB EEPROM (Phase 4.1E-r2)

**Input:** clean JP ROM (2,097,152 bytes; SHA-256 `ac0c793b30d2de19ff6504d5a205e33f42aeeac724e7c284b48f48fbfbe53ed8`). **Output:** EEPROM-only build, SHA-256 `f5652123b1eee5541a4c761c4818e4872a1ca9f00ce7c106708ee7d5f7044217`; WonderSwan checksum `0x77E3`, save type `0x20` (cartridge EEPROM 2 KiB). The supplied direct JP BPS is 2066 bytes, SHA-256 `76cbadf9c878f57cea71c882f17b1c457642d15ddfae11617f43f2c5d04f0d4a`. It was copied byte-exactly from the external upload and matches the nested source package.

## Apply

Use a CRC-verifying BPS patcher and `patches/Makaimura_Phase4_1E_r2_CUMULATIVO_ORIGINAL.bps` on clean JP. Never apply it to HF20. You can use the preserved `APLICAR_BPS.bat` on Windows with Python 3 or run:

```sh
python3 source/patch_rom.py apply /private/original.ws patches/Makaimura_Phase4_1E_r2_CUMULATIVO_ORIGINAL.bps /private/original-eeprom.ws
```

## Build and behavior

`python3 source/build_project.py /private/original.ws -o /private/rebuilt-original-eeprom.ws --work /private/assembly-original` requires Python 3 and GNU i386 `as`, `ld`, `objcopy`, `nm`. The builder verifies ROM hash, 127 SRAM selectors, hooks, FF caves, target hash and header checksum. Historical Linux/Mesen 2.1.1 build and QA are documented in `docs/original-reports/`. A clean JP ROM was unavailable for a rebuild in this packaging run.

The native 645-byte save record is mirrored at WRAM `0x0370–0x05F4`; 646 bytes are transferred with one padding byte. Pause with START, release it, then hold START about 45 updates to save. In OPTIONS, select EXIT, hold START alone about 45 updates, release the keys, and press A to confirm erase or B to cancel. A short START, A on EXIT, normal OPTIONS values and Tip 10 retain their original behavior in the recorded tests. The option panel has four rows; the modal is rendered before the original sprite finalizer. Details and addresses: `../TECHNICAL_FINDINGS.md`.

Copy an existing compatible 2 KiB cartridge `.eeprom` under the new ROM's basename to retain progress. Back it up before a confirmed erase. The driver writes differential changes and has no power-loss journal or hardware read-back error indication. Emulator results do not certify physical flash timing, endurance or interruption tolerance.

`validation/run_validation.py` requires a private advanced save fixture whose SHA-256 is documented in `docs/original-reports/PRUEBAS_REPRODUCIBLES.md`; no save is published. `LICENSE_BPS_TOOL.txt` applies to the bundled BPS implementation, not to the game.
