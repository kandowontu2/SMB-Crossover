# Executed registration correction for the passive fourth-helper probe

The first passive observer did not start successfully in Mesen. Root21077 and
the unchanged retry65429 produced no native receipt. Root traced the startup
exception to `flFollow`: its definition preceded `local function guarded`,
so its internal reference resolved to a missing global. The prior syntax-only
compile gate did not execute this call. Neither run establishes a gameplay or
fourth-helper calibration result. Root stopped only its verified owned Mesen
process after identifying the exception; other sessions remained untouched.

The frozen v1 factory and Lua remain unchanged:

- Factory `replay_dkjr_fourth_first_loss_bc5_1115.py`:
  `e9899b33f9df4f4af5a69a09b984cf9c5115862ebabbc4ed72b68b9f151d79d5`.
- Lua `1d4bc4195d38f4b059890c5aefdf9bd5f5784750eb0dca9032ae6eb718da315f`.

## Separate frozen successor

`tools/audit/replay_dkjr_fourth_first_loss_bc5_v2_1115.py`, SHA256
`f4798c9f8ebc684f8d20dcf18b082093c68b2978e92da1b5ce922883e7e3b5fe`.

APIs:

- `controller(rawbc5)` returns `(text, binding_descriptor)`.
- `from_probe_text(exact_v1_text, rawbc5)` is the strict fast path.
- `from_text(exact_ed3e_text, rawbc5)` uses the frozen v1 transformation first.

Owning image remains exact
`bc5e275d1dd4dabab4b5b2def66f7643ae46aee17a31ab37887528b791594040`.
**New Lua SHA256:**
**`e07e07be0e84cb2b439c1786170ba80e95e233e2440443514f67c5961c853158`**.

The only Lua changes are a forward `local guarded` declaration before the
observer functions and replacement of the later `local function guarded(name,fn)`
declaration with `guarded=function(name,fn)`. The assignment occurs before any
callback registration. The global `guarded` remains nil in the executed fixture.

Removing those two changes restores exact v1. Removing v1's observer restores
exact unchanged ed3e:
`ed3e7206e7e2cd29f403048d4816de5c01f58768b53113eba5021f24ade6d4b1`.
The factory also regenerates the v1 transformation from that restored ed3e and
requires exact v1 equality. Ordinary inputs, guards, timeout, strong endpoint,
eight-witness maximum and all binding preimages are retained. The count scope
at the endpoint remains completed private D65E motor returns, not host Main.

## Executed Lua gate

`tools/audit/check_dkjr_fourth_first_loss_registration_v2_1115.py`, SHA256
`cfad76444a1e32dc2bf2675535da798ccc8f1240c66f4e4601c5577bae6b9b24`.

Bounded source session40374 completed PASS. Aggregate receipt SHA256:
`c885994232d0b2378b10a8398b41abcad605aa52966533e2d5ce5ef98c1ffc15`.

This executes Lua5.4 with explicit emulator API mocks and global `guarded=nil`:

- Exact v1 reproduces `attempt to call a nil value (global 'guarded')` after
  three static memory callbacks, before either event callback is installed.
- V2 executes all top-level registration and installs exactly36 static memory
  callbacks, including14 source-store and3 origin-store hooks, plus inputPolled
  and endFrame handlers. Every callback is a guarded closure with its expected
  label. No global guard is installed.
- Every static callback executes once with the mocked game inactive; both event
  handlers also execute. There is no stop or error receipt.
- Separate observer-only mock locals exercise support, wall and plane entry
  hooks and their dynamically installed return hooks. All3 matching returns
  complete; wrong PC and SP do not complete them; repeated entries do not add
  duplicate return hooks. These mocked locals are not production controller
  changes or real game-state fixtures.

The exact current public DK payload/cookie/native envelope and the five hook
preimages are authenticated as in
[v1 calibration](dkjr-fourth-native-calibration-bc5-1115.md). Source compile and
v2-to-v1-to-ed3e restoration pass. The first fast-path invocation correctly
rejected the mutable shared-slot controller after root reused that slot; the
successful gate regenerated the production text without relaxing its pin.

Exact bounded root:
`build/dkjr-fourth-loss-registration-v2-1115`, max-files1/600 seconds. The root
remains absent; zero generated files, PNGs, game writes, candidates or helper
emulator runs. No source handles remain active. Actual hardware calibration
is pending root's sole native queue. No new controls, game proposal, lease or
gameplay success is implied.
