# Jay McCray donor movement seam

Jay's current prototype reaches the Mike Jones movement and weapons code.
On the tested `d2542ff3…` nightly, the real menu selects Jay on Mike's slot
15 after one Select press. `SelectedCharacter` is 16 and `$730B & $60` is
`$20`. Eight ordinary Main updates each reach PRG96 `$A521` → `$A2CB`
for movement and PRG96 `$A57E` → PRG98 `$A000` for weapons.

The prototype build's original source packet was limited to donor body art,
palette, and menu workers. Its retained `linked-v3.json` records the later
selector operand change from `$5FE8` to `$730B`. The current runtime trace
binds the actual selector byte and Mike calls on the nightly.

## Donor execution

`C:/NES/Journey to Silius (USA).nes` is the original mapper 1 cartridge with
128 KiB each of PRG and CHR. Its SHA-256 is
`12f5c5e413a2aa5bff75b5077e4477497d7e49aa432560c2e8c3fd3cc71910cc`.
The source CPU bus starts at the reset vector `$FFF3`, executes the original
MMC1 selection and controller reads, and delivers the original `$C151` NMI
on logical frame boundaries. The three body anchors match the earlier
controller-only hardware capture at the same frame and pose.

| Frame | Controller phase | Body OAM anchor |
| --- | --- | --- |
| 1500 | Idle | X88, Y160 |
| 1536 | Walk | X96, Y160 |
| 1550 | Jump | X96, Y124 |

The retained hardware receipt has SHA-256
`926a1f5691960335915043009e5f7a2e5c81c63fe5550ae9d2b11ae171bb3ae1`.
The current run uses a bounded logical PPU/DMA bus. The matching anchors
bind the start and sampled pose positions to the earlier hardware evidence.

| Donor coordinate | Executed responsibility |
| --- | --- |
| PRG7 `$C12D` → PRG6 `$8000` | Player update after the original bank switch |
| PRG7 `$E25D` → PRG6 `$8048` → `$8093` | Restore 16-byte actor state from `$0500` into `$10..$1F`, then run the control update |
| PRG6 `$818A` | Jump admission, held-A updates, and release |
| PRG6 `$81D2` → `$844E` | Weapon cooldown and original stock gun row |
| PRG6 `$81EA` | Camera/position setup and level scroll requests |
| PRG6 `$8055` → PRG7 `$E1A4` → `$CE4D` | Player gravity, fixed-point integration, and terrain contact |
| PRG6 `$8304` and PRG7 `$E2AE` | Select body pose and save actor state |

At `$8093`, `$0162` is the current controller sample and `$0163` is its
previous sample. `$C86E` computes the actual fresh-button bits. Actor `$14`
and `$15` hold signed velocities in sixteenths of a pixel. The original
jump uses velocity `$CC` and hold byte `$51`. The source CPU replay measures
an apex of 19.5 px for a tap and 52.5 px for a 14-update hold. Right movement
from rest reaches 26/16 px per update in the opening. The original stock
gun allocates up to three high projectile slots through `$A387`. The fresh-B
test, `$52` cooldown4, and `$8E3F` spawn write execute on the actual path.
Holding B produces one projectile. Releasing and pressing again produces
a second. Both are owner1 with initial speed 64/16 px per update in the
right-facing fixture.

## First port seam

`tools/reference/jay_silius_original_input_1110.s` reassembles all 319
original bytes of PRG6 `$8093..<$81D2`, starting at cartridge file offset
98467. Its donor slice SHA-256 is
`fcb1e99c33e0857acdf00ddc86efe57998e981986d3ca797d072888dd716d5fa`.
The test relocation to `$6093` changes only internal absolute high operands
at donor `$8095`, `$80AC`, and `$81A5`. It still executes the real donor
`$81D2` weapon dispatch and `$C86E` controller edge helper. The relocated
bytes are confined to the disposable in-memory donor CPU arena.

Eight controller sequences fork the genuine donor opening. Across 243
actual `$8048` caller frames, the original and relocated control blocks
return equal AXYP/SP, instruction cycles, live stack, RAM, and modeled PPU
and mapper state. The same runs follow the original actor through integration
and terrain on every update. The sequences cover idle, right movement,
reversal/release, tap and held jumps, crouch, repeated stock B, and jumping
with a stock shot.

The next integration step is a Jay-only branch at the proven Mike movement
ingress, gated by the existing `$730B` variant bits. It needs a private donor
actor/input state lease and the original order from `$8093` through `$81EA`
and `$E1A4`. The terrain/camera bridge must translate the native host probes
at `$CE4D` and the scroll requests from `$81EA` while preserving the donor's
position fractions, per-frame gravity, hold state, and move/contact order.
Weapon admission has a separate actual donor call, `$81D2`, whose stock slot
ownership and firing edge are now pinned. The current milestone is the
relocated control slice and exact donor trace. Host movement, terrain,
projectile, audio, and full-stage integration are subsequent milestones.

The bounded stdout run used `tools/audit/trace_jay_silius_donor_1110.py` with
`--prototype-rom` pointing to the pinned `d2542ff3…` nightly. Both bounded
output roots stayed absent. The source and checker hashes are
`1c338759bf4f215dca200514d540a1c761bc09bfb2e352836e79bd790852c5e7` and
`20d070792e60aa6fb564adcef2525da705ad2a9f58506067615cbcefd66d3ede`, respectively.
