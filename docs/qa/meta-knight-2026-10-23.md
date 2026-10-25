# Meta Knight alternate

**Historical NH checkpoint.** The current private MMC5 correction is documented
in `meta-knight-source-2026-10-24.md`. It removes flight and the held-B combo,
restores the native body palette, and replaces those inputs with six adapted
NES boss attacks. The old flight controls and cloak mirroring below are retained
only as historical behavior. The40KiB reservation claim below was incorrect:
the linked Kirby family reservation is24KiB. Older clears do not certify NU.

Meta Knight shares Kirby's selection slot. Highlight Kirby and press Select;
press Select again to return to Kirby. The highlighted portrait, name, lives
portrait and in-game HUD name follow the selected alternate. Both full-roster
cartridges include him; the standard 14-identity cartridges are unchanged.

## Controls and rules

| Input | Behavior |
| --- | --- |
| A | Jump; press again in the air to start flight, then hold to rise |
| Up | Start/continue flight |
| Down | Crouch on the ground; cancel flight in the air |
| B | Sword; held B chains slash, thrust and slash |
| Left/Right | Move and face; an active sword swing keeps its starting direction |

The sword works on the ground and in the air, defeats enemies, breaks bricks
and activates question blocks. Its block probe visits the actual sword-tip
cell, retaining the existing protected-terrain rules and native block/reward
animations. It does not borrow a large charged-buster collision rectangle.

Meta Knight has six health points. Mushrooms and flowers restore two, capped
at six, and play the pickup sound. They do not change his sword or grant copy
abilities. Ordinary damage removes one point; the sixth hit starts death.
Easy allows the shared ground-character enemy-stomp policy. Hard retains
contact damage rather than granting ordinary foot stomps. His sword and health
rules are otherwise the same in both settings.

## Source and adaptations

The original NES Meta Knight spritemap is bank $31, table $8000 in the user's
Kirby's Adventure (USA) (Rev 1) ROM, SHA256
`a7a742f5288cd4ab220f530ee7c8d0e3714b8bf107e89c9bf03039217fec5829`.
The packer preserves original pixels, tile flips and sprite offsets. The
original cloak-intro frames receive exact mirrored counterparts for facing
left during flight. No new wing sprites were drawn. Player control, sustained
flight and the chaining input are adaptations: NES Meta Knight is a boss,
not a selectable player in Kirby's Adventure.

The second native sprite window begins at tile $80. Rebasing those tile
numbers correctly avoids selecting unrelated enemy graphics. The additional
8 KiB fits inside Kirby's existing 40 KiB graphics reservation, including in
the oversized MMC3 cache. It uses no additional WRAM allocation.

Kirby now has source-game area/event tracks, and Meta Knight uses the original
boss theme for normal play. Fourteen area/event selections for each identity
were checked against 400 consecutive source APU-shadow frames on both mappers.
The streamed soundtrack currently reproduces pulse, triangle and noise;
DPCM percussion is omitted. Captures are retained losslessly outside the
workspace. No exact musical loop boundary was proven for these captures, so
the retained full capture repeats when exhausted. This is not a claim of
complete original-audio parity or a repair of the rest of the roster's music.

## Validation

Evidence is under `build/verification/meta-knight-nh`. Component tests start
through the real menu, then explicitly seed separate interaction arenas;
they are not campaign clears. They cover the selected name/portrait, sword
enemy and question-block contacts, protected terrain, both health foods and
sounds, flight/cancellation, six-hit death and interrupt bank restoration.
The normal native 1-1 scenery is reviewed separately from these arenas.
Artificially placing a block over a hill without replacing the existing
nametable attribute produces a green fixture block; that fixture screenshot
is not evidence of a random block in a controller-only playthrough.

The 1-1 run exposed a shared Kirby-family head-probe bug beside tall pipes:
an edge probe could sample one pixel into a side wall before horizontal
collision resolved, and move the player down as though hitting a ceiling.
The wider edge probes now use the pre-step X, retaining normal ceiling
contacts. Meta Knight subsequently clears the surface route into controllable
1-2 with zero deaths on each full-roster mapper, using separately replayed
controller inputs. This does not certify every level or every Hard route.

The build also includes the pending SMB3 camera/P-meter/statue-damage repairs
and the turtle dispatch, health-HUD cache and fast-landing Easy-stomp repairs.
The SMB3 native form/pickup/statue-race suite and all four turtle fast-landing
fixtures pass. The four-Goomba turtle benchmark improves substantially over
the original 30 skipped draws per 60 updates, but does not eliminate all lag.

The earlier `full-roster-nd` checkpoint remains available. Its 18 recorded
surface-route clears apply to that recorded ROM, not automatically to this
new build. Prepared assets build without downloading reference ROMs or NSFs.
