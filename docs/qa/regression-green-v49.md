# v49 green regression suite and final route pass

This update continues from Codex's installed HU checkpoint
(`roster-audit-v49-sophia-block-origin-hu`). HU's full `tools/verify.py` run had
688 passes, 73 failures and a failing stock-Mario comparison. The working build
now passes **all 757 emulator cases on both mappers plus the Mario trace check**
in one unchanged-fixture run (`python tools/verify.py --mmc5`).

## Runtime changes

Three small source changes. Each is checked against Codex's own evidence.

- **Sophia wall-climb flicker (real bug, since checkpoint C).** Holding toward a
  wall with the climb upgrade made Sophia attach and detach on alternate frames
  (x 94↔96). Attachment is re-decided each update from side contact. C's source
  side probe places her at `wallLeft-18`, but while attached all source terrain
  queries were rejected. The narrower native probe then saw no wall from that
  position. Only the two side consumers (`SophiaSourceSideProbe`,
  `SophiaSourceWall`) now keep the source body while wall-attached. Ceiling and
  rotated forms, feet and head keep their native fallback. The check runs only
  on the already-rejected path, so ordinary updates execute exactly HU's bytes:
  each `Native:` stub is a same-size jump into new code appended at the end of
  `SOPHIA_TERRAIN_COLD`.
- **Water Shield cache (MMC5 budget).** Installs Codex's reviewed EQ/ES candidate
  (`root49-water-cache-eq`, compiled review EW): the vector-key test moves into
  `EnsureWaterScale`'s only caller. MMC5 expansion max falls under the existing
  6100-cycle bound (was 6113/6114).
- **Block-origin wrapper cost.** HU's Sophia block-origin fix ran its wrapper on
  every character's block bump, about 35 cycles. That added one lag frame to
  Bill's fixed route and killed it in 1-3. Non-Sophia characters now test
  `SelectedCharacter` first and tail-call `InitBlock_XY_Pos`. Codex's 64-case
  native Sophia block regression (`root49-sophia-block-shift-hn`, HR) produces a
  CSV byte-identical to HU's admitted result on both mappers and modes.

Relative to HU only bank 5 (Sophia cold terrain), bank 9 (block-origin tail) and
bank 60 (Water Shield) change.

## Fixture changes

All 37 failing tests were bisected across the checkpoints since v48. Every
failure first appears at the integration that changed the corresponding rule.
29 first fail at Easy/Hard BY; the rest at DU or C.

- **Relocated bank pins (19 tests).** Fixtures pinned literal `CurrentBank`
  values, and BY/C moved `RosterMovement` (22→3), Mega Man movement (1→3),
  `LinkDeferredThrustFinish`, LSR effect finishes and `GuestInjuryStart`.
  `run_mesen.py` now exposes `B[label]`, each code label's physical 8 KiB PRG bank
  from the `.dbg`. Only guards whose literal equalled the hooked label's old bank
  were rewritten to `B.<label>`. Fixed-bank handlers (wall/head/bump) now use a
  physical-address check, as in Codex's G wall observer.
- **Intended source behavior (expectations updated, values cited from code).**
  - Mario: HARD water acceleration 350/7200, release friction .000001, walk cap
    175/120 and post-gravity fall cap 400/120. Spring launch is 400/950 in Q16.
    Mario's source injury replaces the native `$f0` shrink.
  - Bill: HARD Flare owns a center object, so three coexist. A teleported
    airborne Bill keeps the upright 31.5 waterline. The art repack moved Lance's
    walk bank 123→118; all 920 DMA pixel composites are unchanged.
  - Sophia: the 19 px source body stops at pipe−18 (430).
  - Samus: the brick-breaking suit rule is EASY. `menu-bootstrap.lua` gains
    `SelectEasyRules()` for such fixtures.
- **Rebased references.** Both Bill collision-equivalence CSVs are byte-identical
  on every checkpoint BY..HU and on both mappers. Their reference hashes now
  record that behavior, and the superseded hashes are kept in the JSON. The
  source-Mario trace (identical since BY) is frozen as
  `tests/mario-trace-reference.csv`. The stock baseline replay remains a smoke
  test.
- **Coverage scope.** Bill and Sophia leave the native head-cutoff matrix, and
  Sophia leaves the shared foot-clamp matrix: their source bodies no longer use
  those native paths. The arena reset clears Mario's longer invulnerability.
  The Samus head arena authors a real upward crossing. The Options label moved
  one column after the user's "PLAYER OUTLINES" rename.
- **Retired.** `mario-native-physics-control` and `mario-native-water-pit-control`.
  Mario no longer runs native physics; Luigi keeps the native-reference
  comparison.

## Routes and recordings

All 14 H fixed-controller routes (13 characters plus Lance, Easy, MMC3) replay
on the final build. All six stages clear through 2-2 with zero deaths, at their
original frame counts. Each route was then recorded on that exact ROM
(`build/roster-through-2-2/claude-final-video-<character>-v<variant>-mmc3/`):

- Native ZMBV segments and continuous PCM are kept.
- `playthrough-lossless.mkv` passes the exact decoded RGB/PCM check.
- `playthrough.mp4` is the delivery copy.
- Every movie has emulator frames − 1 video frames and non-silent audio.
- The 14 movies total about 4.4 GB.

| Route | Frames | Length |
| --- | ---: | ---: |
| Mario | 16991 | 4:43 |
| Mega Man | 32518 | 9:01 |
| Samus | 32224 | 8:56 |
| Bill | 34401 | 9:32 |
| Lance | 33254 | 9:13 |
| Link | 27058 | 7:30 |
| Simon | 28793 | 7:59 |
| Pit | 25750 | 7:08 |
| Rygar | 21537 | 5:58 |
| Luigi | 17412 | 4:50 |
| Bass | 29543 | 8:12 |
| Ryu | 23098 | 6:24 |
| Sophia | 25404 | 7:03 |
| Scrooge | 21742 | 6:02 |

No one has watched or listened through every frame. Codex's automated per-frame
review tool was not rerun on these movies.

## Not covered

MMC5 route replays, natural acquisition of every upgrade and special,
source-perfect geometry, and further lag reduction remain open, as in Codex's
goal index.
