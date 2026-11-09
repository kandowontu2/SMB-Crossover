# Shared gameplay cadence on MMC5

The previous public ROM `c8bd2e2c` applied shared work reductions to the native
game loop, terrain parser, platform pairing, and ordinary player contact.
The paired contact proof measured 63–84 cycles saved per update for Mario and
75–100 for the other sampled owners, including Samus and Mini Mario, in the
same three- and four-contact scenes. The shared game-loop tail separately
saves 27 cycles per completed call. Mini Mario's actual Downloads 1-1 route
has 3,494 active video frames, 3,494 game updates, and zero missed controller
reads. The replay reports loading and stage transitions separately.
[Delivery and scoped results](continuation-current.json)

## Samus and Bill opening replays

Each replay starts from the title in Easy, with cheats off. After 120 active
idle frames with no enemies, it holds Right from world X40 to X258. The walk
includes the first natural Goomba. Both characters reach 94 ordinary player
contact calls across 175 walk updates. The exact previous ROM `df03fc35`
differs from current `c8bd2e2c` by the latest ordinary player contact change.
For each character, every measured field matches between the two images.

| Character and phase | Physical frames | Main entries | Missed controller reads | Lag NMIs | Frames with no Main entry |
|---|---:|---:|---:|---:|---:|
| Samus idle | 120 | 120 | 0 | 0 | 0 |
| Samus walk | 181 | 175 | 22 | 22 | 6 |
| Bill idle | 120 | 120 | 3 | 3 | 0 |
| Bill walk | 184 | 175 | 29 | 29 | 9 |

Input polling and game-loop entry can fall on different sides of the video
frame boundary. Both counts are recorded so a catch-up Main entry cannot
hide a missed controller read. The paired samples show no cadence change from
the latest contact optimization in these opening routes.
[Controller observer](../../tools/audit/shared_gameplay_cadence_1110.lua)

The current Bill replay also recorded the actual interrupted address for all
32 active lag NMIs. The three idle samples interrupt PRG63 `$B42B` and `$B446`,
and PRG4 `$A525`. Of the 29 walking samples, nine interrupt PRG4, seven PRG3,
six PRG2, four the RAM farcall trampoline, and one each PRG63, PRG86 and PRG126.
These are deadline locations. The code running when NMI arrives can be a
consumer of earlier time in the same update. The three idle misses occur
before the first enemy or any projectile.
[Deadline observer](../../tools/audit/shared_gameplay_nmi_1110.lua) ·
[Interrupted PCs](../../build/shared-gameplay-nmi-1110/capture/deadlines.json)

The shared shot-bank selector remains active with four empty projectile
slots because it also maintains the logical CHR shadow. An in-memory trial
at PRG78 `$BC9A` skips the type comparisons for empty slots and preserves
the ordered CHR shadow writes. It saves 24 cycles with all four slots empty
and can add up to eight with all four occupied. The trial matched registers
and publication writes in 13,156 CPU controls and passed 80 IRQ or lag-NMI
pairs. In native runs of that change alone, Bill missed two idle reads and
Samus missed 21 walking reads.
[Shot-only native replay](../../build/shared-shot-scan-native-1110/proof.json)

## Sparse world draw and projectile scan

The released `f33c7b19` nightly avoids a second native scan when the current
enemy IDs cannot draw firebars or small lifts. Firebars and lifts still use
their existing renderer. The combined CPU proof verifies 544 cold-entry
updates for Mario, Bill, Samus and Rogue Dawn with exact game state and sprite
output. The world change saves 80 cycles on those updates. The combined
change saves 104 cycles in the Mini opening fixture. Real positive firebar
and small-lift OAM and the existing native actor IDs were checked.
[Combined CPU proof](../../build/native-sparse-world-draw-1110/combo.json)

| Easy opening | `c8bd2e2c` missed reads | `f33c7b19` missed reads |
|---|---:|---:|
| Bill idle | 3 | 1 |
| Bill walk | 29 | 28 |
| Samus idle | 0 | 0 |
| Samus walk | 22 | 18 |

Samus's walk also went from six to five frames with no game-loop entry.
The identical Mini controller cleared the full nonshortcut 1-1 and rode all
three lifts with 3,494 updates in 3,494 active frames and zero lag NMIs.
[Matched native openings](../../build/shared-sparse-draw-native-1110/proof.json) ·
[Mini native timing](../../build/shared-sparse-draw-native-1110/mini/capture/timing.json)

The actual Downloads launch repeated Mini's timing, lift contacts and audio
order. The sole Current IPS reconstructs the tested Downloads file exactly.
[Delivery verification](../../build/shared-sparse-draw-delivery-1110/verified-delivery.json)
