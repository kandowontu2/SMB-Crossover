# Excitebike readiness — November 2

## Delivered November 2

Current Downloads nightly SHA256:
`37959000690d3f9fe596823fc0910e86b9fc977448779360d523751764248b0c`.
Excitebike is selectable at row4, column6. Exact candidate and actual Downloads
tests pass throttle/turbo/coast/reverse, the source-derived61px back-lean jump,
landing and native graphics checks. Combined Arthur flower/torch and unchanged
Shinobi idle/walk/OAM regressions pass. Source checkpoint:
`docs/qa/checkpoints/2026-11-02/excitebike-source-v1`.

Full1-1 remains incomplete: the first controller crosses two pipes and reaches
world671, then continuous turbo overheats and the recovery path stalls at
state5/speed0. The third64px pipe was not reached, so this is not evidence for
adding a helper. No helper platforms were added. Earlier source proposals and
private negative tests below are historical, not current availability claims.

## Current private integration: repaired successor awaiting native qualification

The current combined successor is
`build/excitebike-pose-1101-v3/current3.nes`, SHA256
`37959000690d3f9fe596823fc0910e86b9fc977448779360d523751764248b0c`.
It adds the exact frozen Excitebike repair to installed Arthur wall/maturity
`b9e685ff`. Its 7,373 changed Ex bytes are strictly disjoint from all 198 Arthur
changed bytes; every other installed b9 byte is preserved. The complete byte
proof is `current3-composition.json`. No installation is claimed.

Its unchanged Excitebike counterpart is
`build/excitebike-pose-1101-v3/current2.nes`, SHA256
`23086fbfa3daa0f4b5b850166c51362eb6a7e8908230bd01cb1a679eadb15616`.
It preserves installed Shinobi v30 / Metal v41 / Arthur v4 `6f319d20` and
does not include the later independent Arthur side-clamp repair. Exact patch
preimages and source/CPU bindings are in `current2-composition.json`.
It publishes a stable zero native metasprite header, prevents the legacy shot
updater from replacing Excitebike CHR736, and routes actual native colors and
status calls to typed owner services. Every foreign UI owner tails the exact
original ROM leaf. Ex resident code uses 960 of 968 granted bytes; the approved
Sh shot-gate change uses one padding byte and moves its bbox entry ADD6→ADD7.
No other Sh span or private cookie is borrowed.

Root completed the frozen `native3/` on current2: its 1,303 completed-frame
hardware checks all pass, with real source colors calls and correct
CHR736..739, palette20/16/0F, `EXBIKE ` HUD and aligned OAM. Gameplay remains a
terminal negative: the 180-update straight windup hit a real enemy at world
X=314, entering original crashFF before A. Consequently there were zero
launches; Y remained176 and original recovery progressed to state5, lives2→2.
This is not an input-sampling failure. Preserve all three completed negatives.

Frozen `native4/ready.json` now binds current3 and uses original Right+B turbo
for40 Main epochs, four Up/Right/B prelean epochs, then fresh A for eight
epochs. A narrow ten-case source test (`controller-windup-CPU.json`) proves
this genuine control sequence reaches speed693/angle7 after56px windup and a
61px flat-floor rise, with no source crash/heat. Right-only90 reaches only
30px. Native4 retains the greater-than-30px assertion, hardware checks and
passive input/angle/speed/launch observers. The separate `arthur-flower/`
packet is the exact unchanged passing b9 flower/maturity/B-torch controller
rebound to current3. Root owns both runs; neither has completed yet. No full
1-1 or installation is claimed.

Current successor CPU checks cover 4,680 exact foreign UI contexts and 60 own
palette/status cases; 320 foreign shot-gate contexts, 234 actual bbox cases and
400 actual IRQ/lag-NMI cuts; and 271 completed normal-NMI checks of hardware
CHR, palette, HUD and OAM. Cold-copy proof covers 779 actual disabled-NMI cuts
and 118 actual pre-SEI IRQ cuts, including 80 live-upper-latch NMI cuts across
all sixteen copy/verify selectors. All 8,192 copied bytes, both full headers,
final $5130=0 and cold/warm guards pass. No CPU count establishes native 1-1.

