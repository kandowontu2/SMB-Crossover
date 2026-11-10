# Jay McCray isolated cold and Main integration

The test uses the exact installed `9897c2b85489024be25b4b296d0ea57975a579ba1e3ff37a71f7ac3e0b195b97`.
The original 1,925-byte movement link stays byte-exact. The model installs it
from physical CHR331/332 through the current common scene and compact worker,
authenticates it on the ordinary Main callback, and uses the actual native
1-1 tile buffers. Source proof runs in the bounded CPU model.

## Scene and cold copy

The real native entry sequence distinguishes three lifetimes. Mike-family
reset PRG96 `$A6EF` runs at logical update 0 and still sees title coordinates
X120/Y160. PRG65 `$AC2C` runs at logical update 1 with rendering blank,
`FamilyMainCommit=1`, and `NmiDisable=$FF`. The native spawn is still unset
at that point. Ordinary movement first sees X40/Y176 at active update 167.
The isolated proposal uses the scene hook to copy only, then constructs the
donor actor on the first authenticated active movement update. Its center is
Y192, sixteen pixels below the native top anchor Y176.

| Physical PRG and site | Existing bytes | Isolated call |
|---|---|---|
| 65 `$AC2C` | `20 26 B0` | Jay-only cold or the original retirement call, preserving `$AC2F` continuation |
| 65 `$AF00` | `AD 02 60` | Exact raw16 plus `$730B & $60 == $20` descriptor and cookie, otherwise original `$AF03` |
| 65 `$AE85` | `20 72 AB` | Jay-only direct compact worker call, otherwise original typed copy/bootstrap |
| 96 `$A53D` | `4C CB A2` | Jay-only hot gate, with original Mike fallback |

The common raw37–43 table remains bounded exactly as before. The Jay branch
uses the existing `$AE00` caller for forced-blank guard, prior-owner retirement,
dual-header invalidation, copy result, final commit and mapper/PPU restoration.
The existing PRG91 typed bootstrap would try `$D25E` for raw16, so only Jay
calls the unchanged PRG123 `$AF40` compact worker directly. The descriptor is
`02 02 01 4B 01 4C 01`. It copies and independently verifies two 1 KB code
rows into physical RAM3, and zeroes one state page in physical RAM2. Cookie
`A71020012173402E9563319FF8163990` binds Jay's raw/alternate, revision, padded
packet and descriptor. It commits through the existing full `$BFE0/$DFE0`
header protocol. The shared mailbox remains untouched.

The cold test observes 4,100 actual PPUDATA reads for the two copied and
verified pages. An authenticated warm call reads no CHR. The warm scene
wrapper clears Jay's `Ready` after authentication, so a new scene constructs
fresh position rather than reusing the previous actor. Every single-byte
fault in either header reloads on a legal blank scene. Three readback fault
locations leave both headers invalid. The cold path passes 426 genuine
forced-blank NMI cuts and 134 IRQ cuts.

The current seven raw37–43 owners run paired cold transactions with identical
state and physical PPU reads before and after replacing pages 331/332 in the
fixture. None reads either page. Real bidirectional cold transitions pass
between Jay and each of raw37, raw39 and raw43. The current Zelda II alias
also passes 512 paired actual pose/setter and regular NMI tests, all 256
indices and both facings. Neither page is published. Restoring the old alias
for index 23 publishes page 331 and triggers the negative control. Together
with the finite current publication bindings in `jay-silius-host-tile-1110.md`,
this supports a conditional 331/332 carrier reservation for review.

## Gameplay boundary

The hot callback checks both full headers before mapping the code. Native
frame epoch prevents a second update on duplicate entry. It publishes native
position, horizontal delta and vertical status, then restores both PRG maps
and the callback register frame. The isolated fixture accepts the actual
fixed-camera 1-1 opening with B released. It invokes the genuine donor `$81D2`
in a separate donor CPU bus for each weapon input call. The packet has no
host projectile or scripted-terrain binding. Outside the qualified scope or
after failed authentication, the gate takes the unchanged Mike prototype path.

Eighty-six controller-driven Main updates execute original movement on the
native parsed terrain after the real menu/scene transition. Jay walks to
X78.25, holds A for fourteen updates, rises the original 52.5 px and lands at
center Y192. The host ends at X78/Y176 with two lives. Mike and Steve each
execute the same 60-update controller sequence on base and proposal, with
equal native state, private RAM, VRAM, CHR and mapper state.

The hot path passes 704 actual lag NMIs and 704 hardware IRQs at reached
resident and private instructions. Five cuts fall between mapper shadow and
physical writes. Actual returns preserve the live register/stack frame,
private RAM and SMC, and a split may restore the new shadow one instruction
early. Thirty-two separate header-byte faults at the hot entry reach the
original fallback without executing or changing the private packet. Five
context rejections behave the same. A same-epoch repeat from the reached
Main context leaves the actor unchanged. A post-Main direct call was
discarded for that test because `FamilyMainCommit` has already cleared there.

## Residency and scope

The assembled resident fixture uses 136 bytes for cold including its cookie,
434 bytes for hot including its 51-byte actor template and second cookie, and
seven descriptor bytes. Four existing 3-byte sites redirect to the fixture.
The checker supplies resident code and descriptor in synthetic test memory
at `$4800`, `$4A00` and `$4D00`. Those addresses have no executable cartridge
allocation. The exact in-memory derivative therefore cannot run as a native
ROM. The private movement packet still leaves 123 bytes in two pages. The
434-byte resident bridge does not fit that tail, and actual fixed-bank space
or a separately funded and linked bridge remains required.

Jay still needs camera/scene progression, native enemy and body/collision
effects, authored pose and weapon/projectile publication, and end-to-end 1-1
and item testing. The current packet uses a bounded no-B external fixture and
preserves the old Mike fallback for unsupported scenes. No production PRG,
RAM or CHR grant follows from these tests. No Mesen run, ROM file or build
output was created.

The zero-output command is `python -B tools/audit/run_bounded_build_v1.py --output build/jay-silius-scene-lifecycle-1110 --max-files 1 --timeout 600 -- python -B tools/audit/check_jay_silius_scene_lifecycle_1110.py`.

- Resident source SHA-256 `e8ce4d4df3f8c3254bf91bd00780d64720687f7f5a4b19f8309add7e0713ad85`.
- Checker SHA-256 `6ddad4674cc9fbb967e3f970f6dc8c011b252151710fda3397b9a7acd01121eb`.
- In-memory cartridge view SHA-256 `de486fef2afb59b8d47619fd4c9d473c484b8aaf7b4e756d9b5e76246be56062`.
