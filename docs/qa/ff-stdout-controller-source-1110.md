# FF stdout-only native controller, 2026-11-10

Active standalone Lua source:
`tools/playthroughs/ff_full_stage_stdout_1110_v4.lua`, SHA256
`42ed1997f6c472ab3bfa12ab2c8c5a5020eb39963af7af8f7d82b67bf5d09f96`.
Root owns the sole Mesen queue, ROM/hash binding, stdout watchdog and native
outcome. This report qualifies source/API checks only, not a native stage clear.

The controller follows natural title to roster slot21 (Down twice, Right five
times), Select zero to three times for Fighter/White Mage/Black Mage/Thief,
then Start. Menu taps hold four physical frames and release eight. Gameplay
conditions and thresholds are ported from the frozen Python first-mushroom,
flower, earned-attack and full-stage controllers named in the Lua header.
It approaches the real mushroom block, tracks the real produced item, crosses
the native obstacles, bumps/collects the flower, commits the class-specific
earned attack against a naturally streamed enemy, then uses the original
full-stage lookahead controller through the native flag and active1-2. V3
preserves the first-mushroom controller body exactly and adds explicit sampled
input delivery and bounded grounded-obstacle retries afterward, as below.

Actual native Main at CPU `$82D9`, physical PRG byte1032921, counts logical
entries. Real caller-stack/SP-qualified returns at `$82BE` (normal) and `$82D0`
(native catch-up) drive decisions from completed native updates. Input changes
are supplied exclusively through `inputPolled`/`emu.setInput`; a catch-up that
does not sample a controller keeps the native sampled input. No NMI, actor,
physics, stage, terrain, power, position or timer state is synthesized.

The script emits one terminal `SMB_NATIVE_RECEIPT ` JSON line, stops with code0
or1, and latches callback failures. Receipts cover actual pickup callback
returns, sound/actor erase/floaty, both60-tick freezes, class damage return and
native HP/defeat, flag/entrance, private head callbacks, completed-loop world
and camera deltas, and physical/logical/catch-up/poll counts. Camera extrema
are evidence, not a blanket smoothness assertion. Bounds are12000 physical
frames and6000 actual Main entries. There are no file, memory-write, save/load,
reset, screenshot-file or video APIs.

Environment:

- `SMB_TEST_VARIANT`:0..3, default0.
- `SMB_STDOUT_ROM_SHA`: required lowercase64-digit SHA256. The runner must
  verify the launched ROM; Lua explicitly labels this as runner-supplied.
- `SMB_EXPECT_STAIR_STALL=1`: optional strict negative mode, accepted only with
  exact original c10 pin; requires the old X2225/engine8 stall after the earned
  prefix, rather than calling it a stage clear.
- `SMB_STDOUT_IMAGES=1`: optional, at most two in-memory PNGs encoded as
  `SMB_NATIVE_IMAGE ` base64 lines. Default0. The receipt records tag/order/frame;
  captures reflect completed PPU frames, not a source-pixel identity proof.

## Retained first native negative and outline correction

Frozen v1 `tools/playthroughs/ff_full_stage_stdout_1110.lua`, SHA256
`1e11e26049e82ebe7db046dfc3a18a6e3e5927edb34985aabe325609bec68250`,
stopped on root's actual private96e0 Mesen run at first active physical
frame340, Main314, X40/Y176/lives2. Its assertion that `PlayerOutlinesOff` must
equal0 was an invalid physical-start assumption copied from a zero-initialized
CPU menu arena. That failure is retained; no product ROM was changed for it.

Authentic `src/characters.s:194` loads1 and stores `PlayerOutlinesOff` with the
comment that extra black masks are opt-in. The v2 derivative changes only
that observer assertion to the real cold default1, adds its value to snapshots,
and explains the correction in comments. The original Lua remains byte-exact.

This is not proof that all requested FF shadows are always rendered. The
current `FfRenderChunk::Admit` source and actual kernel read at `$B57D` still
conditionally omit bit32 extra black-mask records when this flag is1; ordinary
non-bit32 source cells bypass that filter. The host early body-chunk iterator
also consults this option. The user's separate request for forced FF shadows
therefore remains explicitly unqualified by this route run and needs its own
source/art/OAM assessment and any required product repair. Neither flag value
alone proves mandatory original black-pixel fidelity.

## Zero-output source/API qualification

