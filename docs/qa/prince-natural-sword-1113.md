# Prince natural pickup route on the current nightly

ROM SHA256:
`65ee94ca9ac6e1b5ad44303d08f76ecbc175a88232c82ef8c32712edf150a643`.
This is controller-only Mesen testing from the Downloads launch path. No
ROM changes, emulated state writes, cheats, added helpers or captures.

The current adapter authenticates the complete Prince cold packet and its
`a726024146cc2049b14dcc581a3340fe` cookie. It uses the existing current
native support publication at D746. The ordinary first-pickup approach is
runout390, face right, fresh Up80 and observe100. The initial runout360
probe climbed onto the brick row instead of collecting the mushroom; its
timeout is an input-route failure, not evidence of a gameplay regression.

## Corrected item observer

The older pickup script reads slot5's flag at15, ID at1C, state at24, X at7B
and Y atC3, but reads the powerup type from34, belonging to slot0. The
current adapter consistently reads type39 for slot5. The previous result
therefore misidentified the stationary flower as a healing mushroom. No
powerup behavior was changed to make the test pass.

The corrected default run passes at frame5756, commit2421, X1245/Y176,
HP4 and both lives. It earns the first mushroom, crosses four native pipes
and the first pit, hits the real flower block and observes the native
kind1 flower. The flower is not yet collected in this default probe.

- Receipt SHA256: `f374af376a053702a35bea92ffbc0e4865508fe12bcc86db9de824926ba5cb3f`.
- Controller SHA256: `fd01530f67b1bcf923fa5a66d91bf06cc95038f2d79a10c5f0826aa7e5878bd7`.

## Route findings and remaining gate

The unchanged standing-jump third-pipe route incurs original fall damage:
fall counter3, X844/Y176, source A291 debits HP5 to4. The alternative
Down+Right descent avoids that fall debit but meets the Goombas before
its running jump is admitted. The original unarmed defender then debits
all five HP. Waiting for the normal running-pose gate alone still meets
the enemy at the same position. These are negative route observations;
the test does not bypass fall damage or combat rules.

The optional `--collect-sword` continuation uses the actual connected
flower ledge geometry, original careful steps, turn, Up climb and walking
to reach the stationary flower. Its acceptance requires a naturally
revealed mature slot5 flower, erased native actor and original sword
inventory. It is under qualification; default emergence proof does not
claim natural sword collection or combat. Existing placed-actor CPU
draw/parry/attack/defeat coverage remains in `prince-sword-controls-1112.md`.

The latest collection continuation is a negative alignment result, receipt
`16ab581d8a9625b716fd50b7b40d3c5198b585b49581da2ec535204285a5eac8`,
controller `754d90bc5cf5bc90b25b1fb3b9dba57ba1030b3145d509f8fc6cf63911cc14fa`.
Actual connected ledge tiles are X1232/51, X1248/C4 and X1264/51, with
empty columns on either side. The ordinary careful-step/turn sequence ends
at X1214/Y176. Up alone from there stretches without grabbing; Up+Right
walks under the row. The mature kind1 flower stays at X1248/Y119. There
is no sword grant in this run. Next work must qualify the original grab
alignment rather than assume this controller's ledge offset is correct.

Run through the bounded wrapper, reusing only root's unfinished two-file
output:

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/metal-flower-native-1112 --resume --max-files 2 --timeout 170 -- python -B tools/audit/replay_prince_current_pickups_1113.py
```

Add `--collect-sword` for the unfinished collection continuation. Root
retains a single controller output and the already delivered candidate.

## Current CPU alignment and placed-flower check

On installed `a3c5fa63872fbb3103ae57d9748fef233e8b2273e26d985aa4006b2492d81b8a`,
the checker authenticates the Prince packet and stages the observed flower
ledge at1232/1248/1264, top144, with camera left1148. Eighteen directed
positions execute the existing live controller. Facing right, initial
X1218 through1230 (two-pixel increments) reach original climb action10,
pose145 at X1289/Y113. Initial X1214/1216 do not grab. The nine tested
left-facing positions1278 through1294 do not reach that height.

The optional placed-flower check uses three initial positions1218/1220/1224,
native status1 and an explicitly placed mature flower in slot5 at1248/Y119.
It holds original Up, then requests Left when the climb reaches the cap.
All three execute the real native PowerUpObjHandler and collect the flower
at X1260/Y112: the actor is erased and original sword inventory becomes1.
Sword inventory itself is never seeded. These are directed position/terrain
and mature-item fixtures, not natural emergence or complete controller routes.
No raster inspection, helper, ROM edit or movement-constant change is involved.

The prepared natural controller now brakes its flower approach six pixels
later, uses Up alone for the grab, accepts the original action10 cap, and
walks back toward the stationary flower. Lua syntax passes with SHA256
`12f55c86840aa9750d0312c806f629b23e8cec5e8aa67483ffe77762934d3e66`.
That revised natural route has not run in Mesen; the existing25GB free-space
guard currently prevents a new native test. The adapter authenticates the
unrelated Karnov successor through its exact inverse and confirms the Prince
packet is identical to65ee. The older emergence receipt above retains its
stated65ee scope.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/metal-flower-native-1112 --resume --max-files 2 --timeout 180 -- python -B tools/audit/check_prince_flower_climb_1113.py --placed-flower
python -B tools/audit/run_bounded_build_v1.py --output build/metal-flower-native-1112 --resume --max-files 2 --timeout 120 -- python -B tools/audit/replay_prince_current_pickups_1113.py --collect-sword --check-only
```
