# Jay McCray private movement link

The original donor input, position setup, projection, gravity, integration and
contact resolver link with the native tile adapter into **1,925 bytes** at
`$A000..<$A785`. This exact link needs two 1 KB carrier pages and leaves 123
bytes within `$A000..<$A800`.

| Source contribution | Bytes |
|---|---:|
| Frozen donor input and motion after removing original `$D002` | 1,304 |
| Direct zero-page operand growth before the probe rewrite | 222 |
| Net probe rewrite, including its original logical pointer | 25 |
| Probe metadata repack | −5 |
| Fresh input, logical mapper result and sound request | 32 |
| Native D002 adapter | 347 |
| **Total** | **1,925** |

The seven original indexed-indirect loads belong to the X=0 player resolver
at donor `$CF07`. They now index the same five two-point records in private
code. Y retains its original local byte index. The original X=0 is restored
before the sampler and on exit. The private copies of donor `$00/$01` retain
the exact original logical pointer. The original probe order, coordinate
adjustments and solid-contact paths remain in the resolver. All 150 linked
relative branches fit. The closest limits are `BEQ $A0B1` from `$A030`
(+127, original `RightInput`) and `BNE $A07A` from `$A0F1` (−121, original
`StoreHorizontalVelocity`). Inserting bytes into the former span can require
a branch rewrite.

The proposed state maps 51 fields into physical RAM2 `$C000..<$C033`. The two
coarse tile coordinates share `$C0F0/$C0F1` with the adapter. The query fields
and private record index extend through `$C0FA`. The no-B donor weapon import
exercises the original inline-dispatch pointer `$F4/$F5`. Both bytes are mapped
explicitly along with its cooldown `$52` and weapon selection `$B8`. The
logical MMC1 helper preserves donor return flags and logical state without
touching MMC5 registers. No host zero page is borrowed.

## Executed checks

The checker binds the pinned Journey to Silius cartridge and reproduces the
three prior opening hardware anchors in the donor CPU model. Each of 249
original controller updates was forked at the actual player input, position
and integration call sites. All **747 paired calls** returned the same A/X/Y/P,
live stack, donor RAM and modeled hardware state. This includes idle, walk,
reverse/release, jump tap and hold, crouch, stock fire and jump/fire. The
donor parity link runs the genuine `$81D2` on all 249 input calls and the
genuine packed `$D002` on all 839 probes. Ordered sample coordinates match.
The harness translates the logical bank byte into a donor PRG view for those
original leaves. The private link omits the donor's MMC1 serial bus writes.

The host link runs the proposed adapter against the native 1-1 buffers on
the exact `49295acff1d70349119b599882a2ec0b4e2f58d21f153c90b2228dc9aceee2a7`
parent. The earlier installed image is reconstructed in memory by reversing
the pinned SMB2 preview fix on the current `9897c2b8…` Downloads image and
reapplying the frozen source recipe byte-for-byte. Actual Jay menu confirms
and the first active native parser state match on both parents.

Four detached actor fixtures then use that real terrain for 134 total motion
updates and 466 samples. The authored row-13 floor is raw `$54` at Y208.
Current native spawn `(40,176)` uses the top anchor. The original Jay foot
probe is center+16, so the fixture initializes Jay's center at Y192. Directly
using native Y176 as the center caused the first eight idle updates to fall
through empty row 12. The surface-based initialization is part of the proposed
constructor contract.

| Input | Updates | Terminal Jay center | Apex above start |
|---|---:|---|---:|
| Idle | 8 | X40, Y192 | 0 px |
| Right | 40 | X96.25, Y192 | 0 px |
| Tap A | 36 | X40, Y192 | 19.5 px |
| Hold A for 14 updates | 50 | X40, Y192 | 52.5 px |

The two jumps land through the original contact resolver on the actual floor.
The host fixture invokes the real donor weapon input in a separate CPU bus
with B released. The result establishes the movement and terrain link. A live
Jay constructor, ordinary Main routing, camera publication, body and pose,
weapon/projectile service, scripted terrain events and native item effects
still require integration. `$B000/$B003` are explicit test import coordinates
for `$81D2/$EA06`, without executable host bindings. CHR331/332 and the
mutually exclusive A3/C2 windows remain conditional. No production loader or
shared hook was changed.

Run `python -B tools/audit/run_bounded_build_v1.py --output build/jay-silius-private-motion-1110 --max-files 1 --timeout 600 -- python -B tools/audit/check_jay_silius_private_motion_1110.py`.
The output root remained absent. No ROM, capture or Mesen execution was created.

Packet SHA-256 `c79bc2e16d67ee256fb1f44089eb429950906884b846522a40b73842d9ed31a1`.
Linker source SHA-256 `e17fe994098a54e4ca049fc8907ed510ae4a500eae48783121dcceb20670a078`.
