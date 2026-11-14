# Current native sprite windows and temporal private proposals

This is a source resource investigation against delivered82ec
`82ec0446873b28af458e7686fec87938feaf798a0a893b44e4dccfd071ccfd63`,
independently inverted to exact421 by the frozen common-reset composer. It
does not allocate a window or code/data byte, compose a private ROM, run Mesen,
or qualify a future change. The common reset and all176 hidden/cheat fixes stay
intact. Root's delivered common coverage is in
[shared-world-chr-reset-1114.md](shared-world-chr-reset-1114.md).

Frozen checker: `tools/audit/check_current_world_sprite_windows_1114.py`, SHA256
`54683a6c557fb022e11a05fae46844f7d290743a593573296b6ef990ebc17f1c`.
All commands run through the shared bounded wrapper, for example:

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/shared-world-sprite-audit-1114 --max-files 1 --timeout 600 -- python -B tools/audit/check_current_world_sprite_windows_1114.py
```

Separate modes are `--owners`, `--lifecycle`, `--poses`, `--render` and
`--runtime`. The default and these modes have terminal positive source results;
each returns only aggregate stdout. File-write and Mesen traps are installed by
the frozen CLI. Zero output files/bytes; the bounded output directory does not
exist. No historical audit producer, expanded source tree or proof graph was
restored. Only two pure pose-geometry reader functions were extracted with AST
from existing source; their exact hashes appear in `--poses`.

## Native world consumers

Current PRG4 is byte-identical in421 and82ec, SHA256
`4058e8d4703b48029a99d4835348ffa4958c4039588c2d8f0868f656e4c130c8`.
The compiled Star..Toad domain is IDs63..144. All656 actual metasprite renderer
cases (82 IDs, both facings, four palettes) use only sprite windows0..4. This
includes the powerups, native enemies/Bowser, particles and rescued retainers.
No optional mouse metasprite is compiled.

Direct current paths also execute: the fast Goomba kernel16 cases uses2;
world firebars16 frames with12 parts and brick debris4 frames with4 parts use1;
all11 floating-score controls use1; both vine sides use3; all5 spring states
use3; flag5 scores use3 for the flag and1 for its score. Firebar and brick
immutable descriptors are independently executed through the generic kernel.
The dead non-crossover legacy writers are not substituted for current paths.

The first vine fixture selected Hogan and emitted no OAM because the current
public entry goes through the selected-owner dispatch. It was not a game
failure or evidence of unused art. The explicit native selected0 rendering
unit emits E8/EA through that public entry; both sides pass. This unit does not
claim naturally reached vine gameplay. An initial render fixture attempted to
write a currently ROM-mapped virtual address; it was corrected to its explicit
RAM3 fixture. No ROM output or production mutation occurred.

## Current owners and retirement

Windows5/6/7 are temporal resources, not globally free. Roll owns6/7 under its
Bass alternate; Parodius owns6/7 under Vic's alternate, and other character
weapons have their selected dispatch. Actual Prince38 and classic Donkey
Kong28 calls to `RlIsActive`, `VvIsActive` and `InventorySupported` return C0.
`InventoryDrawPickups`, `SamusDrawShots` and `MegaManFullShotBank` produce no
5/6/7 software or hardware window write for either owner. The latter three
return carries are reported, not mislabeled as denial flags. Exact current
entry bytes/PRG/PC are emitted by `--owners`.

Genuine compiled UI navigation/Start/parser/constructor followed by8 ordinary
neutral Main updates for each owner retains logical5/6/7 `[24,25,26]` with
modes `[0,0,0]` and zero software writes to those windows. The HUD resource
fixture invokes the actual publisher: physical200 goes only to BG8, with no
sprite5/6/7 alias.

A separate finite retirement unit invokes the public setter on5/6/7, then
compiled `FmNativePrepare`. It clears all12 modes, restores logical0..7
`[18,20,21,22,23,24,25,26]`, and actual publication yields
`[14,16,17,18,19,20,21,21]`. This proves the existing native preparation
primitive; it is not a claim that a future candidate's every exit necessarily
calls it. The frozen common82 macro already restores1..11 on area-type change
while preserving0. A future remap still needs actual admitted caller, menu/lives
preview, death/restart, changed/unchanged area, pipe and NMI/busy qualification.
Direct unconditional private publishers must never be invoked under a foreign
selected owner. No global physical-CHR page ownership is inferred here.

## Smallest separate classic Donkey Kong proposal

All9 current body records and6 barrel records contain even source tiles below64.
Body stays window0. Existing `DkDraw` publishes private823 to1 and ORs40 into
both barrel tiles; this is the confirmed blank native Mushroom conflict. Its
selected-owner gate is exact `PHP/PHA/LDA $6002/CMP #28/BEQ +3/PLA/PLP/RTS`.
Current routine PRG12 `$DCAE..$DD6E` (half-open), file105662..105854, SHA256
`37848f72a1194db9c3b1316651c1a310bcc9278a7d2dca21ba75619c9f2dab80`.