`tools/audit/check_ff_stdout_controller_source_1110.py`, SHA256
`708104d52a3c43f2154304857ea0642374e640d4c56993f73724003fe69a95bc`,
and v2 derivative `tools/audit/check_ff_stdout_controller_source_1110_v2.py`,
SHA256 `722f7a9ce32758f1fc0c4ffc41cee9b4aa9ed821914710895e1f74bc5ae0235d`,
pass using the already-live Lua5.4 binary read-only:
`build/smb2-final62-observer-lua-deps-v1/lupa/lua54.cp314-win_amd64.pyd`,
SHA256 `0b763f9765d059ebff66d11a2867176b263f7f6fbbb51cbdd876aa05f7f5c9b2`.
No dependency was installed, extracted or copied.

The checks compile/execute the real Lua with a mocked emulator API, compare46
RAM/table constants against the existing symbol bundle, pin all five Python
controllers, and exercise all four menu class edges, stack/return handling,
both60-tick lifecycles, class-specific damage, flag/completion, two base64 image
messages, the expected-stair branch, invalid variant, callback failure latch,
and both runtime bounds. Mock fixture writes affect plain test tables only;
they execute no ROM, game, PPU, audio or native physics. The v2 checker verifies
the exact minimal derivative and authentic cold/filter source snippets.

```text
python -B tools/audit/run_bounded_build_v1.py --output build/ff-stdout-controller-source-1110 --max-files 1 --timeout 120 -- python -B tools/audit/check_ff_stdout_controller_source_1110_v2.py --output build/ff-stdout-controller-source-1110
```

Exit0, zero generated files, output root absent. Root's native Mesen receipts
must be assessed independently; these API mocks are not gameplay evidence.

## Retained v2 physical failure and v3 jump delivery

Frozen v2 SHA256
`40f5f3e521d14a3facd80b95a2ba21466e375d5f5f3a140818ee74be2fc55a9e`
passes the real earned-mushroom collection/60 ticks/palette in root's actual
Mesen runs, then reaches the flower controller bound1100 at the second pipe:
X593/Y176, camera483, engine8, Power/Earned1, lives2, no injury. Phaseflower
starts X420/Y118 at physical1196. Both private96e0 and original publicc10 end
at the same state and Main1869; physical frames3396 versus3394. Root's c10
receipt SHA256 is
`8130576dbcb79c3cd7cf37bf6873463ddba28ebac8ce602e457135e0d7b20306`.
This is retained as a physical controller failure predating the ROM change,
not a new candidate-only gameplay regression. Its c10 cadence is3054 gameplay
physical frames,1506 with no completed update,724 native catch-up updates;
the controller poll observer reports no missing polls.

V3 addresses the difference between a one-logical-update input pulse and real
sampled input. Authentic `src/final_fantasy_core.s` computes
`FfFresh=(SavedJoypadBits XOR FfPrevious) AND SavedJoypadBits`; the actual private
read starts at `$AACC`. A fresh grounded A reaches `$AB6D` after the genuine
motor sets VY=-5.25. The source explicitly has no release-height cut.

After the unchanged mushroom prefix, V3 holds a requested A through catch-up
decisions until the existing source accepts it. If the source previously held
A, it first waits for actual Saved/FfPrevious release. It then requires the
real fresh-ground-A acceptance callback and a completed airborne witness,
holds23 further Main updates, and releases. Unaccepted press/release is bounded
at16 Main updates. Acceptance with no completed airborne state after four
updates is recorded as blocked and releases for a fresh retry, rather than
being reported as a successful takeoff. Original flower obstacle cues retry
only while grounded, at the original greater-than35 spacing, at most8 requests
per pipe cue. The existing phase bounds and all earned/damage/death assertions
remain intact. This is a controller adaptation, not an original frozen-Python
route equivalence or a change to ROM movement.

The separate bounded `jump_delivery` log retains up to64 requests with raw
SavedJoypadBits, native AB/previousAB, source FfPrevious/FfFresh/FfJump,
JumpSwimTimer/SwimmingFlag, position, phase and Main/poll clocks. It observes
request, poll, at most six source reads, actual acceptance, airborne and release.
Optional image2 queues at real source jump acceptance near pipe608
(X540..640); image1 remains the opening active frame. Neither image is written
to disk. Root binds both c10 and96e0 to the same source for native comparison.

