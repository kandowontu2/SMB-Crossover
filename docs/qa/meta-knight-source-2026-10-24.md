# Grounded NES Meta Knight correction — private NU

This supersedes the flight and flat-blue Meta Knight implementation in NH.
The original Kirby's Adventure boss does not use the invented player-flight
mode. His native body uses pink `$36`, purple `$14`, and ink `$0F`; the sword
uses a separate source palette. Intro cloak frames are not flying frames.

## Playable controls

| Input | Current private MMC5 behavior |
| --- | --- |
| A | Ground jump; fresh A/Up in the air cannot initiate flight |
| B on the ground | Single sword slash |
| Up+B on the ground | Triple slash |
| Left/Right+B on the ground | Charging sword attack |
| Select on the ground | Lunge |
| B in the air | Eight-pose spinning sword attack |
| Down+B in the air |32-update hover/windup, downward strike, landing recovery |

Attacks lock their starting facing. Sword collision derives from the opaque
source sword pixels for the current pose, with signed world coordinates.
Question blocks use one strict tip-cell transaction; bricks retain native
debris and sound, and foundation/adjacent protected terrain remain intact.

The former Kirby jump became a progression trap when flight was removed:
the preserved negative run stalls at the tall1-1 pipe. NU retains the port's
`-$0390` takeoff, uses Meta's observed `+$0015` Q8.8 gravity, and removes
Kirby's forced23-update apex. Its fixed76-pixel arc clears SMB's64-pixel pipes.
This stronger takeoff is an explicit playable-port accommodation; the native
boss script's normal takeoff is `-$0300`. It is not a claim of exact boss AI
physics. There are no midair jump resets, inflation or sustained flight.

Six health points remain. Naturally alternating mushrooms and flowers heal
two, capped at six; they do not grant copy abilities or sword tiers. Ordinary
contact removes one health. A real death consumes one life and restores six
health on a movable respawn. Easy retains ordinary enemy stomps; Hard requires
the sword rather than granting ordinary body stomps.

## Native art and source boundary

User-local source: Kirby's Adventure (USA) (Rev1), SHA256
`a7a742f5288cd4ab220f530ee7c8d0e3714b8bf107e89c9bf03039217fec5829`.
Original spritemap bank `$31`, table `$8000`, sprite-window1 physical CHR `$A4`.
The original room was entered at its native initializer and the offered sword
was collected by controller inputs. Native boss AI/scripts/art were not patched;
Kirby's health was replenished to allow observation. Those are source-observation
arenas, not original-game campaign clears.

The independent decoder compares all90 linked poses against25,245 composited
source pixels.35 captured original boss poses additionally verify136 visible
hardware OAM parts, physical CHR and body/sword palettes. Natively offscreen
parts are counted separately rather than mistaken for missing art. Complete
eight-frame spin and upward-slash art fit in three2KiB pools. Kirby's first16KiB
and the three health glyph indices are unchanged; the family remains inside
its actual24KiB linked allocation.

Body colors are exact. Source sword shades `$30/$37/$17` are explicitly mapped
to the stable world weapon palette `$30/$27/$16`. Sword hue parity is therefore
incomplete. The attack input mappings, shorter boss recovery waits, bounded
player spin and stronger jump are adaptations. The current audible sword SFX
uses the SMB fallback, not the original `$3A` sound. Dedicated source sword
audio and exact sword hues remain fidelity limitations; no perfect-native
implementation is claimed.

The annotated source research in Nathan-R-Og/kirbyadventure `src/prg/bank2b.asm`
identifies the single/triple/lunge/spin/strike/charge scripts. Source actions and
observed original velocity traces are retained under
`build/verification/meta-knight-source-nu`. No reference ROM is downloaded or
included in the source snapshot.

## Verification

Private MMC5 ROM SHA256
`b90ede8fa3afaceefe3ef3090424f4d6b6662c139a1a3d6df52e64b7ec00b240`.

- Both facings and Easy/Hard: fresh A/Up cannot fly/reset gravity; full pipe
  clearance; six actual sword attacks each execute a native enemy defeat;
  downward strike holds its windup height before falling. These are explicitly
  seeded arenas at the real GameLoop boundary, not campaign claims.
- Both food types emerge after controller head bumps, remain visible before
  pickup, heal/cap correctly, and queue their pickup sound. Sword question,
  brick/debris/noise and protected-foundation cases pass. Six real contacts,
  death and healthy movable respawn pass. Interrupt work/graphics ownership is
  checked throughout.
- Cold-menu1-1 discoveries and independent fixed-input replays pass Easy
  (5285frames) and Hard (5544frames): zero deaths and movement restored in1-2.
  Every replay frame is retained losslessly in the verified external evidence
  location; actual player CHR publication is checked on every eligible frame.
- Separate read-only port DMA/pixel/scanline inspection passes2964body frames
  and9439body/sword parts with zero priority mismatches.352starts at slot0 and
  439ends at slot63 per mode explicitly cover safe ring boundaries. Full native
  jump-pose timing4/15/9/6/5 is observed in both facings before settling34/35.
  Staging OAM dumps alone are not described as hardware proof.
- The expanded-only priority selector moved into the cold Kirby bank to fit
  bank4.8064actual native draws compare old/new Bill and ordinary-Kirby rotor
  outputs over all2016legal input pairs per identity: byte-identical. This is
  a seeded-boundary differential, not a performance or campaign certificate.

An independent hardware audit exposed an error in the first art checker:
it composed source and packed descriptors using the same assumed priority.
Native OAM is forward-order; the port emitter is descending-order. The v5
negative has905wrong-composite frames per mode despite every part being
present. The corrected packer reverses Meta's records, and the checker now
models actual descending emission. The former v4/v5 composition passes are
withdrawn. The separate ring-pivot guard skips positions inside Meta's body
span before drawing; it retains allocation and guest flicker while preventing
slot63/0 from reordering the body again.

The native falling/jump sequence also replaces the old permanent cape pose38.
That mostly black source frame could appear almost invisible underground;
actual palettes/CHR were intact. It is now a brief native transition followed
by pose34, with no invented recoloring or silhouette changes.

Preserved negatives include incomplete original-room harnesses, old66-pose
flight behavior, the pipe-stall route, and component placement mistakes that
initially placed a falling Goomba below the moving sword. Those fixture
corrections did not require weakening enemy-defeat assertions. Final attack
checks require a sword-owned native defeat, so an Easy stomp cannot mask a
missing sword collision.

The37-identity final matrix, complete powerups/levels/audio/performance work,
and full-roster oversized MMC3 port remain open. The public33-identity ROMs
are unchanged; this private MMC5 repair does not certify that other build.