## Preserved native negatives

The separate current counterpart is
`build/excitebike-pose-1101-v3/current.nes`, SHA256
`70621f954e65d0bc582fd6177a0a2f5eb50f3af3d51e39531a6fb81cd2800b85`,
built from installed Shinobi v30 / Metal v41 / Arthur v4 `6f319d20`.
Root ran the exact controller packet in `native/` for 1,848 physical frames.
Its terminal result is **failed**: ordinary cold menu ingress, idle, throttle,
coast and reverse worked, lives stayed 2→2, but the jump phase stayed at Y=176.
The three screenshots also show incorrect blue/green bike colors and malformed
HUD text (`TO MEG`). No installation or full 1-1 claim is authorized by this run.
Preserve `native/capture/result.json` and its screenshots. The next packet must
use a separate directory, retaining this negative evidence.

Root also completed `native2` on the same exact ROM. Holding A for eight Main
epochs produced one genuine source launch and a 30px rise (Y=176→146), with
lives still 2→2. Its passive observers found **zero** ExHostColors calls,
physical CHR window4=535 overwriting the intended736, and OAM tuples shifted
by one or more bytes. This second terminal negative is preserved separately.
The repaired successor uses a stable zero native SmPosePtr header,
an approved one-byte36/37 shot-bank gate extension (Sh bbox moves ADD6→ADD7),
and exact native colors/status ingress. A blanket HuColors rebind was rejected
by the all-profile CPU check because it changed Tank's palette. The successor
therefore forwards every foreign UI owner to the exact original ROM leaf.
No successor native pass or installation is claimed here.

CPU proofs are narrower than native gameplay: all 90 menu profiles and 720
Start/A flag cases, 167 real parser Main updates, and 270 real Main/normal-NMI
updates passed in the declared CPU peripheral model. Shared-route proof covers
1,824 callback cases, 5,328 foreign service cases, 144 Excitebike routes, and 84
IRQ/NMI/lag-NMI cuts. These do not override the native negative result; the
current successor cold-copy coverage is recorded above.

The deliberately adapted native terrain profile is 32px tall with side probes
1/14 and feet 2/13, matching the genuine generic clamp. Sixty-four actual
consumer fixtures at both sides/page seams separate by at most four pixels.
This is not a claim to recover the donor's original rider contact rectangle.
Original motor, pose, crash/recovery, heat and air arithmetic remain source
backed. Flat-floor source-backlean tests rise at most 61px, so native tall-pipe
traversal may need existing native helper platforms after contact qualification.
No Excitebike helpers have been added or verified.

The one-update A press was missed by source sampling; eight epochs produced
one real launch. Hardware publication and typed HUD repairs pass native3;
the early turbo jump route and combined Arthur regression await native4.
Resource leases and exact current preimages are recorded in `dispatch-lease.json`
and `current2-composition.json` under the single owned output above. Earlier
sections below describe historical recovery/proposals, not current admission.

The next source-backed unready character after Shinobi is Excitebike. Prince
of Persia now has a separately recovered source actor component and a resource
proposal; no host allocation or playable admission exists. Neither is playable in the current
nightly. Older continuation entries also call Metal Storm unselectable; those
entries predate its current full-stage result and must not be used as a current
roster count.

## Executable animation addition

`tools/audit/prepare_excitebike_pose_1101_v3.py` recovers original donor
E1F9..E269 into the relocatable `ExPose` entry. It retains the original recovery,
stopped, wheel/pedal, lean and airborne pose decisions, including writes to
private offsets 000E and 039F. It imports `ExState`; it does not borrow host
zero-page bytes. The previous component had generated art packets but did not
include this executable selector.

Run:

```powershell
python tools/audit/run_bounded_build_v1.py --output build/excitebike-pose-1101-v3 --resume --timeout 180 -- python -B tools/audit/prepare_excitebike_pose_1101_v3.py
```

