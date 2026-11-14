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

Actual root idle/walk windows remain pending. No optimization, source
physics change, ROM output, nightly replacement or release is implied.
Every producer is bounded under `build/dkjr-head-bridge-1113`, max-files1,
stdout/in-memory only, zero generated files.
