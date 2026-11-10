# FF automatic entrance priority diagnostic, 2026-11-10

The first incorrect write is FF graphics clearing the native sideways-pipe
entrance signal. This is a real controller-route failure, not a synthetic
terrain or player-state fixture boundary.

The independent observer is `tools/audit/diagnose_ff_intro_stall_1110.py`,
SHA256 `9aada09aa2b861a799879e2d43e7f63d3196f5d354f1e1de62bef6fc162f50a5`.
It leaves the full-stage checker unchanged and verifies its exact SHA256
`4081ddb23a5e1c5dd5a59bfa87ae0058b108dc27f0b7fa2c1bb158ed98124439`
before and after execution. Its only cartridge change is a scoped read facade
and matching PIN before the existing genuine cold/menu/pickup/attack prefix.
Python memory-observer classes and CPU references add metadata only; no actor,
terrain, power, position, transition or RAM state is injected.

## First incorrect write

On exact private head-corner v1 candidate
`db20d5a53259b90b0c0892b416e8da78aab1815a1c68fb99c4a1974ad5326069`,
the genuine 1-2 entrance reaches X146/Y176, engine7, EntranceCtrl7. Streamed
native pipe cells are X160/Y176=`$1C`, X160/Y192=`$1F`; the adjacent pipe cells
at X176/Y176 and Y192 are `$1D` and `$20`.

1. Native physical PRG126:`$9CFA`, bytes `8D8705`, writes
   `Player_SprAttrib $0587` from `$00` to `$20`. The observer's raw map tag is
   254, the ROM-tagged representation of physical bank126. Native collision
   subsequently sets `ChangeAreaTimer` to `$A0`.
2. In the same frame, private RAM3:`$B3D5`, also `8D8705`, writes `$20` to `$00`.
   This is `FfGraphics` after `FfEnsure`: `LDA #0 / STA Player_SprAttrib` in
   `src/final_fantasy_render.s:19`.
3. All 256 retained actual native `PlayerEntrance` attribute reads return zero.
   There are 78 priority edges: 39 native set / FF clear pairs, with the first
   pair at X146. No actual native entrance timer decrement occurs.

The unchanged host contract is explicit: `src/collision.s:1511` sets bit `$20`
on sideways-pipe contact; `src/player.s:40` loads `Player_SprAttrib` and branches
to `IntroEntr` when nonzero, calling `EnterSidePipe` and decrementing
`ChangeAreaTimer`. Native `ResetPalStar` uses `AND #$FC` and preserves bit `$20`.
The observed clobber is the FF store, not that native palette update. The later
X240-to239 viewport clamp observed at physical PRG1:`$AA59` is downstream of the
missed pipe branch. Missing FF private movement callbacks after the flagpole
are not the cause.

The v1 route still reaches the actual 1-1 flagpole at step1023, X3161/Y120,
engine4, then the real level1 entrance. Its intentional diagnostic stop is
step2063, X230/Y176/engine7, lives2/power2/earned2, with no injuries.

## Independent v2 comparison

The same unchanged controller checker and observer run on exact in-memory
candidate `96e09ab1b67a7c75b89d49219e8e529582b9a05b7dd82dd3cd570fdb239212bd`.
Its source builder is `tools/audit/check_ff_head_corner_1110_v2.py`, SHA256
`e508771dbac9dfb42c33ca41b3d3af4c07f98f81fd2f742205f6e4a3ce690665`;
assembly source `tools/reference/ff_head_corner_1110_v2.s`, SHA256
`6e58b2460852e808031f64ce733545ca0bffc78da05e5b68860d929e98c7f0cd`.

Native PRG126:`$9CFA` again sets the signal at X146. Actual native entrance read
operand PC `$A05B` then reads `$20` with timer `$A0`; this is retained read151
(zero-based) of the capped 256-read log. There is no FF `$20`-to-zero clobber.
The observer records 211 timer writes, including 184 actual native decrements
at operand PC `$A068`. Pipe contacts can reset the timer while X aligns; the
final decrements at X160 are 4-to3-to2-to1-to0. The one later signal clear occurs
in next-area initialization, with timer0, AreaType changed1-to2 and
EntranceCtrl changed7-to0, rather than during the side-pipe handshake.

The unchanged route returns success at step2177: active native 1-2,
world0/level1, mode1/task3/engine8, X40/Y48, lives2/power2/earned2, no injury.
Its 1-1 flagpole witness is identical to v1.

## Reproduction and limits

Both final-source runs completed with exit0 through the shared bounded runner:

```text
python -B tools/audit/run_bounded_build_v1.py --output build/ff-intro-priority-original-1110 --max-files 1 --timeout 600 -- python -B tools/audit/diagnose_ff_intro_stall_1110.py --output build/ff-intro-priority-original-1110 --candidate v1 --prefix-only
python -B tools/audit/run_bounded_build_v1.py --output build/ff-intro-independent-diagnostic-1110 --max-files 1 --timeout 600 -- python -B tools/audit/diagnose_ff_intro_stall_1110.py --output build/ff-intro-independent-diagnostic-1110 --candidate v2 --prefix-only
```

Both roots remain absent: zero generated files, no ROM, Mesen, installation,
publication or frozen-source edits. This independently checks Fighter's genuine
logical CPU/controller/normal-NMI route and native entrance signal. The v2
candidate also includes the separately owned coin-filter change, so this is
not an isolated single-change differential for all gameplay. Other classes,
cold faults/interrupt cuts, physical cadence/audio and body OAM priority behind
the pipe are outside this observer's qualification. Root owns their tests and
any product/delivery decision. This observer did not retain the route's maximum
logical camera step. Root's separate v2 full-stage driver reports that its
at-most-two-pixel camera guard fails; that remains under investigation and this
entrance success does not qualify camera smoothness or a deliverable candidate.
Sonic constructor work remains deferred.
