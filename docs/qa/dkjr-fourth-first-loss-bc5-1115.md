# First fourth-helper support loss: currentbc5 source evidence

The source trace isolates a vertical support loss while horizontal overlap
remains valid. One original floor probe accepts the helper; native carrying
does not continue, then the descending helper moves beyond the unchanged
two-pixel floor-probe window. The original fall transition and origin update
follow normally. This is source evidence on exactbc5, not a claim that the
hardware's additional one-pixel X shift has been explained or repaired.

## Exact diagnostic

New read-only checker `tools/audit/check_dkjr_fourth_first_loss_bc5_1115.py`,
SHA256 `ea9958a9936217481835cd3c9a7b5a95449a6a1d8bc11931436d68d0f96cc9d0`.
Terminal source12082 diagnostic PASS, receipt SHA256:
`2c42c3c278b8f154a81b9513041e0d5c9f9a338c276d0f9ce6fe0ed89865fc6a`.

It runs the same frozen ordinary `ed3e7206…` controller body on actual
`bc5e275d1dd4dabab4b5b2def66f7643ae46aee17a31ab37887528b791594040`,
using the strict Hot118 inverse only as a67 reference boundary. Complete
11433-byte DK ownership SHA remains
`9eda92c47548d0b5b8fa39efb0555367b61d9139ca45ecce2ca7f632093fbfff`.
Compiled Select/Start/parser/cold is genuine. No actor/player/terrain/health,
input or game-code fixture is installed after cold. The Python bus subclass
observes writes and delegates each original write unchanged.

The checker stops after four completed post-carry D65E returns. Counts:
4246 motor entries and matching returns, one actual944 position, four support
probes, four helper-plane candidates and one wall probe. It retains at most
eight specific witnesses; seven are populated. Native-X-decrease is absent.
There is no generic trajectory or per-frame state array.

The observer's source ticks are scheduler iterations; its motor serial counts
all D65E entries including the initial ready/constructor admission. They are
not native physical frames or interchangeable with the controller's active
`Main` counter.

## First transition, with real coordinates

Helper is the unchanged stage1-1 stock vertical actor25 at initial left944,
center960, top192, width32. It occupies slot3 in this source prefix. Camera
is848 and native playerX stays929 throughout this first-loss window.

| Specific boundary | Source tick / motor serial | Player nativeY / originalY | Helper rawY / bbox top | Result |
|---|---|---|---|---|
| First actual position, PRG71:AC29 |4241 /4242|107 /122|139 /137|passenger3; source1/native0|
| Next D65E entry |4242 /4243|107 /122|139 /137|source1/prior1, origin108|
| Support probe, RAM3:B065 |4242 /4243|107 /122|139 /139 after refresh|returnsA1, real helper plane selected|
| First source4 store, RAM3:A321 |4243 /4244|107 /122|140 /140|support list empty; passenger255|
| Fresh origin store, RAM3:A275 |4244 /4245|107 /122|141 /141|stores122 over108, source4/prior1|

At the first actual position, player bbox[80,127,97,142] and helper
bbox[96,137,128,150] still reflect the preceding roof/pre-move publication.
The helper is descending: its raw Y is139 and native VY is1.

At the next original support query:

- Actual original body query is[80,122,97,137].
- The floor wrapper's exact window is X80..97/Y138..139.
- Refreshed helper box is[96,139,128,152].
- The real B5C8 plane argument is139. Horizontal and vertical intersection
  both pass; the actual append returns with WCount0→4.
- Original support returnsA1 and selects contact[96,139,128,139].
- The immediately following original wall probe B061 returnsA0. No wall
  rectangle is published.

Thus the original floor query is initially correct. It recognizes the
helper at the narrow overlap, rather than rejecting an invented horizontal
boundary or treating it as a side wall.

Before the next original floor query, player bbox is correctly refreshed to
[80,122,97,137] and native Y remains107. Helper raw Y and published box top
are now140. Passenger is255 and there is no second native positioning call.
The unchanged floor window ends at139, so the helper's140 plane is outside
it and the support list is empty. The original ground handler stores4 at
A321. On state entry, A275 loads originalY122 and stores it as the new fall
origin; this is an ordinary fresh origin write, not demonstrated corruption.

All retained first-loss states have held/sample1 (Right), original direction4
and facing1; native direction is1. No native X decrease occurs in this source
window. Native x speed becomes0 while the original fractional X accumulator
is160; that alone is not an input reversal or wall recoil.

## Mechanism supported by source, and native limit

The native carrier positions DK Jr. at `platformTop−32`. The true original
16-pixel bbox projection ends at `nativeY+30`; at nativeY107 its footer is137,
two pixels above platformTop139. The original support query deliberately
tests bodyBottom+1..+2, so its initial138..139 query can recognize139. But it
cannot follow the descending platform once native overlap/positioning has
ceased and the platform reaches140. The real count of only one positioning
event and subsequent passenger255 agree with that loss.

The existing native large-platform pipeline checks collision before moving
the platform, then moves/positions it only if passenger admission succeeded.
The source observations therefore motivate inspecting the private-body footer
versus native platform-collision contract. They do not motivate widening the
gameplay body globally, changing original fall limits, inventing support or
resetting the origin to hide the later injury.

Hardware76234 independently had one944 carry and the same immediate loss,
but showed928→927 at adoption. This source run does not reproduce that X
decrease. Actual native bbox/query/first-store calibration may still reveal
an additional edge effect. The source result must not be relabeled as direct
hardware proof of a footer repair or of a horizontal boundary defect.

No new controller, ROM composition, source mount or code repair is performed
in this diagnostic. Existing native/footer sampler research and grants are
historical/private; any current change needs its own explicit measured scope,
caller/flags/restoration and native qualification. The frozen controller and
both preceding source/native failure receipts remain preserved in
[dkjr-public-fourth-carried-bc5-1115.md](dkjr-public-fourth-carried-bc5-1115.md).

The exact absent bounded root is `build/dkjr-fourth-first-loss-bc5-1115`,
max-files1/600 seconds, zero generated files. There is no live helper source
handle, emulator, image, patch or new ROM file.
