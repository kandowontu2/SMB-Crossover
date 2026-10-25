# Private Parodius Bell and pickup integration

This checkpoint extends the existing native Octopus, TwinBee and Pentarou
component. It remains a private MMC5 integration, with published MMC3/MMC5 ROMs
unchanged. Candidate SHA256:
`c6369dbd1e56b55751fe6ba7a06c25f48292c97b9a0a1d9be67f6fd0ddce15d3`.

## Implemented behavior and repairs

The original cartridge's 352 Bell/pickup instructions now drive roulette,
White Bell1UP, Blue Super Bomb, Red's three crest shots and their full retraction
timers. Big uses the existing original morph, invincibility and expiry code;
its larger body collision box now agrees with that state. Gaining a life no
longer resets equipment. Super Bomb defeats SMB enemies through the ordinary
enemy defeat path, applies bounded Bowser damage, and restores every captured
palette byte after its flash.

Only VBlank captures the live palette. A resident nine-byte gateway enters
the banked helper without using the foreground far-call scratch. NMI retains
and restores the original C bank. Sprite palette bytes are queued before
background bytes, respecting the $3F10/$3F00 aliases; the earlier reverse order
could undo the backdrop flash. Native palette backpressure is preserved.

The original group1 capsule/Bell/score records are decoded by the same original
renderer oracle as player weapons. Capsules retain each character's source
shape, including its ordinary/Big skin consistency. Colors are explicitly
quantized into the available shared NES palettes. No enemy palette is replaced.
Gold, Blue, Red, White and flashing pickups have separate source poses/colors.
Gold bonuses progress through500/1000/2500/5000/10000, show the source score
sprites for40 native updates, and cap their streak at10000.

One actual graphics-budget problem was removed: white, yellow and red all fit
the existing world palette2. Capsules and score digits now use one sprite per
original part instead of separate overlapping color layers. Score digits retain
the original3–5 sprites; each isolated pickup fits the eight-sprite scanline limit.
Player/world sprites still share the hardware limit.

Private weapon CHR moved from window4 into6, and pickups use7. This preserves
the original Bowser/Podoboo window4 and mouse window5. Source skin/weapon/pickup
pools fit the existing192KiB reservation; no CHR or WRAM expansion was added.

Physical Bell metadata initially borrowed unused Punch owners, but the native
weapon-clear loop sweeps all28 entries. It now occupies unused padding between
the original28-byte arrays instead. Twenty state bytes survive actual native
full clears. The proposed MMC3 overlay has matching free padding; production
MMC3 Parodius relocation is still outstanding.

## Evidence

All current integration evidence is under `build/verification/parodius-bells-nm`:

- `final-differential`:272 cases and440,792 instructions per proposed mapper
  layout match the source CPU's Bell/pickup state. Palette, terrain and damage
  delivery are explicitly controlled host callbacks in this oracle.
- `parodius-native-ni/art-oracle.json` (in the adjacent verification directory):
  449 original group0/group1 records, four palette cases each,1,796 cases total.
- `packed-art-proof.json`:664 packed source-pixel cases with declared color
  quantization, including capsules, Bells and score records in every pool.
- `final-components-v3`:each alternate passes native movement, equipment limits,
  both guns, actual SMB block/enemy contacts, protected terrain, sprite-budget
  reservation and status-bar clipping checks. These arenas seed state explicitly.
- `final-bells-v3`:physical White/roulette/Blue/Red/Big pickup arenas, exact
  palette restoration, three Red shots and their complete lifecycle, and1,536
  native updates covering Big expiry. Actual palette reads are checked in VBlank.
- `physical-pickups-v6`:15 actually uploaded source-pixel poses per alternate
  (45 total), five physical Gold pickups with score progression/expiry, native
  weapon clears, and controller shots exercising all16 Bell color changes.
  Gold takes four shots; special colors take one. This gallery explicitly
  positions actors and holds a Bell in a firing lane; it is not a campaign.
- `final-entry-group1/2/3`:all36 identities enter through actual menus and pass
  ordinary movement and interrupt ownership checks on this candidate.
- `replay-octopus-v3`, `replay-twinbee-v3`, `replay-pentarou-v3`:independent fixed
  controller replays clear Easy surface1-1, with zero deaths and restored1-2
  movement. Their input streams are retained and bound to this candidate hash.

Actual rendered pickup images were reviewed. The screenshot capture now waits
for the uploaded OAM to reach a completed video frame; earlier gallery PNGs
showed the preceding form despite the new OAM being correct. Rendered body,
weapon and campaign samples are bounded checks, not a claim of reviewing every
video frame or every powerup in every character's final campaign.

## Remaining requirements

Source SFX/music, native dynamic palette overrides, shield contact geometry,
hero-change pickups, exact final Bell disappearance and negative-X lifetime,
drop-policy review, oversized MMC3 integration, and full campaign/performance
coverage remain. The other requested roster work, including Roll, is not
complete. See `final-verification-plan-2026-10-23.md` for the unfulfilled final
full-roster/every-powerup gate. The goal remains active.
