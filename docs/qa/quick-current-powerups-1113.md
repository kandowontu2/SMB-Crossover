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