Use `--resume` only for this unfinished output, or omit it when starting a new
output. The recipe reads the existing v2 `state-799.bin` fixture without copying
its source tree. It generates six files totaling 7,472 bytes. The compiled
selector is 182 bytes; 6,144 CPU comparisons pass across four actor indices, six
recovery states, sixteen angles and sixteen clock phases. All 23 known pose
indices occur. Application RAM, CPU registers, physical status flags and stack
pointer match the original; host zero page is unchanged. Execution costs
49–117 CPU cycles. This is CPU component evidence, not a native ROM playtest.

The existing `source-art.json` contains packets keyed by `source_pose`; the
renderer should look up the returned A value there. Do not invent another
animation table from elapsed host frames. X remains the source actor index.

## Integration still required

- Current front-end source identifies Excitebike as menu slot 29, `FmAlts`
  bit 16 clear, pending portrait/name index 24. Prince shares slot 29 with
  bit 16 set and pending index 25. These pending indices are not gameplay IDs.
- No Excitebike PRG/CHR or conditional RAM ownership grant exists among the
  current November 1 grants. Tank, Metal and Shinobi grants cannot be reused
  concurrently. Root must perform the current linked identity/resource census
  before assigning a raw ID and storage. A run of FF bytes alone is insufficient.
- Current component costs are 1,240 bytes of motion/temperature code, 76 bytes
  of tables and now 182 bytes of pose selection, before host adapters and native
  packet metadata. Source art contains 154 eight-by-eight patterns (2,464
  bytes). Do not assume it fits three physical pages after native eight-by-sixteen
  packet conversion. Existing component state is 2,048 bytes at ExState.
- Original source controls are A throttle, B turbo and left/right lean, with
  lane movement and automatic ramp launch. An SMB adapter must define deliberate
  jump input without feeding SMB tile IDs into the original slope tables or
  silently replacing the source acceleration/jump arithmetic.
- An owning constructor/retirement path, original timing cadence, world/camera
  export, terrain probes, enemy/damage/death handoff, rendering publication and
  native stage traversal remain necessary. Test the full 1-1 route before
  deciding which native helper platforms it needs.

No nightly, shared continuation, existing roster results, host assembly or
helper-platform inventory changed in this task. No Mesen instance was launched.

## Current resource proposal

`tools/audit/audit_excitebike_resources_1101_v1.py` reads the installed nightly
and asserts equality to the matching v41 candidate before executing the census.
Its receipt is `build/excitebike-pose-1101-v3/resource-census.json`, bound to
`27dee145eead745dfe94cc6e4734a88fdd03811c7f7c3c9d1ee55e54d3057318`.
The initial v40-bound attempt correctly refused the newly installed v41 image.

- Actual menu resolution and Select handling across 90 combinations leave raw
  IDs **37 and 38 unused**. Propose 37 for Excitebike and 38 for Prince. This
  does not establish that legacy gameplay tables safely accept either ID.
- Physical PRG bank **65**, offsets **0E00..1108**, CPU **AE00..B108**, has
  **776 bytes** of source-declared padding after Shinobi's 0800..0E00 reserve.
  The current bytes are all FF and the next common-record bytes match the
  original source asset. This is a concrete cold-loader allocation proposal;
  loader size and dispatch/retirement fit have not yet been measured.
- Physical CHR pages **728..739** are zero. The actual linked 35-entry Sunny
  table only selects pages **724..727**. All 90 menu combinations followed by
  the actual `X5PublishChr` avoid the proposed pages. This is final-publication
  menu evidence, not a test of every instruction cut or gameplay publisher.
  Root still needs complete other-owner reader/publisher closure before reuse.
- A conditional bank-3 code / bank-2 state overlay could reuse the existing
  mutually exclusive architecture. Proposed ExState is **C000..C800** and
  headers remain **BFE0/DFE0**. Existing owners must retire on every foreign
  identity/scene/constructor path before either bank changes. No conditional
  storage or header was written during this audit.

Run this census with the same bounded output root and `--resume`. Neither
resource proposal is a grant, and no current ROM bytes were modified.
