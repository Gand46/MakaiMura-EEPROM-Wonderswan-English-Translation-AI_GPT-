# Makaimura EN-US Phase4W-HF11 — Demon INDEX private localization report

Date: 2026-09-20
Status: **stable development baseline; not global Release Candidate**

## Change

HF11 closes the pending Demon INDEX-name regression introduced when HF1 correctly restored the shared Library structures.

The old Phase4W implementation changed shared data at `D000:32D0-366E` and reused `D000:FF77-FFFF`. Those structures are also consumed by other Library screens and caused cross-screen corruption. HF11 does **not** restore those changes globally.

Instead HF11:

- reconstructs the known Phase4W English Demon-name resource privately in unused `E000` ROM space;
- relocates its pointer tables explicitly;
- redirects only the Demon INDEX consumer and its three list-render calls to the private resource;
- leaves the shared `D000` structures byte-identical to HF10;
- preserves token 1 as the native locked `?` glyph rather than the old duplicate `N`, preventing the historical `NNNNNNNN` defect;
- expands the locked mask to 10 `?` cells so no long English name leaks from underneath;
- repacks all 42 English names into fixed 10-cell fields padded with native blank tokens so scrolling cannot leave stale trailing letters.

## Demon names restored

1. ZOMBIE
2. WOO
3. WOODY PIG
4. ORC MAN
5. GARGOYLE
6. CROW
7. MAD CROW
8. VULTURE
9. MAD SPIDER
10. GREEN MSTR
11. GRILLIAN
12. BAT
13. GHOST
14. SKULL FLWR
15. SEIREN
16. DARK ARTHR
17. RED ARREMR
18. FIRE BAT
19. PETIT GOB
20. PETIT DEV
21. FLYING KLR
22. BLUE KILLR
23. BELIAL
24. MAGICIAN
25. MIMIC
26. ROSE BUD
27. ARMOR ZOMB
28. PIRATE
29. ROCK TURTL
30. MAD DOG
31. REAPER
32. FACE TOWER
33. MAN EATER
34. POP HAND
35. FRANK ZOMB
36. ROCK MONST
37. DAGON
38. EFREET
39. NIGHTMARE
40. RANGDA
41. TIAMAT
42. AZAZEL

The shortened forms are retained from the previously integrated translation because the INDEX field is limited to 10 cells. They remain candidates for the later terminology/polish pass, not evidence of missing integration.

## Runtime QA

Emulator: **Mesen 2.1.1**.

### Normal locked-state build

`SCRIPTED_NATURAL` navigation from boot to `LIBRARY -> DEMONS -> INDEX` confirms:

- `N0001` etc. remain intact;
- locked entries render as ten `?` glyphs;
- no `NNNNNNNN` corruption;
- no English-name suffix leaks through the mask.

Evidence: `evidence/HF11_DEMON_INDEX_LOCKED_RUNTIME.png`.

### English-name coverage

A **QA-only synthetic unlock** changes one conditional jump in a temporary ROM after the final HF11 build. It does not alter the distributed HF11 ROM or BPS. This is used only to expose all names without requiring a full playthrough.

The runtime sweep reaches the full list and confirms N0001-N0042, including the terminal page N0037-N0042. All names render without binary garbage, clipping or stale-tail residue.

Evidence:

- `evidence/HF11_DEMON_INDEX_UNLOCKED_QA_TOP.png`
- `evidence/HF11_DEMON_INDEX_42_NAMES_RUNTIME_QA.png`
- `evidence/HF11_NAMES_END_37_42.png`

Access method for this coverage: `SYNTHETIC_STATE / controlled conditional override`, not natural gameplay unlock progression.

## Binary isolation

HF10 -> HF11:

- changed bytes: **1392**
- unexpected changed offsets: **0**
- permitted changes are limited to four Demon INDEX consumer immediates, the private `E000:C700-CCED` resource, and the WonderSwan checksum.
- shared `D000:32D0-366E` and `D000:FF77-FFFF` remain unchanged from HF10.

Audit: `build/HF10_HF11_DIFF_AND_BPS_AUDIT.json`.

## Integrity

Clean Japanese base SHA-256:
`ac0c793b30d2de19ff6504d5a205e33f42aeeac724e7c284b48f48fbfbe53ed8`

HF10 SHA-256:
`60f9a85690e31f3cd0ce71da7da28db7c553ac68af0fe8773682c47a4a96f6f2`

HF11 SHA-256:
`b6379ffbdb8eb5caf8bb587cbc742149b63bfc8f4ac6af920affd29f32e45ff4`

WonderSwan checksum:
`0x6C87` stored = `0x6C87` recalculated.

Cumulative BPS JP -> HF11 SHA-256:
`3c9034c9ebd59cd93ea140d5020b2c16b527081564477d9cf96c4af4f6541984`

Incremental BPS HF10 -> HF11 SHA-256:
`5dac98aa039fb7bbed85a28fe4e05ad4325875be16c2dd1fc9c3aca1c312b638`

Both BPS round-trips are byte-identical PASS.

## Remaining project work

HF11 is not a global RC claim. The next phase remains the broader residual-Japanese census plus directed Stage Clear / Game Over / Continue / late-game / ending / credits and linguistic/visual consistency review.
