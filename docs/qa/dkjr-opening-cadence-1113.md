# DK Jr opening cost and pending physical cadence

No physical cadence or FPS conclusion is made here. Root owns the sole
Mesen queue; the factories below are read-only and create no captures.

`check_dkjr_opening_cost_1113.py` exits0 in session68490. The original NROM
is `C:/NES/Donkey Kong Jr. (World) (Rev 1).nes`, SHA256
`1bc7fdc98c29b2c51438c3ce92ca37fac61b939a7cf100c644fed37206cf2cf6`.
It executes normal reset,243 supplied NMI epochs to the active scene, then
32 idle and32 Right epochs. Each epoch enters and returns the actual
originalD412 motor once. Idle instruction cycles min/mean/max are
13041/13947/15674; Right14703/15650.28125/16259. OriginalX stays8 idle and
walks8→28. PPU readiness is untimed and DMA/raster stalls are not modeled.

The same test executes the authentic current menu/cold/parser and settles
the generic opening seed naturally for21 updates. On exact769 atX87/Y176,
there are zero active native enemy slots. Thirty-two complete scheduled
nativeMain calls each enter and return DK's actualD65E interval once:

| Phase | Complete Main min/mean/max cycles | DK interval mean cycles | Movement |
|---|---|---|---|
| Idle |48695 /48887.15625 /51545|6769.0625|87→87|
| Right |51410 /52886.75 /54425|10699.90625|87→107|

Both phases spend519040 aggregate cycles in mapped bank193, or16220/Main.
The hottest instructions AF35/AF38/AF3D are in the shared authentication
header loop. This is a source-backed optimization lead, not an assertion
that this loop alone causes a particular physical rate. The original and
current authored scenes/coordinates differ; their cycle totals are not
identical-geometry performance controls. The current model schedules one
Main per call, so its32/32 completion count cannot establish NES cadence.
No input-poll count is used as an update counter.

`replay_dkjr_opening_cadence_1113.py` exports strict factories for root:

- `controller(raw769)`: Lua
  `7307ac6c57ccde9f3028137d23c741fbbe703cf15cd4664fe296d505034c59ba`.
- `original_controller(originalNROM)`: Lua
  `bfadd17b98c67233f88496e122db84f961977c9f08311f34595e3c2f1c0734e2`.

They use fixed physical windows120 neutral,32 Right and32 Left, counting
actual dynamically matched return PC/SP separately from update entry,
controller serial reads and input-polled frames. Current requires normal
menu selection, no cheats, active grounded1-1, both lives and zero native
actors. Original uses normal Start and original active/ground checks.
The original has no qualified skipped-NMI RAM counter, so that field is
explicitly unavailable. The current uses its native NmiSkipped counter.

`check_dkjr_opening_cadence_1113.py` session34603 exits0, exercising all
three phase transitions and actual update return callbacks in both CPU
models (185 scheduled epochs each). Original serial read hooks dispatch;
the current route harness does not dispatch read hooks, which is reported
explicitly. These scheduled epochs are not native physical frames despite
the production Lua's intended receipt field name. The initial9280 original
fixture incorrectly sent title Start to an already-active CPU model and
paused it; CPU_CONTROLLER_OPENING now skips title input only for that
already-constructed fixture. Native title input is unchanged.

Root's exact current7307 native idle window is now positive, receipt
`249b3ce24615d741a531736eb0c8e066267d56fef6880a28983f694bb5504a0a`:
120 physical frames produce60 D65E entries and60 matched returns,
120 input-polled frames/240 controller reads and90 skipped-NMI increments.
The neutral state stays X40/Y176/source1/both lives. The first walk frame
then fails the original factory's overly restrictive native-state0 ground
predicate. This retains the valid idle row and does not qualify walking or
the full7307 script.

Root ran exact originalbfadd17b directly from the original NROM path, with
no copied ROM. Receipt
`2c1cea372453df49406a3f9fbf4e217f73b8993646c0f4f09f8d4e7d4655278c`
passes all three physical windows: idle120/120 actual motor entries and
matched returns; Right32/32 moves X8→28; Left32/32 returns X28→8. Each
window has one input-polled frame per physical frame and remains healthy
at Y199/source1. Thus the current opening's measured60/120 rate differs
from the donor's120/120 and is not explained by an intentional donor30Hz
motor schedule. The authored opening scenes still differ geometrically.

A separate `donor_ground_controller(raw769)` preserves the frozen7307
default and originalbfadd factories. It is Lua
`c49a943f8da7c82e00379386ce6f30e4983217104736550eb4657c654bcbbe50`.
It admits native states0/2 only with acknowledged donor current/prior1,
sourceY=nativeY+15, nativeY176, both lives, zero native actors and stage0/0.
Receipts also record native_state/prior_source/source_y. Bounded source
38166 exits0: the three ordinary phases and actual return callbacks pass
185 scheduled calls in each model. Current walking moves87→107→87.
Those scheduled calls remain a source harness check, not native cadence;
root's corrected current walking windows are still pending.

No optimization, source physics change, ROM output, nightly replacement
or release is implied by these measurements.
Every producer is bounded under `build/dkjr-head-bridge-1113`, max-files1,
stdout/in-memory only, zero generated files.
The1114 continuation uses absent output root `build/dkjr-handoff-lag-1114`
with the same one-file reservation and zero generated output files.
