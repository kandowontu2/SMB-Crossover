# Crowd performance and default outlines, v30

These results cover explicit enemy arenas and focused regression tests. They
do not establish final controller routes, completed roster recordings, or
absence of lag.

## ROMs and changes

Immutable input: `build/checkpoints/roster-audit-v30`.

- MMC3: `2086937f6e3482e66066d6c04216128a899945da18f519bacc4c045f2920468c`.
- MMC5: `f598ed70398da9d4ec118096cafb215ccddd13a9c04d0763d2ffbede77083f7c`.

Outlines default OFF at power/reset. The option and its help line use the gold
menu palette; the existing Down navigation and toggle controls remain. The
choice survives area and life changes. Only extra black mask records disappear;
the character's ordinary dark pixels and face colors remain.

The renderer now skips mask filtering entirely for characters whose generated
records contain no added black mask parts. A cache still handles immutable ROM
records for Samus, Link, Simon and Bass; mutable RAM records rebuild each time.

Other CPU changes avoid the generic weapon dispatcher for unrelated characters,
avoid candidate construction when a weapon pool is empty and cannot create a
shot, and run native enemies directly when no freeze effect exists. The freeze
helper now resides in the native OBJECT bank. Actual AI and collision work is
retained.

## Matched before/after crowd benchmark

`build/profiling/plain-walking-v29-v30-comparison.json` compares v29 and v30 with
the exact same benchmark source (SHA256
`1bf4f10ebfcfc99bb65e5eb3dca94cba0387d0eec1eb42410832be40ed29a992`).
Twelve runs cover six characters on two mappers, standing/walking, outlines
ON/OFF, and zero/one/two/four/six live Goombas. Each scene has 60 completed logic
updates. All 14,400 completed-update rows agree across 204 gameplay observation
fields, alongside their scene/update identifiers. These are authored arenas,
not ordinary-input playthroughs.

Selected MMC5 walking measurements, outlines OFF:

| Character / Goombas | Foreground cycles before | After | Physical frames per 60 updates before | After | Draw calls before / after |
| --- | ---: | ---: | ---: | ---: | ---: |
| Samus /1 |17,360|16,143|60|60|60 /60|
| Samus /2 |19,533|17,974|60|60|60 /60|
| Samus /4 |22,602|20,354|90|60|30 /30|
| Samus /6 |28,461|25,537|90|90|30 /30|
| Mega Man /4 |20,601|19,964|70|62|30 /30|
| Bill /4 |22,568|20,415|60|60|30 /31|

Thus the four-Goomba Samus scene advances game logic at 60 updates/second
instead of approximately 40, but still skips half its redraws. Six-Goomba
scenes still slow down. Draw-call counts are actual function-entry receipts;
the original probe does not count hardware OAM DMA writes. NMI/IRQ bodies are
subtracted from foreground timing, while their entry/RTI overhead remains in
both measurements. Physical-frame and completed-update counts do not depend on
that small attribution detail.

A later light probe explicitly counts writes to $4014 in both immutable ROMs:
`build/profiling/plain-walking-v29-v30-dma-comparison.json`. Its 240 matched
scenes use the same frozen supplement. For the four-Goomba Samus walking scene
on each mapper, 60 logic updates take 90 physical frames, 60 DMA copies and 30
DrawAll calls before, versus 60 physical frames, 30 copies and 30 DrawAll calls
after. Some old copies repeat an earlier image. This improves redraw rate from
approximately 20 to 30 per second while retaining the distinction from 60Hz game
logic. Every six-Goomba walking scene still has 90 physical frames, 60 copies
and 30 DrawAll calls per 60 updates, approximately 40Hz logic and 20Hz redraws.

## Hardware sprite pressure

The independent v29 ordinary OAM audit submitted every player part in all 8,192
samples, with at most 20 total OAM entries. The visible losses come from the
eight-sprites-per-scanline limit and skipped redraws, rather than the 64-entry
OAM capacity. Outlines OFF lowers Samus's four-Goomba row pressure from 14 to 11
parts. The native enemy shuffle rotates which enemies lose priority; it cannot
make 11 simultaneous overlapping parts fit into eight hardware slots.

Bass's walking layers can exceed the scanline limit even with one Goomba.
Packing the same palette/color-index image into fewer hardware parts is under
separate development, with original edge clipping retained. It is not part of
the v30 results above.

## Acceptance scope and known follow-up

Root's 20 focused tests on each mapper pass (40/40), with identical before/after
fixture hashes: `build/checkpoint-tests/root-source-v30-focused-a/summary.json`.
They cover menu control and palette, all roster previews, cache safety, Samus
injury/morph/beam/forms/ceiling contacts, ordinary and spin body contacts,
Bill/Lance injury, native Mario/Luigi physics, Pit clearance and castle pixels.
Another 52 scoped pipeline slots pass; exclusions and corrected authored floor
coordinates are explicit in
`build/verification/scoped-pipeline-v30-evidence.json`. These include 4,224
native-freeze caller cases per mapper, active weapon collision differentials,
empty-pool controls, inventories, and 16 source enemy-effect slots.

Samus has no ordinary stomp in the pinned 2.02 source: `Character.canStomp`
defaults false and `Samus.hitEnemy` delegates ordinary contact to that base
behavior. Her active Screw Attack supplies the aerial body attack; its actual
contact cases pass separately.

A deliberately late raw-B input receipt exposed a real v30 Sophia race: the
empty-pool candidate gate can precede a cannon launch that uses a newer raw
controller latch. The shot then copies a stale attack tier. Both mapper
negatives are retained. v31 must prepare the actual post-input pool and query
Sophia's tier at creation; v30 is not a complete weapon acceptance checkpoint.

Full-roster source injury migration, actual controller routes through 2-2, and
final recordings remain open.
