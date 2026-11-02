# Bub / Bob original-source readiness — 2026-11-01

Status: original normal-play source recovered and CPU-checked. **No host bytes,
raw character ID, menu entry, cache page, CHR page or resident span allocated.**
No Mesen run, candidate ROM, installation or commit was performed by this work.
Shinobi v29/v30 inputs were left intact.

## Donor and credits

- Original local donor: `C:/NES/Bubble Bobble (USA).nes`, 163,856 bytes.
- SHA256: `e34901acf6917495890ef79ddb33e4641ea309a803d777a27a198e8802c9b4a0`.
- Original PRG: 131,072 bytes, CRC32 `b1378c99`; CHR: 32,768 bytes,
  CRC32 `a6aa53ac`; MMC1, eight 16KB PRG banks, eight 4KB CHR banks.
- Original fixed-bank vectors: NMI `$CE07`, reset `$E882`, IRQ `$CE61`.
- No Bubble Bobble source component was found in current tools/source/reference
  material; the compacted-source index returned zero `bobble` matches.
- Original game attribution: **Taito**. The USA original manual identifies
  Taito Software Inc. and credits Taito America, Inc., copyright 1988. Specific
  NES staff names have not been authenticated from this donor; do not substitute
  arcade/C64/other-platform staff lists.