`tools/audit/check_ff_stdout_controller_source_1110_v3.py` additionally checks
all54 current constants, pins v1/v2, proves the mushroom controller body is
unchanged, and API-mocks an A pulse surviving unpolled catch-up, required fresh
release,23-update hold after source acceptance/airborne, blocked acceptance,
and a no-acceptance timeout. These are plain-table API tests, not ROM gameplay.
The bounded v3 source check exits0 with zero outputs; native v3 outcome is
owned separately by root.

## Retained v3 physical prefix and v4 early release

Root's actual private96e0/v3 run completes both earned pickups, exactly60 ticks
each and the class palettes, then Fighter's150-damage native hit defeats the
Goomba at playerX1500/enemyX1526. It subsequently fails on real native injury
at stage19, Main1643, physical2949, playerX1530/Y176. Root receipt SHA256:
`ed5b5220c4c829227f4f182943fdfa758e7da2cfe96bffc81887c6ffc0149cbe`.
The surviving Goomba is slot1/X1540/Y184; the prior defeated slot0 is state34,
HP0/X1546/Y168. Both optional PNGs are valid: the pipe608 takeoff shows the
red source body; the initial active frame precedes its first body publication.

Actual stage A acceptance is Main1626 at X1500/Y176 and the completed airborne
witness is the same Main, X1502/Y170. A source read at1630 shows X1507/Y156.
The low brick ceiling then ends this jump and the player returns to Y176 while
v3 still holds A for23 updates. A continued held A cannot create a fresh source
edge after landing. This is a retained failed controller attempt, not an
accepted native full-stage pass.

V4 changes only jump release: after genuine source acceptance and completed
airborne state, it releases A immediately. It suppresses any remaining old
raw hold command until that command goes low, so a catch-up cannot resurrect
the old press. A later fresh request still works. The motor has no release
height cut, so this changes input edge scheduling without replacing physics.
There is no additional combat policy or ROM change in v4; grounded obstacle
retries, source diagnostics and all existing phase/damage assertions remain.

`tools/audit/check_ff_stdout_controller_source_1110_v4.py`, SHA256
`1d9f7f8c1ad35c9097c221f1d6a13421e6e67014d56833e93be4b7813859f592`,
passes the inherited source/API suite plus immediate-release, suppressed old
hold/fresh later request, and source-accepted-but-blocked cases. V1/v2/v3 remain
byte-exact. Bounded v4 source checks create zero files; root owns its pending
actual native result.

## Actual v4 results and v5 sampled-airborne decline

Root's actual v4 Fighter/private96e0 run clears full1-1 into underground1-2,
with no injury, lives2, Power/Earned2, both60-tick earned transformations and
native150-damage acceptance. Single-run witness: physical6738/Main3813,
stage2189; actual flag physical5065/Main2644. Receipt SHA256:
`5ff65b833f37a33f2805cfe78a0b3f3d4e94c4fd3889e9f4cd64605b6e2ecd3d`.
The subsequent all-class campaign also passes Fighter (physical6739) and White
Mage (physical6759) without injury into1-2. It aborts before delivery at Black
Mage's unaccepted-A observer guard; Thief is not qualified by that campaign.

Black's terminal state is stage399/Main2058/physical3843, X2122/Y138,
state2/falling, VY `[0,28,3]`, lives2/Power/Earned2/no injury. Actual source
Jump0/Fresh0/Previous129/Saved129 means a request decided while grounded was
sampled after walking off a roof; original FfMovement correctly does not enter
its ground-A branch while airborne. This is an invalid observer assumption,
not a manufactured successful jump or an observed gameplay injury.

Standalone v5 `tools/playthroughs/ff_full_stage_stdout_1110_v5.lua`, SHA256
`aa18b8bcf1b81bbd817e507d1228a5f889dfea09cf73015c68f93de2c8fa4025`,
records an unaccepted A actually sampled at `$AACC` in native airborne state
as `sampled-airborne-declined-not-accepted`. It releases controller A and allows
a fresh request after landing. It does not add acceptance/airborne-success
fields, move the actor or alter source flags. Actual `$AB6D` acceptance remains
required for a successful jump, and an unexplained unaccepted grounded request
still fails the16-Main guard. Earned-pickup, damage, no-injury, flag and lives
requirements are unchanged; frozen v4 remains byte-exact.

The v5 source/API checker inherits the full suite and separately verifies rising
and falling decline/release/fresh-ground retry plus the retained unexplained
grounded timeout. Zero outputs. Root owns the pending native v5 campaign;
public/nightly remains c10 at this handoff.
