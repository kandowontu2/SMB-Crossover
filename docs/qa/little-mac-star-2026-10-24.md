# Little Mac star and new-life repair

The private NT increment follows `parodius-performance-ns`. It repairs two
specific Little Mac defects and leaves the full verification goal open.

The old star crop retained 58 of the original HUD symbol's 73 foreground
pixels. `prepare_little_mac_star.py` now extracts the entire original glyph
from the pinned Punch-Out frame. It fits in the same two hardware sprites by
placing their shared vertical origin at -6 instead of splitting at a 16-pixel
boundary. Palette index 2 remains original white $30. Only the first 64 bytes
of physical CHR page 704 and the two metasprite coordinates change; all body
and portrait graphics are unchanged.

A physical-contact death also exposed a zero-health respawn. `LmClear` stamped
the current life number before `LmEnsure` could recognize a new life. The reset
gate now checks/initializes the life before clearing and stamping area state.

## Evidence and limits

`build/verification/little-mac-star-nt/proof.json` binds the exact private ROM,
source changes, 37 cold identity entries and the following narrower checks:

- Cold Easy and Hard menus followed by explicitly seeded terrain/player/enemy
  arenas at the native GameLoop boundary. Controller head bumps reveal and
  collect a healing mushroom and four flower-replacement stars, exercising
  stock 0/1/2/3, the three-star cap, actual HUD publication, pickup sound queues,
  an earned super punch, contact damage, death and healthy movable respawn.
- The actual uploaded OAM/CHR/palette matches all 73 native star pixels on
  200 Easy and 204 Hard DMA frames. No sprite-limit bypass is enabled.
- Hard 1-1 discovery and independent exact-input replay: 4,084 frames each,
  zero deaths, controllable 1-2, and no player CHR-commit mismatch.

The original 58-pixel failure and the zero-health new-life failure remain
preserved. Initial observer checks were corrected to ignore NMIs which did not
perform DMA and to latch death when it actually occurred, rather than checking
after respawn. These fixture corrections did not change the retained artwork
or health assertions.

Two Easy route attempts fall into a pit near world X1409. Those traces remain
failures; the Hard clear does not certify Easy. Extra-life inventory persistence
and the native invincibility pickup are not yet covered by this fixture. The
Mike art findings, Meta Knight correction request, dedicated audio, remaining
lag/dropout, full MMC3 port and full every-character/every-item matrix remain
open. Public ROMs have not been replaced.
