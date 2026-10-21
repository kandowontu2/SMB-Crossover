# v29 focused rendering and injury checks

This is focused component evidence. It does not claim a complete acceptance
suite, all-character playthrough, final capture, or zero lag.

Immutable ROMs live in `build/checkpoints/roster-audit-v29`:

- MMC3 SHA256 `3b79c999cce7945a0f7b6d30aa36d6e3e8d2e8c0064b6ab4f8c41ed5a90713ed`.
- MMC5 SHA256 `d2c7d5c4836045f4e6bd305036038afee16b3f98d3b6e0a2943871572ec04df0`.

## Outlines preference and renderer

Player outlines now default OFF after power/reset. The menu option uses a
distinct gold background palette, remains reachable by Down, and toggles with
the existing controls. Area changes and death retain the preference.
`player-outlines.lua` exercises actual menu inputs, ON/OFF text, the separate
cursor, palette/attribute bytes, previews, launch and respawn on both mappers.

`player-outlines-render.lua` traverses all twelve roster positions with normal
controller input in each option state. Actual DMA OAM/CHR/palette decoding
finds115 extra black pixels removed per mapper; colored and face pixels match.
Native Mario and Luigi bypass filtering because their native sprites have no
added mask layer.

`PlayerRemoveOutlines` caches only immutable C000–DFFF ROM records, keyed by
their full pointer and active C-window PRG bank. Mutable RAM records rebuild
and invalidate this cache. The helper moved to SAMUS to leave renderer space.
`player-outline-cache.lua` verifies400 exact-byte real helper calls per mapper,
including six independently authored mutable-pose receipts, changed bank keys,
and cold/warm timing with interrupt time excluded:

| Mapper | Warm helper cycles | Forced rebuild | Changed-bank rebuild |
| --- | ---: | ---: | ---: |
| MMC3 |83.2|726|744|
| MMC5 |83.2|742|760|

These are helper costs, not whole-frame improvements. Walking among native
enemies still needs separate CPU and physical sprite-overload measurements.

## Samus injury source behavior

The pinned2.02 `Samus.as` supplies a250ms recoil, attacker-relative185 source
VX capped to150, a grounded250 source upward boost, retained airborne VY,
700 dry/400 submerged gravity,450 fall cap,25ms flicker, and a separate1250ms
protection interval. `AnimatedObject.gravityPull` skips its first gravity pull
when the hit starts grounded. `exitMorphBall` keeps ball form under a low roof;
a successful grounded exit lifts by10 source pixels (5NES pixels).

`samus-injury-202.lua` checks32 actual-impact arenas per mapper,448 independent
numeric recoil updates each, facing independent of attacker side, ground/air,
wet/dry/surface/page seams,14 fully locked movements before elapsed update15,
75 later protection updates, rational flicker phase, late parsed-input masking,
injury sound queue, and an unrelated moving enemy. The fixture ends when the
protection window expires. The original longer fixture correctly encountered
a newly spawned ordinary level enemy after its protection ended; that was not
a recoil regression. Original diagnostics are preserved.

The corrected first-ground gravity oracle reproduced a v28 negative on both
mappers (-1.9861 instead of -2.0833NES pixels/update). The v29 helper skips
exactly that first pull; a new scoped Samus flag records this source ordering.
`samus-injury-morph-202.lua` adds32 actual-impact cases per mapper, checking
blocked/open ball exits, full/short collision returns, art, exact initial lift,
and the first gravity/integration ordering. Both fixtures pass v29.

Samus has no ordinary stomp in2.02. The separate Screw Attack body-contact
tests retain the source aerial attack; ordinary contact remains injurious.
Noninteractive head-block activation and non-enemy hazard recoil origins still
need a separate source audit; these component positives do not cover them.

## Retained checks and evidence boundaries

`build/checkpoint-tests/root-source-v29-focused-validation.json` consolidates
40 passing actual test slots across both mappers. These include native
Mario/Luigi39-trial physics, Pit48-case roof clearance, Samus432 head contacts,
crouch/shoot art in all three forms, real beam pointers, acquired passives,
ordinary84-case contacts, spin15-case contacts, Bill/Lance one-hit injury,
native castle art, and Bill/Lance HUD splits in both outline states.

Two reference-data-table invocations were accidentally queued by the focused
runner and stopped. They are explicitly excluded, with raw nonzero results
retained; the executable `samus-crouch-power-forms` wrapper passes separately.
Every executed batch retains before/after fixture hashes.

MM/Bass source hurt effects and their58 focused positives are separately
recorded in `build/verification/mm-bass-injury-v29/summary.json`, packing
invariants and art totals. Source Link/Simon/Ryu injury migration remains open.
All current-ROM all-character route proofs and final recordings remain open.
