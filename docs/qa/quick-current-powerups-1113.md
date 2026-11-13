# Quick Man current gameplay and powerup audit

Exact input is installeda3c5fa63872fbb3103ae57d9748fef233e8b2273e26d985aa4006b2492d81b8a.
This audit writes no ROM, output files or emulator captures. Root owns Mesen.
Karnov and the CHR739 allocation proposal remain frozen.

Quick Man was selected over Goku because Goku has newer native full1-1 and
helper/camera qualification on f205, including its source-aware pipe retry.
The specific retained Quick native packets found are short Oct30 UI smoke and
performance holds; they establish neither a current full stage nor natural
powerups. Historical fixture BRKs are not reused as positive evidence.

Actual current compiled-menu admission is slot9/cycle2, raw9/FmAlts32. The
existing CPU menu arena, Select/Start, native parser/cold constructor and60
opening input updates pass: X40/Y176→X127/Y127, engine8/lives2. The current
full Quick header in raw2 is `a7092005e731d952bdb4b950826271bc`. Source code
executes through conditional raw1; its BFE0 isFF, so that location is not
treated as a Quick cookie. Source HP/max are5E0A/5E2A, initially40.

`tools/audit/check_quick_powerups_current_1113.py` first runs declared native
actor fixtures. Real HuInjury supplies a4HP deficit for ordinary kinds0/1.
Native preparation preserves the supplied physical kind and owner9/FC, with
no invented item mapping or growth tier. Actual HandlePowerUpCollision then
erases the mature actor and heals36→40, leaving PlayerStatus0 and no hosted
growth freeze. Star sets native timer35/music64. 1UP goes through native
floatey handling and changes lives2→3 after12 actual Main/NMI updates. These
four fixtures do not prove natural item emergence or collection.

This behavior agrees with the existing Quick host source QhPrepare/QhPickup/
QhFullPower in `tools/audit/quickman_host_runtime_v3.s`: mushroom and flower
are health refills; Star/1UP delegate to MarioSourcePowerupCollision. The
native UnionPwrUpCore in `src/union_rare.s` chooses an ordinary powerup's
physical kind from PlayerStatus before preparation. Quick keeps status0, so
another ordinary authored block is expected to produce a mushroom again.
A naturally earned physical flower is not claimed by supplying kind1 to a
fixture. No new growth mapping is introduced here.

The enemy-free cost fixture explicitly clears the six enemy flags in a clone;
it is separate from the natural route. Each of64 logical updates executes
one actual IdleLoop/NMI/GameLoop. Idle has64 enemy-free samples with mean
GameLoop29256.05cycles/max30120. Walking right has18 enemy-free samples out
of64, mean29810.22/max32008cycles. QhMovement/QhUi/QhDraw each execute once
per update. Source/native worldX mismatch count is0; camera-relative maximum
is112 while walking, minimumSP204. These are CPU cycle/logical-update results;
no physical NES lag, cadence or speedup is claimed.

The shared standalone controller source
`tools/reference/quick_natural_powerups_1113.lua` uses only native controller
input and read-only observations. Its first-mushroom CPU route passes291
logical updates after the established cold opening. The actual C1 head effect
is X330/Y151, DYFF, low fraction7; authored mushroom336/Y135 genuinely emerges,
matures, and is collected through the mapped native handler at X401/Y176,
actual actor413/Y164. HP40/status0/lives2 remain, camera289. No actor, inventory,
health, terrain, position or engine state is written by this route.

Complete mushroom controller SHA256:
`a8b617b0a44587bfbb8875c828e95c019a36a58fbeb036e33ecb07ed20355dd4`.
API `check_quick_powerups_current_1113.controller(raw, 'mushroom')` returns
that standalone Lua string without producing a file. The source includes a
native title/menu Down/Right/two-Select/Start sequence for root's future Mesen
run; the CPU test reuses the established cold-menu arena/opening fixture, so
this is not a native physical startup qualification.

