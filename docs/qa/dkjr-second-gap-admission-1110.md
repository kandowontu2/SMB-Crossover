# DK Jr. second-gap production admission

The in-memory builder applies to exact b031. It produces
`c506ffea482d031a7c3ea6e7866c482e50629494e500443a7bfbeab1dc9270ed`
and DK Jr. cookie `a72801b96058ad9af823ba7f575bf9d0`. The candidate is ready
for the menu-to-gap emulator replay.

The allocator admits a ninth helper in the loaded 1-1 room when camera-left
is X1121–1152. It uses a free stock enemy slot and calls `InitEnemyObject`
for ID `$28` at world left X1408, center X1432 and initial top Y208. Native
box 6 and both stock horizontal oscillator counters survive construction.
The admission cursor advances once after successful birth. A full pool
retries during the same camera window. The eight pipe helper rows retain
their original camera windows, vertical centers, and box 5 override.

| Existing DK Jr. owner interval, half-open | Use |
|---|---|
| RAM3 `$B624..$B6A5` | Platform refresh and shared actor birth fields |
| RAM3 `$B7B8..$B7BB` | Existing allocator tail jump |
| RAM3 `$BD3C..$BD45` | Existing pipe box override and refresh jump |
| RAM2 `$D18B..$D200` | Room/window scope, allocator and ordinal bases |
| RAM2 `$D2C4..$D2D5` | World X and vertical oscillator tables |
| RAM2 `$D2FC..$D300` | Camera start offsets |
| RAM2 `$D7FC..$D800` | Camera window masks |

The refresh scans the active pool once, with the existing scratch save and
restore, after scope admission. That supplies the space for both actor
types' birth fields. The builder reassembles the parent spans and compares
every preimage before patching. It modifies only physical CHR pages 881,
883 and 960 and the DK Jr. cookie. The already-redirected fruit tiles and all
legal atlas selections retain their image data. The cold program, both
header spans and shared platform engine retain their bytes.

The complete CPU suite covers 14,336 camera/cursor cases, 108 full-pool
retry and slot-birth cases, two wrong-room cases and two warm life resets.
Actual cold readback verifies every DK Jr. payload byte and both committed
headers on the parent and candidate. The 810 paired refresh cases preserve
registers, final memory and mapper state. Active calls vary by −54 to +6 CPU
cycles. The empty/inactive path adds 451 cycles. Across 28 full idle and
walking updates with no actors, player states agree and the same 451-cycle
increase raises the range from 47,803–53,077 to 48,254–53,528 CPU cycles.
Physical frame cadence still needs emulator measurement.

In the parser-backed CPU route, the only translated input is ingress at
X1220/Y176. The production allocator itself creates the actor at camera
X1121 and player X1233. At X1366, wait for the actor's left edge X1408 with
movement direction 2. Hold Right+A for eight gameplay updates, then Right.
The original landing executes at X1393. The player acquires the far bank
at X1412/Y176, then reaches X1424/Y176 with two lives on update 354.

The pure builder is `check_dkjr_second_gap_admission_1110.proposal(b031_raw)`.
It returns the candidate bytes, cookie and source labels in memory. The
checker uses exact b031 in Downloads and retains zero output files.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B tools/audit/run_bounded_build_v1.py --output build/dkjr-gap-admission-1110 --max-files 1 --timeout 600 -- python -B tools/audit/check_dkjr_second_gap_admission_1110.py
```
