# Outlines, crowd CPU work and sprite pressure, v32

The current checkpoint is `build/checkpoints/roster-audit-v32`:

- MMC3 SHA256: `df61b1e120307c6033a0cffa97e98f63414a509d15f935760f76295df0f1920b`.
- MMC5 SHA256: `61abc0014c6c7bfb6d25e1c905fef377aa69d7a706203f2f6a354ac0a4497652`.

This is accepted component evidence. Complete current-ROM
routes through 2-2 and final all-character recordings remain unfinished.

## Menu and source behavior

Player outlines default OFF and remain optional. Down from the lower roster row
focuses the option; A/Start/Select/Left/Right toggles it. Its foreground is bright
gold in all three nontransparent font indices, distinct from the gray menu.
The choice survives gameplay, area transitions and death.

A screenshot review caught that v31's font uses palette index 1, whose original
gold choice was too dark (RGB 51,53,0). The corrected check rejects v31 on both
mappers and passes v32. v32 changes exactly two ROM bytes per mapper, replacing
the first two foreground palette colors with $28. Runtime addresses, code and
CHR are identical to v31. The exact diff is retained in
`build/checkpoints/roster-audit-v32/binary-diff-v31.json`.

The four v32 menu/selection positives are in
`build/checkpoint-tests/root-menu-gold-v32-positive-a/summary.json`; the matching
v31 negatives are adjacent under `root-menu-gold-v31-negative-a`. Root's 40
focused v31 tests pass with unchanged fixture hashes. The all-roster preview
check removes 115 added black pixels while preserving colored and face pixels.

Samus ordinary contact remains harmful, as in the pinned 2.02 source.
`Character.canStomp` defaults false; `Samus.hitEnemy` uses the base contact path
except for active Screw Attack against eligible enemies. Actual ordinary and
spin-contact tests cover this distinction. A new Mario-style stomp would change
that behavior.

## CPU work

The inherited v30 changes and matched 14,400-update before/after results are
documented in `crowd-performance-v30.md`. They skip unused mask filters, empty
weapon candidate work and no-freeze mapper calls. They retain native enemy AI
and collision results. Four-Goomba Samus logic improves from 60 updates in 90
physical frames to 60 in 60, but that scene still redraws 30 times; six-enemy
logic still slows down.

v31 additionally avoids Link/Simon/Ryu effect passes when all 18 stop/flash/pose
receipts are zero. Stale frozen-pose cleanup is included in the gate. The post
gate runs after deferred Link thrust, which can create an effect in that same
update. Bill/Sophia prepare the actual post-input shot pool, and Sophia queries
its cannon tier at creation. This fixes the retained v30 late-raw-B negative
without changing controller-latch semantics.

The complete v30→v32 matched matrix also agrees on all 14,400 completed-update
rows across 204 gameplay fields (twelve runs, two mappers). Evidence:
`build/profiling/plain-walking-v30-v32-comparison.json`. MM/Samus timing matches
v30. In four-Goomba walking/OFF scenes, MMC5 Link draw calls rise 30→47 per 60
physical frames and Ryu 32→50. MMC3 Ryu rises 30→31; Simon remains 30 on both.
Extra redraws are separated from non-draw CPU costs. Six-enemy scenes still
take 90 physical frames and 30 redraws per 60 logic updates. Bill's layout helper
adds approximately 68–73 non-draw cycles; its benefit is lower sprite pressure.

## Lower sprite pressure with unchanged artwork

The original Bass/Bill pose records and their CHR are retained. New internal
viewport records pack opaque pixels more efficiently into 8x16 sprites. Bass
WALK1/DASH uses a private 1KiB bank and nine parts instead of eleven. Two other
walk frames reuse proven spare pattern pairs. Conservative X/Y/page guards
select original records at viewport edges, preserving exact legacy clipping.
Bill's alternate Lance and fire outfit keep their original art.

The independent v31 fixture checks 4,600 actual DMA images: 2,760 Bass and 1,840
Bill/Lance. It compares source palette/color-index symbols against immutable
v30 across direction, power, star, outline and clipping cases, and verifies
pointer, bank and helper return values. Bass's ordinary buster is also checked
in all 2,760 images while the body switches among the new and old CHR banks.
An initial reference-exporter flip bug is retained as an excluded diagnostic;
the corrected exporter reads immutable v30 and applies horizontal/vertical bits
separately.

An additional 128-arena/8,192-sample ordinary OAM audit shows:

- Bass walking plus one Goomba: peak row pressure 9→8; partial player images
  drop from 30/33 of 64 frames to zero on the two mappers.
- Bill walking plus two Goombas: peak row pressure 9→8; no partial player images.
- Four-Goomba crowds still exceed eight sprites per row and still skip redraws.

These results remove particular overloads; they do not establish zero flicker
or 60 rendered frames/second in every crowd. MMC5 retains the NES CPU speed and
the same eight-sprites-per-scanline hardware limit.

## Broad verification and evidence limits

The initial broad suite executed 729 slots against immutable v32, with frozen
fixtures and launch/tool hashes in
`build/verification/roster-audit-v32-full.json`. It reported 721 passing slots
and eight failures. Its unchanged original diagnostics are preserved in
`build/verification/roster-audit-v32-initial-batch-summary.json` and the full log.

Six negatives came from three older fixture expectations/setup errors:

- Mega Man environment expected a Mario-style stomp. It now checks actual
  source injury, no bounce and an undefeated enemy; both original spring
  launch profiles and earlier environment checks remain.
- Lives portraits counted added black masks despite the new default OFF.
  Expected parts now follow explicit source mask metadata; every one of the
  fourteen character/alternate portrait wrappers was rerun in all power forms.
- Simon's sequential block arenas retained engine 9 and an unrelated inventory
  after earlier real mushroom pickups. Each isolated arena now starts in
  gameplay with coherent source basic/Flame inventory. Actual B attacks and
  every map, PPU, reward and world-palette assertion remain.

The other two reported failures had actual exit 0 and all 32 body-profile
assertions passing: their output said `PASS32`, while the outer verifier
requires `PASS `. Only the missing space changed.

Exactly these four fixture files changed. All 34 affected mapper/test slots
pass again, with unchanged fixtures during the confirmation and identical ROM
hashes. Consolidated coverage is 729 unique emulator slots; the original
failed batch is retained rather than represented as a single all-green run.
Evidence: `build/verification/roster-audit-v32-consolidated.json` and
`build/checkpoint-tests/root-v32-fixture-migrations-confirm-b/summary.json`.

Current source injury gaps, dense-crowd slowdown, final roster routes and
recordings remain separate outstanding work. No physical cartridge acceptance
or complete source parity is claimed.