```
python -B tools/audit/run_bounded_build_v1.py --output build/quick-powerups-cpu-1113 --max-files 1 --timeout 240 -- python -B tools/audit/check_quick_powerups_current_1113.py
python -B tools/audit/run_bounded_build_v1.py --output build/quick-powerups-cpu-1113 --max-files 1 --timeout 240 -- python -B tools/audit/check_quick_powerups_current_1113.py --route mushroom --limit 1000
```

Both completed runs exit0 with zero outputs. Natural1UP/Star/second ordinary
item and full1-1 traversal remain in progress. No Quick helper placement,
source gameplay change, Mesen pass or completed full-stage claim is made.

The first items continuation (script8cdcb759ea68ab3e8a23a7bf8f83123271ad97bd9e3808f6ec66680746002189,
sourcec8b464b9) stalls X592/Y176 before the second pipe left608/top160,
HP40/lives2. This is a negative controller result. Its12-update A hold only
rises45 pixels; the pipe requires48. Fresh-A enemy-free opening tests execute
one original jump-store each: tap rises8pixels; hold12 rises45; hold40 rises50.
Holding B alongside A produces the same50-pixel curve. Air release/repress
does not create another jump. Full hold returns to ground on update40.

These results match supplied original Rockman CX ROM
e04a4523e4ff0a0c7bfad1d30acedb9140c0972fa3be1c62e5d42a09664b5f6e.
Physical PRG3C:8588 tests new A bit0,859F stores original04DF VY. Airborne
state6 starts8609;869A..86A5 caps rising VY to0100 if A is released. State12
starts3D:BE81 and tests its own fresh A atBE94..BE9E before859F. No airborne
doublejump is invented. The checker also executes bounded original ground
edge and preguarded air-release leaves directly from this retained donor.

The full-hold/wall-edge items controller now crosses all four early pipes
without a helper, genuinely collects the hidden1UP (authored1024/top128;
actual actor1058/Y165 at player1048/Y176) and the next ordinary mushroom
(authored1248/top144; actor1293/Y165, player1284/Y176). Lives become3 and
HP stays40. It subsequently lands above the Star row atX1606/Y112 and cannot
bump it from below, so the complete items run remains negative. This is a
controller approach issue, not a demonstrated source defect. All results
here remain CPU Main/NMI/controller evidence; native cadence and full1-1
are open. No new game bytes, helpers, ROM copies or generated outputs exist.

The under-row correction passes the natural items CPU route in1557 logical
Main/NMI updates. Only controller input changes: walk below the Star row and
reserve the long jump for the first pit. Genuine authored births are336/Y135
kind0,1024/Y119 kind3,1248/Y136 kind0,1616/Y135 kind2. All four mature before
the actual mapped native collector and are erased there. The Star actor is
1687/Y165 at player1677/Y176, epoch1556. Final HP40/max40, status0, lives3,
camera1565. This is not a natural physical flower: the second ordinary block
correctly follows Quick's unchanged health-refill/no-growth policy.

Passing items controller SHA256:
`a28640952287b1bf4d42c30c4ca988aede4be9e869bcec3b56b4dec4af63ba22`.
No native Mesen pass is implied. Root's capture guard remains blocked below
the unchanged25GB free-space floor; this audit has created zero generated
files. All four early pipes and the first gap use authentic jumps, with no
new helper placement. Full1-1, physical lag/cadence and native menu/start
verification remain open.

The full continuation then exposes a real host-adapter boundary to resolve.
Blind auto-hop misses the flag above the visible shaft (controller
4c2e1e3e112d3261381b7b2bb6dc7ed0f0a3252ace7366ceba4fdc3e40901c42,
source0956e57d); no full-stage pass follows. Releasing A near the last stair
and descending instead reaches X3152/Y176/high1, HP40/lives3, engine8, and
holding right remains clamped there for600 updates. Actual mapped native
HandleClimbing and FlagpoleCollision entries both have zero calls.

