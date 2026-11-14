# Mario the Tank current full-stage controller — November14

Strict input is installed421379021e775e6e03357c0aa11d4cab04008452f94bc9e8938f0662cc0c979f.
This changes controls and readonly observation only. No ROM/game/cosmetic/helper
change, installation, patch asset or release is proposed.

Factory `tools/audit/replay_mario_tank_full11_1114.py` exposes `controller(raw)`
and `metadata(raw)`. Lua SHA256 is
`f6d5fce6e1aae6a0041065265abf903f50529d91ed25c0091473053052d9b132`.
Actual compiled slot0 Select seven times yields `MARIO THE TANK`, owner0,
MarioVariant7; both factory and genuine source cold start assert this result.
Native Lua operates the actual title/roster/Select/Start. Source menu arena
cannot reproduce real vblank; root native evidence remains the authority there.

Tank's intended small-state movement is the donor native Mario walk/jump through
its authenticated worker, not the ordinary Flash Mario movement owner. Powered
boots give the source contact/injury and terrain policies, with native timer/pit
death retained. This full route stays power0/Star0 and does not claim naturally
earned boots, their immunity/combat or terrain destruction. No ability is seeded.

The new factory calls the frozen294b Toad factory, whose actual native-physics
route fits Tank, then binds only Tank's compiled selector/config and adds
readonly Tank ownership/call assertions. Frozen factory SHA256 is
`e25b9510f2fbdc5ece466033ad02d8ba25abc19cf8359bb15e3bcfe669b3af61`.
Toad/Peach/Kamikaze factories and their Lua hashes remain unchanged. The closed
source driver9f56378f is reused by a separate explicit factory binding; closed
sibling source routes are not rerun.

Current owner proof includes22 complete PRG banks byte-exact to12397 (native
physics, loader, full-header gates, menu/graphics/dispatch) and exact carrier
pages501/502,2048bytes, SHA256
`5e8a1b5e0c26da6c6db3dae0c4d05a4e46386ba02b4b8a260c95c8a02f1c39aa`.
Actual cold-loaded RAM2 worker bytes are compared to those carriers, with the
complete16-byte cookie `a7f705017de422bb9753a6c535f03aa4`, after both1-1 and1-2
constructors. Native mapped worker PC B676/rawRAM2 offset1676 calls are observed
using exact current instruction preimages. No worker/code/health/terrain/actor/
position/ability/cheat fixture is inserted. All176 current hidden/cheat fixes
remain exact through the explicit typed421 normalization proof.

Source job95326 terminal PASS,2974 matched Main entries/returns:

- Native flag1737, ordinary castle1800 and next entrance2377.
- 25 completed living grounded1-2 updates atX40/Y176, engine8, lives2,
  power0, Star0, MarioVariant7, CHR mode0.
- 2783 actual Tank movement calls,58 in1-2. Full cookie and2048-byte worker
  comparisons pass in both areas. Status path contains only genuine status0.
- Source receipt SHA256
  `434bb360368b96b2d840b7b568880a83a6ce60ec0db73164dcbeab10ee3c4d98`.

These counts use source scheduler units, not physical video/APU timing. Main
return PC/SP and mapped preimages are authenticated; entry counts are separate.
Strict metadata rejects truncated, physics-corrupt, fa66 and12397 inputs, traps
file/Mesen writes and disallows mutable nightly rereads after initial input load.

Retain the genuine earlier input negative: sibling navigation controller
`fab28a946999fd94f58b5dba4a3c4ceb33d998c60f78972c8ee5535ca10b1758`
lost a natural life at source1665/X2441/maxX2450 in the final stair gap, despite
1663 real Tank movement calls and valid loaded owner. Receipt
`cb354799dad5be04116a655ba449701a0c560a8feed78552cd344a0a48d87f2d`.
This is a failed input route, not a new ROM defect or a negative against the
subsequent correctly mounted crossing.

Historical natural mushroom and boot acquisition remains a separate closed
7ec9 native scope, toX1212/no lost life, in
`checkpoints/2026-11-01/mario-the-tank-natural-powerups/receipt.json` and its
544232f0 native packet. It explicitly did not clear1-1. No historical expanded
build path was restored or claimed live, and those closed donor/pickup suites
were not rerun. Current natural S/L and powered combat/terrain gates remain.

Root owns the pending native queue. Tank staysU for a current full native stage
until root reports the separate f6d5 run; the source result alone is insufficient.
No helper was added or moved. Both affected stage coordinates in the ordinary
stair controller are positions earned by normal inputs, not placed actors.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/mario-tank-full11-source-1114 --max-files 1 --timeout 600 -- python -B tools/audit/check_mario_tank_full11_1114.py
```

Add `--metadata` for strict pin/selector/preservation checks only. The output root
remains absent: zero generated build files, ROMs, images or Mesen processes.
Protected user roster progress and unrelated Steve QA are untouched.