| CPU | File instruction | Exact old→proposed | Changed operand file |
| --- | --- | --- | --- |
| DCD9 | 105705 | `A0 01`→`A0 07` | 105706 |
| DD1B | 105771 | `09 40`→`09 C1` | 105772 |
| DD23 | 105779 | `09 40`→`09 C1` | 105780 |

This proposes only a temporal7 lease for admitted classic Donkey Kong28 draw,
using the same immutable823 page. Source tiles24..46 become C1-based odd tile
IDs selecting7 with identical local pair offsets. No CHR copy, new art, record
mutation, new RAM or code growth is needed. `DkPortrait`/menu body9 and all body0
requests remain separate. No candidate has been composed; these exact three
operands and the temporal lease require Root's grant before qualification.

## Separate Prince proposal and runtime ABI

Authenticated cookie `a726026f8a1229edf5a0683733ba6baf`; current runtime SHA256
`c1f64b964b03c2cd7e7184f294f8ed53e1f8ebdd17ef21666a27da9c1ae034f4`;
metadata SHA256
`12723b0ee33c0e9acda75831e5c0b20a4afd61c96daead0b9d396096cacf89ea`.
Of239 frames,204 exist:147 one-page,53 two-page and4 three-page. All1289 source
parts have even tile IDs0..138. Math-only mapping0→0,1→5,2→6 with OR1 only on
owned tiles>=64 preserves every pair offset. Current pages, art and metadata
remain untouched.

The actual renderer executes408 finite fixtures (204 poses, both facings),
2578 emitted pieces. All31 page IDs0..30 and both physical-high values occur.
Three-page frames142/156/230/231 pass in both facings. Frame156 publishes
physical391/393/544; frame230/231 publish391/613/615. Page indices0/1/2 are
metadata indices, not physical banks. After the high helper, X already holds
the derived physical high byte. Y is the saved metadata stream cursor until
the window load; it is restored from the stack after publication.

Current page loop is BC30; the sole `LDY Window($BD04)` is BC40. The common
tile store is BC7E after `ReadTile D79C`. Runtime BDC3 is occupied by the
physical-high helper, followed by the existing body-compatibility helper and
one NOP; its old high-table label is not free space. Tile carry observations
are not a flags-liveness proof. A future helper must preserve flags or prove
its exact consumers. Prince code/storage funding is separate and does not
block the three-byte DK proposal.

The first renderer aggregate accidentally retained a mutable event-list
reference in its three-page receipt rows. Every per-case assertion passed,
but those rows displayed the last frame's calls. The list was copied and the
full408-fixture run repeated terminal positive with correct three-call rows.
Neither this correction nor the rendering units implies a private fix or
native graphics acceptance. Root's delivered82 Prince Mushroom remains an
orange fragment and DK's remains invisible, as recorded in the common QA.
