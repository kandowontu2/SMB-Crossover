# Native fourth-helper loss: trace the first private X change

Root38164 completed the v2 passive diagnostic on actual currentbc5. Original
ed3e gameplay remained negative, as expected. Diagnostic receipt SHA256:
`564acf2ea7f5b7d151a42cb03a3f949648d1376dd940ec2d7e6a960cb72d9300`.
The new observation changes the first-loss classification: **actual native
support first fails horizontally**, while the retained source model first
accepts a plane and loses it vertically on a later update. Neither result
authorizes applying the source footer hypothesis to native gameplay.

## Actual native evidence, distinct from source

At first qualified944 carry, Main3653/frame8889, nativeX928/Y109/camera848:

- Original X72/Y124, horizontal fraction96; native bbox[79,127,96,142].
- Helper slot3, actual plane141, published bbox[96,140,128,153], passenger3.
- Next D65E entry still has original X72.

At the first original support query, Main3654/frame8890, original X is already71:

- Original body query[78,124,95,139]; floor window[78,95,140,141].
- Actual B5C8 plane141 is vertically inside the window.
- Candidate left96 exceeds window right95, so horizontal overlap fails.
- No plane appends; WCount stays0. The original ground handler then stores4
  at A321. The subsequent A275 origin write loads current originalY124.
- Native wall query returnsA0.

The observed native-X decrease is later. CPU write75 changes160→159; emulator
observed PC isB2CA, just after `STA75` atB2C8. Its nearby current bytes fromB2C4
are `086d1f078575ad1d076900`. This is `DkjrNativePublishAnchor` exporting the
already changed original X, rather than the first demonstrated X cause.

Retained source12082 receipt
`2c42c3c278b8f154a81b9513041e0d5c9f9a338c276d0f9ce6fe0ed89865fc6a`
had nativeX929, an accepted initial139 plane, then a later140 plane outside
the unchanged original floor window. Its horizontal overlap stayed valid and
no native-X decrease was observed. Those source observations remain valid in
their own scope; see
[source first-loss QA](dkjr-fourth-first-loss-bc5-1115.md).

## Read-only source lead, not yet native cause

The unchanged source `DkjrNativePhase` calls `DkjrNativeShiftCamera` before
controls, platform refresh and original movement. That routine computes the
delta from current ScreenLeft to its saved CameraLow/High, then subtracts
the delta from `C203,X` for each live source body cell. X16 reaches C213.
Its current authenticated store is RAM3:BB27, `9D03C2`; normal emulator
post-instruction PC would beBB2A. This could explain72→71 if the cached camera
lags the current camera by1, but the native cached-camera values have not
yet been observed. A stale native relative-X cache is also unproven; the
current shift routine computes directly from native ScreenLeft and its own
saved camera, rather than reading native Player_Rel_XPos.

## Separate frozen passive successor

Factory `tools/audit/replay_dkjr_fourth_private_x_bc5_1115.py`, SHA256:
`f613664dab04e40492aeaaa23d57205e70e7178fa952c1266bb2397c6eaf9752`.

- `controller(rawbc5)` returns `(text, binding_descriptor)`.
- `from_probe_text(exact_e07_text, rawbc5)` is a strict fast path.
- Owning ROM:
  `bc5e275d1dd4dabab4b5b2def66f7643ae46aee17a31ab37887528b791594040`.
- Parent passive Lua:
  `e07e07be0e84cb2b439c1786170ba80e95e233e2440443514f67c5961c853158`.
- **New passive Lua:**
  **`ee3a1bcbc46f8495a346f5da8096a107e5b720c22f4ca3da7c7350d3c7e1f7f6`**.

The proven wall witness is replaced by the first private-X decrease witness.
There are still at most8 specific witnesses. Its CPU write targetC213 must
map to WorkRAM bank2/offset213, physical16915. The callback records the old
private X before the store, requested new byte, observed CPU PC/SP/AXYP and
nearby11 code bytes. It retains input/fraction, current and saved cameras,
camera delta/ready, native relative-X at571, world-relative X, and the implied
source/native anchor relationship. It does not alter or synthesize any field.

Two possible indexed writer windows are independently authenticated against
the exact current DK payload. If the observed PC matches one, the runtime
code mapping and every window byte must match. An unexpected writer remains
an observed PC/window and is not silently labeled as either known writer.

| Current writer | Store / observed post-PC | Carrier file / near-start | Exact11-byte window |
|---|---|---|---|
| Camera-shift indexed C203,X |BB27 /BB2A|1952564 /BB24|`ed38c49d03c2cacacacae0`|
| Explicit anchor import C213,X |B29E /B2A1|1937067 /B29B|`6df1c89d13c2cacacaca10`|

Window SHA256 respectively:
`965d096d74e2b3767569c9ceff4045417f5035ca71733ad6a09dd98449e32514`
and
`e7b8908a2b2b467b7b60733137eef39877c0607e3523ddbb7f3785584c560947`.
All preceding hook preimages, exact current payload/cookie/native envelope
and immutable v2 factory are also checked. Removing the new text restores
exact e07, then the unchanged1d4 and ed3e boundaries. All ordinary controls,
guards, timeout and completed D65E motor-return endpoint remain unchanged.

## Executed observer gate

Checker `tools/audit/check_dkjr_fourth_private_x_registration_1115.py`, SHA256
`47d86a452588017b5d75f6a7e151e16f726c58d02e2a2c0092b0ad1308419b96`.
Terminal PASS receipt SHA256:
`7c9021a560ffe00d6a3bae979ded6828ade9f0efc043f3fb8a0e2287737eed39`.

The Lua API mock executes all top-level registration with global guarded=nil:
36 memory hooks and both input/endFrame handlers install, then all inactive
closures and both events execute without an error receipt. A separate,
explicit observer-only mock checks wrong bank rejection, non-decrease rejection,
one-time capture and the actual camera-writer window classification withX16.
Its847→848 camera values are deliberate test data, not a native observation.
No ROM CPU or gameplay state is exercised by this registration gate.

Exact bounded root `build/dkjr-fourth-private-x-registration-1115`, max-files1,
600 seconds, remains absent/zero files. No active helper source handles,
PNGs, game writes, emulator, modified code, controls, lease or delivery.
Root alone will run the native calibration; no game or floor proposal is made
until the first actual private writer is explained.
