# DK Jr. second-gap support and fourth-pipe descent

The CPU checks use the exact b031 nightly, the native area parser and frame
loop, and the DK Jr. source controller. The fixtures translate the ingress
position and instantiate stock actors through `InitEnemyObject`. They cover
local geometry and controller timing. The second-gap actor still needs a
production admission path and an emulator replay from the character menu.

## Second gap in 1-1

The parser places solid floor at X1360 and X1424, with three empty 16-pixel
columns between them. The successful fixture uses stock horizontal platform
ID `$28`, box 6, initial left X1408, center X1432 and initial top Y208. The
platform runs its original horizontal oscillator.

From X1220, walk Right. The fixture instantiates the actor when camera-left
first reaches X1152, at player X1264. Stop on the bank at X1366. Wait for the
actor's left edge to return to X1408 with movement direction 2. Press Right+A
for eight gameplay updates, then hold Right. The CPU replay reaches
X1424/Y176 with two lives at update 406.

At update 355 the actor publishes its native top at Y208. DK Jr.'s world
builder appends that top plane through bank 3 `$B5C8..$B61C`, and original
landing entry `$A966` executes at X1393. The player reaches native ground
state at X1412/Y176 before the platform moves left out of body overlap. The
native direct-carry callback at `$AC29` does not run during this crossing.

The same jump with no actor loses at X1402/Y202. Starts with an actor at
X1376 or X1392 land briefly on its top. The actor remains active and continues
moving left, and its right edge clears the player's left edge before the far
bank becomes reachable. A local fixture with the successful X1408 spawn and
the same jump reaches X1424/Y176 at update 96.

## Fourth-pipe exit in 1-1

The local roof replay starts at X916/Y112. The stock ID `$25` descent actor
has left X944, center X960, initial top Y192 and box 5. At oscillator center
Y161, advancing to X975 on the actor and releasing rightward at descending
top Y193 reaches X980/Y176 with two lives. Waiting at X960 for that same
departure height loses at X978. Oscillator center Y177 with the step-only
controller never boards in the 1,000-update bound. These are local controller
comparisons alongside the separately verified continuous fourth-pipe route.

Both checkers use the current Downloads ROM when it matches either b031 or
a20d. They write receipts to stdout and retain zero build files.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B tools/audit/run_bounded_build_v1.py --output build/dkjr-second-gap-probe-1110 --max-files 1 --timeout 600 -- python -B tools/audit/check_dkjr_second_gap_probe_1110.py
python -B tools/audit/run_bounded_build_v1.py --output build/dkjr-fourth-descent-probe-1110 --max-files 1 --timeout 600 -- python -B tools/audit/check_dkjr_fourth_descent_probe_1110.py
```