- The [original Taito manual](https://www.nesfiles.com/NES/Bubble_Bobble/Bubble_Bobble.pdf)
  identifies controller 1 as Bub and controller 2 as Bob, A as jump and B as
  bubbles, and describes enemy capture, popping groups and held-A bubble riding.

Instruction boundaries were discovered using Junior-Jones's
[Bubble Bobble NES static recompilation](https://github.com/Junior-Jones/Bubble-Bobble-NES-Static-Recomp)
at commit `5980e1a5f1731181ced5d195d85f9551d5ac7f28` (generated banks 4..7).
Every recovered opcode **and operand** comes from the pinned local original ROM.
No generated C engine was adopted. This is annotated ROM recovery, not an
assertion that an original developer source tree or a complete semantic
disassembly was found. The upstream third-party notice is retained; it is not a
license statement about Taito's game. The often-cited NES-Games-Disassembly
repository lists this game as planned and does not provide its source.

## Recovered code and actual mechanics

All addresses below are original donor addresses. Names are recovery annotations.

| Physical PRG16K bank | Range (inclusive) | Bytes | Purpose |
| --- | --- | ---: | --- |
| 7 | `$C38F..C3A7` | 25 | Paired sprite swap / actor iteration |
| 7 | `$C43E..C46F` | 50 | Original axis-distance contact test |
| 7 | `$CE30..CE4C` | 29 | Original post-update frame/timer clock, isolated from PPU/controller/audio NMI work |
| 7 | `$D0BE..D161` | 164 | Tile lookup and adjacent-tile cursors |
| 7 | `$D18A..D770` | 1,511 | Player initialization, input normalization, update, motion, bubble request, injury, animation and pose data |
| 7 | `$D882..E008` | 1,927 | Bubble pool, launch, growth, drift, warning, contact, trap, pop and chain mechanics |
| 6 | `$9528..9602` | 219 | Trapped-enemy update, expiry/release and original pop/death event |
| 7 | `$EFD9..F01D` | 69 | Special-bubble pop bookkeeping; normal positive-state bubbles return without those effects |
| | **Total** | **3,994** | **1,824 recognized instructions**, remaining bytes retain original tables/unclassified data |

The exact reassembly digest is recorded in `source-closure.json`. The initial
3,965-byte closure was extended by the genuine 29-byte source clock tail;
the original player/bubble bytes were not replaced.

- `$D1A0` combines fresh input and held input. Normalized bits `$20/$10` are
  fresh A/B; `$80/$40` are held A/B; low bits retain held directions and fresh
  direction bits are shifted into bits 2..3. `$D1E7` chooses controller by its
  original OAM index 0 or 8 (`TYA` precedes the comparison).
- `$D457` moves one pixel per normal grounded update. The source speed flags
  `$81` add an extra step and even-coordinate snapping. Air input is gated by
  the original 3-update phase at `$28`; `$D518` adds saved-direction movement on
  the original frame phases. The source's initial fast-right alignment produces
  59 pixels in the checked 30-update fixture, versus 60 for fast-left.
- `$D365/$D386/$D2F3`: normal jump has **28 ascent updates and 43 pixels of
  rise**, from the exact 28-entry table at `$D2D7..D2F2`. Falling uses that
  table in reverse order and checks support in one-pixel steps. Speed flags can
  run the vertical update twice per player update; no jump height was invented.
- `$D530`: fresh B sets a 25-update cooldown, or 12 with source flag `$04`,
  and requests Bub (`$80`) or Bob (`$40`) in `$0464`.
- `$D887` iterates **15 four-byte logical bubble slots**, `$88..C3`. Launch
  starts at the real player sprite origin and facing. Three 8-update phases
  grow the normal bubble; `$DFDF` uses original source speed 3 or 5. Original
  terrain/wind and stage timing control drift. Normal/warning states use their
  original timers, then `$DA81` plays the three-step burst and frees the slot.
- Pool saturation uses `$DD24`: an eligible old bubble is retired, the pending
  request survives that early return, and spawning resumes on the next update.
  The checked simultaneous Bub/Bob request sequence is 14/14/15 active slots
  with pending flags `$C0/$40/$00`. It never grows beyond 15.
- `$DE99` tests enemy proxies with original distance threshold **12**; normal
  hit sets enemy flag `$10`, copies the bubble location to the trapped enemy,
  captures its owner and timer, and consumes the projectile. Immunity flags
  `$08/$10` and the original excluded state are retained. Capture is a state
  transition, not ordinary immediate damage.
- `$DC55/$DD6D` preserve player contact pop, bubble pushing and **15-pixel
  chain distance**. The original processes one pending chain actor per update;
  nearby bubbles/enemies become pending before later calls finish the chain.
- `$9528` decrements the trapped-enemy deadline, clears trapping and enters
  escape when it expires. Pop state 5 calls `$95D0`, producing source death
  flags `$18`; a host adapter must turn that event into native enemy defeat and
  credit the correct player once.
- `$DC55` sets player bubble support; `$D331` uses held A during descent to
  restart the **same** source jump. This must remain available for traversal.
- `$D580..D740` select and render the 23 source poses with the original paired
  8×16 tiles, facing swaps, injury and blink behavior. Bub and Bob share art;
  source attributes/palettes identify them.

Source input, tile semantics and boundaries are not the SMB ABI. Original tile
lookup returns **zero for solid** and nonzero for air/wind; it uses 8×8 cells.
Original stages have one-way platforms, fixed horizontal limits and vertical
wrapping; ascent does not check a solid ceiling. These need explicit, tested
native terrain/world/ceiling/pit/camera adapters. Passing the existing native
small-body collision policy to this character would not establish source
accuracy. Original hurt distance is 9; bubble interaction has separate 16/10
tests; trap and chain thresholds are different again.

## Exact state/art needs and proposed envelope

The donor retains player state at `$2E..41` and `$42..55` (20 bytes each),
15 bubble records at `$88..C3` (60 bytes), seven original enemy records at
`$68..83` (28 bytes), plus one trap deadline per enemy and query/frame scratch.
Player state offsets 0..9 are active/lives, normalized input, source flags,
vertical state, jump index, carried direction, pose, animation phase, shot
cooldown and bubble interaction. Offsets `$10..13` hold special-pop progress,
injury/blink timer, pending pop credit and forced-pose timer. Unused/score bytes
must remain private until their native adapters are defined.

Original OAM is also simulation state: players use `$0200..020F`, enemies use
`$0210..0247`, and bubbles use `$0288..02FF`. Source global fields include
`$040A` trap duration, `$0444/$045D` drift phase/configuration, `$0463` bubble
separation timer, `$0464` shot requests and `$0476` death-direction phase.
The compact proof fixture uses three private 256-byte slabs corresponding to
original zero page, OAM and `$0400..04FF`: **768 bytes**, not host zero page or
host live OAM. Native actor associations, 16-bit world/camera coordinates,
owner lifetime and publication scratch fit within a proposed additional
256-byte allowance. The 768-byte original stage tile map is **not** proposed;
native tile-query callbacks replace it.

Normal sprite CHR0 bank 1 supplies tile pairs `$00..2E`. Blink tile `$27`
comes from CHR1 and was checked byte-identical/empty in all normal stage banks
2..5. The extracted normal body/bubble closure is **800 bytes / 25 native 8×16
pairs** (50 bitplane 8×8 tiles). It fits one 1KB CHR page shared by both identities. Original sprite
palette data at `$C556..C565` is retained: Bub's opaque colors are
`$2A/$26/$30`, Bob's `$2C/$23/$30`. No invented sprite art is needed.

The present closure excludes source powerup fire/thunder/water behavior,
item/reward art and original enemies; boss mode changes CHR0 to bank 6.
Ordinary trapped native enemies can retain native art inside source bubbles
through a declared adapter. Those exclusions must remain visible in any first
admission claim; this is the base player/bubble integration, not the entire
Bubble Bobble game or every original powerup.

**Proposal for root review, not an allocation:**

| Resource | Proposed reservation | Measured basis / remaining work |
| --- | ---: | --- |
| Component PRG | one 8KB conditional image | Concrete linked image and carrier proposal below. No whole physical PRG bank is verified free in v30. Native transport, terrain/contact, world/camera, scene/death and OAM adapters still require assembly and foreign-owner proof. |
| Private state | one 1KB page | 768-byte source-state slabs plus 256-byte adapter allowance. Exact linked offsets and page ownership require host review. |
| CHR | one 1KB page | Exact normal closure 800 bytes, shared by Bub and Bob. |
| Resident/shared ingress | **0 allocated** | Determine the existing roster/public-service entry path and assemble exact byte funding before any grant. No Shinobi/Excitebike resident span is assumed available. |
| Menu identities | Bub and Bob absent | Source supports two identities. Root must choose admission/raw-ID policy; no entry or unlock was written. |

Both source and actual native gameplay use 8×16 sprites. Each 16×16 body or
bubble retains **two** sprites, so fifteen bubbles plus the player consume
32 OAM entries. This corrects the initial assumption of an 8×8 native path.
Keep all 15 logical states with bounded viewport/draw admission and stable OAM
clipping; scanline capacity still needs native verification. Exact source tick
cost in the saturated fixture is **9,076..12,098 CPU cycles**, excluding host
transport/drawing. Idle/walk and crowded native profiles remain acceptance work.

No helper platforms have been added. A 43-pixel base jump does not by itself
prove clearance of every native pipe; source bubble riding must be tested before
deciding whether assistance is necessary. A full cold 1-1 replay and helper
inventory update, if any, belong to later root-owned native testing.

## Proof, bounded outputs and reproduction

One active output: `build/bubble-bobble-source-1101-v1`; the continued component
work remains below 2MB and 25 files. The original ROM and full upstream source
tree were not copied.
Fixtures stay in memory and results aggregate into one CPU receipt.

- `instruction-index.json`: pinned boundary provenance and locally recovered
  instruction bytes; `discovery.json`: donor identity and discovery scope.
- `donor-source.s/.cfg/.o/.bin`: exact original-address reassembly;
  `source-closure.json`: byte ranges, SHA and explicit unresolved direct imports.
- `donor-chr-closure.bin`, `chr-closure.json`: exact source graphics and palettes.
- `CPU-closure.json`: **1,930** calls in instruction lockstep against original
  ROM, **1,136 unique source PCs**, all resulting RAM/register/cycle comparisons
  equal. Covers controller normalization, real complete flat-player update,
  jump, cooldown, actual pool scheduler/capacity, 84 trap-contact cases, contact
  pop/chain, trap timeout, empty-bubble age/burst, riding and all 92 identity /
  pose / facing combinations.

Sound, score/UI, special-mode callbacks, original stage bubble spawn and enemy
renderer are explicit RTS imports in the fixture. The default bubble mechanics
execute original instructions. This is not a native host, relocated code,
banked transport, IRQ/NMI, original main-loop or emulator proof. Saturated pool
cycles are actual source fixture costs; not a host lag claim.

Run each producer through the shared bounded wrapper (same output with
`--resume` after discovery):

```text
python tools/audit/run_bounded_build_v1.py --output build/bubble-bobble-source-1101-v1 -- python tools/audit/recover_bubble_bobble_source_1101_v1.py --fetch
python tools/audit/run_bounded_build_v1.py --output build/bubble-bobble-source-1101-v1 --resume -- python tools/audit/prepare_bubble_bobble_closure_1101_v1.py
python tools/audit/run_bounded_build_v1.py --output build/bubble-bobble-source-1101-v1 --resume -- python tools/audit/check_bubble_bobble_closure_1101_v1.py
```

## Concrete independent component v2

`prepare_bubble_bobble_component_1101_v2.py` now assembles `component.bin`, a
  complete **8,192-byte** image for `$A000..BFFF`, SHA256
`28d4099372196cafdcf2df4461128750da49b6814bd4a26077dca9ca60bc6598`.
It uses **5,434 bytes** through `$B539`, leaving 2,726 bytes before the reserved
header at `$BFE0`. The source code/data part is 5,178 bytes after private
operand promotion, branch relaxation and explicit seams. All 418 direct
zero-page operations address private RAM. No instruction borrows host zero page.

The 37 native service rows at `$A000..A06E` all point to `$A06F` (`CLC/RTS`).
This component cannot be menu-admitted by merely binding a new raw ID: native
movement, draw, lifecycle and collision wrappers remain to be written and
qualified. The loader must bind and verify the import vectors before committing
an owner cookie; default imports reject. There is no shared loader implementation
or assumed free resident span in this packet.

Source exports use the original source ABI: X is `$2E` for Bub or `$42` for
Bob, Y is private OAM offset 0 or 8. The bubble/enemy routines use original
four-byte actor indices and paired-sprite OAM offsets. These are **not** native
SMB callback arguments.

| Export | Linked entry | Contract |
| --- | --- | --- |
| `BbSourceClock` | `$A15B` | Original `$CE30..CE4C`, one post-update clock; returns before original audio |
| `BbSourceInit` | `$A25D` | Original initialization for both player records |
| `BbSourceSprites` | `$A3AE` | Original initial sprite pairs for active source identities |
| `BbInput` | `$A278` | X actor, Y private fresh-controller offset `$F5/$F6` |
| `BbPlayerStep` | `$A2C9` | One genuine player update, X/Y actor ABI |
| `BbBubbleStep` | `$A9F8` | One complete pool update, then bounded return |
| `BbTrappedEnemyStep` | `$B3C0` | X enemy proxy `$68..80`, Y OAM `$10..40`, private `$26=X` |
| `BbPoseStep` | `$A79B` | Genuine animation/facing/blink step |
| `BbHurtBub` / `BbHurtBob` | `$A761` / `$A793` | Original injury starts |
| `BbJumpStart` / `BbJumpAscent` | `$A4C2` / `$A4EB` | Source jump request / ascent helper |
| `BbShotRequest` | `$A736` | Source cooldown and identity request |
| `BbBubbleContact` | `$AEC9` | Source pop, push and ride-support contact |
| `BbPopChain` | `$B04D` | One original pending pop-chain actor per update |
| `BbBubbleSupport` | `$A479` | Source held-A / vertical-state eligibility |

All imports are three-byte JMP vectors. They are unresolved host seams, not
implemented native adapters:

| Vector | Name | Required adapter behavior |
| --- | --- | --- |
| `$A080` | Score | Credit original pending score events once, correct owner |
| `$A083` | LivesUI | Reconcile original source life/death output with native lifecycle |
| `$A086` | Yield | Original coroutine entry is outside the admitted bounded API; reject |
| `$A089` | StageEffects | Source special-stage callback; reject until explicitly supported |
| `$A08C` | SpecialAbility | Source optional ability callback; reject until supported |
| `$A08F` | StageBubbles | Original stage bubble spawning policy; explicit native-stage policy needed |
| `$A092` | SpecialPop | Original special-bubble progress/reward effect; currently outside base admission |
| `$A095` | Sound | Original A sound event, publish through host audio ownership |
| `$A098/$A09B` | BossPlayer / BossDeath | Original boss mode is outside this base component; reject |
| `$A09E` | EnemyDraw | Publish native enemy/trapped-overlay state without changing source motion |
| `$A0A1` | EnemyRelease | Restore native enemy AI/contact on source timeout; no defeat credit |
| `$A0A4/$A0A7` | FoodUpdate / ElementalUpdate | Original item/elemental slots; reject until supported |
| `$A0AA/$A0AD` | Tile23 / Tile84 | Read source-format tile cursor at private offsets `$23/$84`; A=value, XY preserved, C/V/D/I preserved, N/Z from value |

Additional native wrappers must import/export 16-bit world coordinates and
camera position, choose exact source update ordering, map eligible native
enemies into seven source proxies, publish trap/pop/release events once, adapt
solid ceilings/pits/scripted travel, derive source-aware body/contact policy,
remap source 8×16 paired tiles into clipped native 8×16 cells, and synchronize
scene/death/pause/owner retirement. No arbitrary PlayerSize toggle is proposed.

Private state is exactly `$C000..C3FF`:

| Private range | Contents |
| --- | --- |
| `$C000..C0FF` | Original zero-page data, actors, input, frame/timer scratch |
| `$C100..C1FF` | Original OAM simulation state; never aliases live native OAM |
| `$C200..C2FF` | Original `$0400..04FF` globals and per-enemy deadlines |
| `$C300..C3FF` | Reserved native adapter context/actor associations/publication scratch |

Indexed original `$03AB..03AD,X` is rebased to `$C1AB..C1AD,X`, reaching the
same private globals for legal enemy indices. There is no private stage tile
map; both indirect source queries are typed imports. `$BFE0..BFEF` code and
`$DFE0..DFEF` state owner headers are separate conditional overlay requirements;
the latter is **16 additional header bytes outside the 1KB body state**. They
must be invalidated/retired and fully authenticated before transport. No header
was committed by this producer.

The relocating proof found and preserved a real code/data overlap: bubble phase
6 reads two bytes beyond the nominal six-pair table at `$DF81`, into the next
JSR's original opcode/operand. A 14-byte private copy retains those bytes,
including the hidden final burst OAM state; it does not read relocated opcodes
as art.

`check_bubble_bobble_component_1101_v2.py` passes **2,297** original-vs-relocated
comparisons and **74** fail-closed native-service cases. Every 768-byte source
state slab, XY/P/SP and host zero-page/nonstack RAM guard matches. A matches
except 24 direct tests of the private `$DA00` helper: its original `PLA/PLA`
discards the caller return address into A. Those cases verify exact relocation
of the discarded JSR return token; the public player/bubble paths overwrite the
dead value. This disclosed normalization is not an arbitrary register mismatch.

Sequential comparisons include the actual source post-update clock, growth at
updates 8/16/24, a fixture deadline remaining trapped through update 119 and
releasing on update 120, both identities' held-A eligibility across grounded /
ascending / falling / injured states, and a complete ridden jump reaching the
same 43-pixel apex after 28 updates. The 120 deadline is a fixture value; original
stage/rank chooses the actual initial deadline. Original full NMI scheduling,
native loader/transport/IRQ and host terrain remain untested.

## Exact v30 resource proposal, not a grant

`audit_bubble_bobble_resources_1101_v2.py` binds to installed v30
`6f319d2039f920bc85e4a6bfe6ee3327996b42020e03c09e671142eada2a6428`:

- No complete blank 8KB physical PRG bank exists. Fixed/DMC mirrors are not
  available PRG funding. No unconditional 1KB global RAM region is available;
  linked SRAM occupies `$6000..7FFF` and BSS reaches `$07EA`.
- Propose **conditional RAM3 `$A000..BFFF` code**, and **conditional RAM2
  `$C000..C3FF` state**, exclusively under a new authenticated owner after all
  previous RAM2/3 owners retire. This shares capacity, not simultaneous ownership.
- For the current 5,434-byte payload, propose physical **CHR pages
  301,305,337,362,363,440** as six noncontiguous carriers loaded to
  `$A000..B7FF`, and **441** for the 800-byte normal art closure. Every proposed
  physical byte is zero in exact v30. The current image never accesses
  `$B800..BFDF`; headers are separate. Native adapters have only **710 bytes**
  before a seventh carrier becomes necessary, even though the virtual 8KB
  layout has 2,726 bytes available. Any extra carrier requires a new exact grant.
- All **44 inherited finite table bindings** still match v30, and all **92
  actual menu states** followed by `X5PublishChr` avoid these seven pages.
  The proposed pages intersect none of the inherited finite reader sets. This
  is **not complete current gameplay/IRQ/new-loader reader/writer closure** and
  therefore does not establish permission to overwrite them.
- Blank pages 511/512/514 are occupied by Thomas/IRQ/SMB3 behavior;
  Excitebike's root-approved 728..739 grant is preserved. Candidate page795 is
  excluded because the actual SMB3 forms use it. Page fill alone is not freedom.
- Excitebike's owner-specific loader is 609 bytes and its resident spans have
  only 3 spare bytes. Its author confirms a descriptor-driven shared loader is
  a possible later design, **not an existing funded capability**. Arbitrary
  carrier lists, new cookie/header rules and the 1KB state size require new
  exact loader proof/funding. No Bub/Bob resident bytes are allocated.
- Raw IDs/menu policy remain unassigned; 37 and 38 are reserved for Excitebike
  and Prince. Bub/Bob admission remains blocked until host ownership, adapters,
  source contacts/abilities, native performance and full 1-1 are proved.

New recipes, all using the same bounded output with `--resume`:

```text
python tools/audit/run_bounded_build_v1.py --output build/bubble-bobble-source-1101-v1 --resume -- python tools/audit/prepare_bubble_bobble_component_1101_v2.py
python tools/audit/run_bounded_build_v1.py --output build/bubble-bobble-source-1101-v1 --resume -- python tools/audit/check_bubble_bobble_component_1101_v2.py
python tools/audit/run_bounded_build_v1.py --output build/bubble-bobble-source-1101-v1 --resume -- python tools/audit/audit_bubble_bobble_resources_1101_v2.py
python tools/audit/run_bounded_build_v1.py --output build/bubble-bobble-source-1101-v1 --resume -- python tools/audit/prepare_bubble_bobble_native_art_1101_v2.py
```

`native-art.json` additionally compares all **92 body** and **48 bubble** source
packets against the actual native paired-tile mapping. Every opaque pixel,
palette index, priority and flip matches. `component-native.chr` is the padded
1KB image: 25 pairs / 800 source bytes plus 224 zero bytes. Native descriptors
need eight record bytes for a two-sprite body or bubble, with source order
reversed for the descending native emitter. No PNG or native draw was produced.

## November 2: current physical resource closure and conditional grant

The earlier six/seven-carrier proposal above is historical. The current exact
request uses **eight code carriers in this order: 301,305,337,362,363,440,819,666**,
plus **441** for the 800-byte art closure padded to 1KB. Root recorded the
conditional grant in `docs/qa/allocations/bubble-bobble-1102-v1.json`. This grants
exclusive RAM3 code `$A000..BFDF`, RAM2 state `$C000..C3FF`, and the separate
`$BFE0/$DFE0` owner headers after authentication/foreign-owner retirement. It
does not grant resident loader/router bytes, a raw identity, or menu admission.
The shared `$DFD0..DFD2` clock lease remains owned by the existing host.

The affirmative evidence is frozen in
`build/bubble-bobble-source-1101-v1/current3-closure-supplement.json`, SHA-256
`858ccee4febd10a651fbb58b96f9f77bf29eb7cb1695f1a11fcd4ece23faaadc`.
Root retained it and its two inputs in
`docs/qa/checkpoints/2026-11-02/bubble-bobble-resources-v1/`.
Its existing finite publisher count is **zero** on exact current3
`37959000690d3f9fe596823fc0910e86b9fc977448779360d523751764248b0c`:

- 44 current table bindings, 816 unchanged native graphics-write instructions,
  15 current private-image writer bindings, 30 actual Tank/Metal/Shinobi/
  Excitebike cold-map rows, and 92 actual menu publications exclude the set.
- WWF's actual 24-row source table reads 637..657 and shared zero carrier 667.
  Its six exact 1,687-byte metadata reads cover only 658..665. Its PRG96 code
  and metadata are byte-identical to the source-clamped proof; body pages do
  not reach 666. Zero carrier 667 remains occupied.
- Page 846 was rejected: Parodius really publishes that intentionally zero
  special-effects page. All 18 current body/special/pickup table rows are now
  included, rather than relying on the earlier dictionary omission.
- The changed Karnov scene call is the source-assembled Tank continuation
  `CE:AFD6 MtFreshV5`: genuine `D5:B57E ThSceneInit`, then `9F:BF69 MtColdLoadV4`,
  then RTS. The actual named MT_CONTACT grant, blob and native call substitution
  bind those bytes; no unexplained restore operands remain.
- Actual current publisher tests pass 2,160 setter instruction cuts and 2,376
  native-menu clear/restore cuts with 4,575 real lag-NMI/RTI returns. All nine
  proposed pages occur as unpublished transient pairs and none is written to
  a live CHR window. The audio child is an explicit return port in this CPU
  fixture. This is not a hardware or new-owner Main/IRQ proof.

Root's subsequent candidate differs in two Arthur row34 operands, with no
publisher change; root owns that successor binding. No helper has written
the granted physical pages or added Bub/Bob to the menu. Bub/Bob needs a new
base family, likely a fifth menu row; an existing family must not be replaced.

## Private native adapters: current qualification boundary

The private v3 model executes the source actor and actual v30 native CPU
services. Qualified leaves cover normalized input/once-per-update cadence,
16-bit world transport, native metatile queries, solid ceilings, native pit/
injury death, scene/new-life initialization, source 9px hurt geometry, trap
association/capture, validated native position/restore, exactly-once native
pop credit, owner-specific trapped-enemy admission, actor-birth invalidation,
retirement, and bounded native 8x16 OAM with the original atlas. It does not use
STOP to freeze trapped bodies: STOP leaves native contacts active.

CPU checks cover both identities' 43px jump, held-A bubble riding without a
new edge, source stage1/rank7 trap deadline40, actual AI resume without defeat
on timeout, one genuine native defeat per pop in each of six enemy slots,
all15 logical bubble slots, 882 compiled terrain callbacks, 441 source/native
box comparisons, 882 compiled hurt-distance cases, recycle/death controls,
and aligned/clipped OAM. Trapped victims retain native art inside original
source bubble pixels. No helper platform or full1-1 result exists for either
identity.

At the qualified 7,906-byte checkpoint, 254 bytes remained before `$BFE0`.
The public 37-row table already reserves 111 bytes and still rejects every
row. **That was not a completed whole-service fit:** update ordering and camera
pool translation were Python orchestration. The next private source revision
is compiling/measuring those paths; its in-progress assembly is excluded from
the first source-core/resource commit. Actual shared owner/birth/AI/contact
ingresses, source sound/score/UI/stage adapters, resident loader/retirement
authentication, Main/IRQ and native controller qualification remain separate.
The current Excitebike loader is owner-specific556B; none of its bytes or
eight spare resident bytes are assumed available to Bub/Bob.