`--flag-diagnostic` replays the real item/stage prefix to2600 updates, then
observes three additional Main/NMI updates without repositioning. The source
queries X3169/Y188 and204 return ordinary solid material1. At world3168/Y187,
the actual rolling block buffer has flag shaft tile25hex, attributes07
(solid+climb); the base atY196 is61hex/attributes45 and must stay solid.
All four native side probe indices3..6 return0, because native right X is3167,
one pixel before the shaft. Source/native X conversion remains exact.

The mounted QuickManWorldProbe starts raw1:B165. Its original host source is
`tools/audit/quickman_host_world_v1.py`: every native MTILE_SOLID bit0 becomes
source ordinarysolid1. Consequently native climbables block the donor before
the retained native side effect can see them. The narrow proposed repair is
to map native climbable cells to source empty, retaining native BG/climb
handling and all ordinary/base solid material behavior. The private source
implementation and complete CPU gates are recorded inquick-climb-material-1113.md.
It preserves the native callback's complete register/flag contract, uses11
bytes in the existing copied Quick code tail, and changes no allocation.
At that checkpoint it was not installed or fully native-qualified; the final
repair is now installed as recorded inquick-climb-material-1113.md.

The diagnostic prints the bounded source queries, native probe fixtures,
actual rolling-buffer cells and mounted disassembly; no output file, source
extraction or ROM copy is made. Its native side calls are declared index
fixtures in clones, separate from the preceding natural-controller stage.

Root has now independently run the frozen scripts on actual Downloadsa3.
Natural items PASS:2969 physical frames/1526 logical updates, genuine
mushroom336, hidden1UP1024, ordinary mushroom1248, Star1616, all mature and
erased by the real native collector, HP40/lives3. Controllera2864095 above;
native receipt82bdd4532ed88725e0451af3cfaea2bd34b549a8d19e306f98d830a9de7fa950.
No physical flower grant is claimed.

The exact frozen full diagnostic2283a8e704a209b1bd9595a69eb87b3e4e956074682f312eb448c3fee051dcf5
also reproduces the pole stop in native Mesen:5380 physical/3053 updates,
X3152/Y176/high1, camera3040, HP40/lives3, no climbing/flag events, route-stall.
Native receiptbfdf42c2de27794ad03d3bc684d748bbffd7d819f8dffba9e82b9998583575b7.
APIcontroller(raw,'full') freezes sourcea7dc2ba8; native and CPU now agree on
the remaining actual host-world mapping defect. These are root-supplied
native receipts; this helper launched no emulator. Root's disk preflight now
permits Mesen again. No fix, install or delivery has been claimed.

Final outcome: root installed4641 and published the soleCurrent/Latestce922
IPS after same-control negative/positive testing and exact Downloads repeat.
Quick clears1-1 with all four authored items and reaches grounded1-2,
HP40/lives3. Seequick-climb-material-1113.md andquick-climb-delivery-1113.md
for complete pins and verification scope. The CLIs derive frozena3 explicitly
through the installed successor's checked inverse, preserving this audit's
baseline and frozen-script expectations. Physical flower acquisition remains
unclaimed under the existing no-growth policy. No helper placement changed.

The later Jay/Quick installed composite is
`aa50112845d1cf70cae0924f03326647b3d2514f876c756d70b134ee44f971d1`.
The read-only CLI explicitly applies the authenticated Jay inverse to recover
exact4641, then the Quick inverse and forward roundtrip to recover frozena3.
Its frozen parent PIN and scripts remain unchanged. The bounded zero-output
`--cold-only` run passed this chain and the real Quick menu/constructor/opening.
Root separately repeated the full native Quick route on exactaa501:5693
physical frames, all four items, grounded1-2, HP40/lives3; controller
`7711ef407ad23be3b432c586bec52dac0d801e1c43c3121a7c5bb269297bf052`,
receipt`50d2332176f026d924ce91d26851b18ff220dff37cbbd8e494e928b428c8666e`.
The current soleIPS is nowa5ecdd50c6e186415f9b4e3c75f53bcef7cf69df3012f02e6466a7e7413e33a1;
the precedingce922 delivery remains the Quick-only historical checkpoint.
