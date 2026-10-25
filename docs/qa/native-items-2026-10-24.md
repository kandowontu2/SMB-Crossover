# Native item progression and CV3 ceiling separation

This audit continues the unfinished 37-identity, every-powerup and route goal.
Its evidence directory is
`C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-items-px`.
Public ROMs and the player guide have not been replaced.

## Reproduced defect and candidate

Alucard's first actual head bump into a question block moved his world X from
112 to127. The native block response stopped his upward speed but left Y166
inside the block. The subsequent side query interpreted its underside as a
left wall. The first wrong X write was the native bank10 wall clamp; this was
not corrected by weakening the movement bounds or shifting the test arena.

The candidate separates a genuinely crossed CV3 ceiling before the side
queries. It uses the already published fractional velocity and actual sampled
row/head adder, preserves the raw query result, and leaves coins and climbable
tiles alone. Standing, compact and crouched profiles and both buffer parities
are checked. No graphics, level, jump table, inventory or RAM layout changes.

Adopted checkpoint: `build/checkpoints/native-items-px/candidate.nes`, SHA256
`18a05934bc95410bf058d239cc67e6c97851dfb575a144194ebf4643dc2a3438`.
Parent PW SHA256
`310716353e9068a1f57b01dad4ca44d6c22e96d5de2fcd410607547244f28a54`.
Root adoption is established by `build/verification/native-items-px/proof.json`.
`finalize_px_once.py` succeeded and must never be rerun.

The source change is two existing files and one added ceiling helper. All
54,001 previous qualified symbols retain their addresses. The expanded ROM
changes 162 bytes in bank 89 only. All CHR bytes are identical. 5,832 other-identity
entry states preserve the exact old dispatcher A/X/Y/live-flags/SP/RAM/bank
state. The full edge test covers 55,296 tile/profile/page/direction/engine cases,
including 8,964 admitted ceilings and 46,332 excluded cases. Turtle and Mac gate
entries preserve their exact cycle costs; the other legacy leaves add 9 cycles
(15 for ordinary Simon). This is not a universal performance improvement.

Candidate v2 fixed the collision but its unconditional selector added one missed
frame in each of two heavy turtle attack components. It was rejected. Candidate
v3 reuses the existing head router's saved A/P and keeps turtles on their original
branch. All eight 600-update turtle components now have byte-exact gameplay,
call/cycle and missed-frame traces against PW, including the overloaded secondary
phase. That phase still has 21–25 missed frames per 120 updates; constant 60 Hz
is not claimed. The failed v2 measurement and stopped diagnostic process trees
are recorded. All raw prefixes and completed captures were retained.

The complete1,217-file source ZIP independently rebuilds this candidate.
Ordinary flag-off builds remain byte-identical to PW: MMC3
`d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb`;
MMC5`f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833`.

## Native item tests

Every fixture uses actual cold menus, real head bumps or kills, native actors,
full emergence and physical collection. The visible and logical test arenas,
initial injured state and any pinned source RNG/drop counter are declared.
Mature item actors are brought to the player only after110ticks; inventories
are not granted between stages. These are component tests, not natural campaign
drop-frequency or every-item route proofs.

On the candidate,14mode/identity cases complete106separate native block
rewards with strict player-X and block-X bounds, including collection and the
declared active ability/ammunition outcomes:

| Identity | Rewards per mode | Observed outcomes |
|---|---:|---|
| Grant | 4 | Mushroom healing, dagger, axe, stopwatch and heart costs |
| Sypha | 4 | Mushroom healing, flame, ice, lightning and heart costs |
| Alucard | 4 | Healing, both fireball upgrades, capped-upgrade healing |
| Mike Jones | 24 | Heart growth, both primary upgrades, all10specials and individual ammunition costs |
| Darkwing | 5 | Healing, Arrow/Heavy/Thunder adaptors, repeated adaptor refill and gas costs |
| SMB3 Mario | 6 | Mushroom, Fire, Raccoon, Frog, Tanooki, Hammer; native suit attacks |
| SMB3 Luigi | 6 | Same actual suit progression and controller abilities |

On PW, additional native suites pass for all four turtles' equipment in both
modes, Roll's block/drop/charge/brick behavior in both modes, and Little Mac's
healing/star cap/super punch in both modes. Those remain PW evidence rather than
fresh candidate coverage. TMNT's equipment pixels and actual DMA admission
also match the authenticated original source descriptors. Overload flicker is
measured, not represented as full-time sprite visibility.

After adoption, Zelda II Link also passes 19 real block rewards in each mode:
all eight spells, three techniques, four additional heart containers and four
additional magic containers, plus the first mushroom's independent healing.
He starts with four containers of each kind, so four more reach the original
eight-container caps. This brings current-checkpoint acquisition requirements
to 144 across 16 mode/identity cases. It proves receipt, not every spell's use,
EXP leveling, drop restoration or the capped fallback reward.

Tanooki initially failed because the fixture released Down while the original
smoke animation was still running. A read-only trace showed the native suit
queue and immediate source-correct release on the next movement update. Holding
Down through the smoke, then releasing it, passes all four SMB3 mode/variant
cases. No Tanooki game fix was invented for that test error. Missing unexported
debugger aliases caused two earlier fixture failures and are also retained.

The first ceiling candidate failed because its test for unsigned subtraction
borrow treated an ordinary negative velocity as a previous-position wrap.
The accepted candidate checks the reconstructed byte ordering instead. All
negative scripts/logs and the original strict movement assertion remain.

## Physical frames, routes and remaining gates

Four PW Mike/Darkwing streams retain 14,587 actual PPU frames; ten v2 and ten
adopted v3 CV3/SMB3 streams each retain 13,611. Every PNG is RGB-verified and every raw stream is
retained in an independently round-tripped lossless archive. Recursive frozen
Lua dependencies are separately hash-bound in `native-capture-bindings-v2.json`.
Every adopted v3 component PPU pixel, native state field, input and ordered
hardware audio write matches the collision-fixed v2 recording. Only the CPU
instruction boundary at physical endFrame is excluded from that state comparison
because the router's instruction timing intentionally changes. The separate
turtle benchmark above has no such timing exclusion.
Sampled visual sheets and the complete 16-frame Alucard head-hit window are
retained; whole-stream human frame-by-frame inspection is not claimed.

All 37 cold character selections pass on the adopted checkpoint. Fresh 1-1 discoveries for
Grant, Alucard and Sypha clear in both modes without deaths. The older generic
controller's deaths/stalls are retained. Previously verified source-specific
controllers produce the successful runs. These six fresh v3 discoveries are not
yet six independently qualified full routes. One v2 Grant route has a strict
guarded direct replay; it remains older-candidate evidence. Independent current
full-route replay and strict scrolling/movement/CHR review remain open. The
current native item, cold entry, comparative performance and binary/source gates
are recorded in the adoption receipt.

The interval12-only guard initially failed to create a decoder screenshot
directory when replaying an interval24discovery. The bound interval24guard
disables that unused screenshot path while retaining every original replay,
code/SMC, stack, NMI/IRQ and movement assertion. The failed observer is retained.

Every remaining item, passive/expiry/depletion/refill behavior, source graphics
and SFX, all37current-hash routes and shortcut routes, music/performance, final
MMC5/oversizedMMC3release and the guide remain unfinished. This audit is not a
completion or release declaration.
