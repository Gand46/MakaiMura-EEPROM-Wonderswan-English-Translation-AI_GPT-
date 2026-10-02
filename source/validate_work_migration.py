#!/usr/bin/env python3
"""Verify an HF11 migration against the clean JP ROM, without an emulator."""
from pathlib import Path
import hashlib
import json
import sys

from build_phase4w_hf11 import build
from build_phase4w_hf2 import ws_checksum
from verify_bps import apply

ROOT = Path(__file__).resolve().parent.parent
BASE_SHA = 'ac0c793b30d2de19ff6504d5a205e33f42aeeac724e7c284b48f48fbfbe53ed8'
TARGET_SHA = 'b6379ffbdb8eb5caf8bb587cbc742149b63bfc8f4ac6af920affd29f32e45ff4'
PATCH_SHA = '3c9034c9ebd59cd93ea140d5020b2c16b527081564477d9cf96c4af4f6541984'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    if len(sys.argv) != 2:
        raise SystemExit('usage: python3 source/validate_work_migration.py CLEAN_JP.ws')
    base = Path(sys.argv[1]).read_bytes()
    if sha(base) != BASE_SHA:
        raise SystemExit('FAIL: clean JP SHA-256 mismatch: ' + sha(base))
    patch = (ROOT / 'patches/Makaimura_EN_US_Phase4W_HF11_CUMULATIVE_FROM_JP.bps').read_bytes()
    if sha(patch) != PATCH_SHA:
        raise SystemExit('FAIL: BPS SHA-256 mismatch: ' + sha(patch))
    rebuilt, hf10, _ = build(base)
    applied = apply(base, patch)
    checks = {
        'base_sha256': sha(base),
        'bps_sha256': sha(patch),
        'target_sha256': sha(rebuilt),
        'rebuild_matches_bps': rebuilt == applied,
        'expected_target': sha(rebuilt) == TARGET_SHA,
        'size_2_mib': len(rebuilt) == 2097152,
        'wonderswan_checksum': int.from_bytes(rebuilt[-2:], 'little') == ws_checksum(rebuilt),
        'shared_d000_table_unchanged_from_hf10': rebuilt[0x1D32D0:0x1D366E] == hf10[0x1D32D0:0x1D366E],
        'shared_d000_tail_unchanged_from_hf10': rebuilt[0x1DFF77:0x1E0000] == hf10[0x1DFF77:0x1E0000],
    }
    print(json.dumps(checks, indent=2))
    if any(v is False for v in checks.values()):
        raise SystemExit('FAIL')
    print('PASS: binary migration. Runtime, translation coverage and visual design remain separate gates.')


if __name__ == '__main__':
    main()
