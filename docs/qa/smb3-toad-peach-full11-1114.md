# SMB3 Toad/Peach current full-stage controls — November14

Strict input: installed421379021e775e6e03357c0aa11d4cab04008452f94bc9e8938f0662cc0c979f.
These are separate normal-controller replays, with no ROM, helper, cosmetic,
actor/terrain/position/health/ability/cheat change, installation or release.

Actual compiled Down twice from slot0 reaches slot16/SMB3 Mario, owner17.
Select twice yields SMB3 Toad/M3Variant2; three times yields SMB3 Peach/3.
Both the factory census and source cold fixture execute the real instructions.
The native controllers use genuine title/roster/Down/Select/Start. Source menu
arena lacks real vblank; root's actual native UI runs remain the authority.

Factories `replay_smb3_toad_full11_1114` and
`replay_smb3_peach_full11_1114` expose `controller(raw)`/`metadata(raw)`.
Shared `replay_smb3_alts_full11_1114` preserves frozen SMB1/Tank siblings and
inlines three retained SMB3 controller sources without editing them:

- `current_roster_chip_pickup_v2.lua`:b77a6897b302de2955ff32b83b03edff7b886cb340587184d1c21e50553cb34b.
- `current_roster_smb3_stair_v2.lua`:4fc9eec0882428141db17821b5d276712fd8ee597a95d9dbf3d05e7ea0070367.
- `current_roster_smb3_pole_v4.lua`:19fde5dedbd7252ef3aa87fc380a00363b0322a02e86d1d6e8bb788c6b044579.

The source checker explicitly binds the closed9f56378f readonly driver to the
new SMB3 factory and its compiled frontend. No old hover/controller suite or
closed sibling route is rerun. Full PRG66/81/90/91/92/124/126/127 and SMB3plus
CHR969..<1019 are byte-exact to12397. All176 current hidden/cheat changes remain
in the actual played421 image. Strict metadata rejects fa66,12397, truncation
and physics corruption; file/Mesen traps and no mutable-nightly-reread checks pass.

Actual M3ReadyB3, mapped M3Movement and M3Step execution are required. Completed
Main counts authenticate both normal/catch-up callers and matching return PC/SP.
Native flag, castle and entrance precede25 completed living grounded quiet1-2
updates, with at least25 actual next-area M3Movement calls.

SMB3 Toad source35862 terminal PASS:

- Lua SHA256 `c8f59a13d8acfddb8c87799bc223b68ab11b6ab6f53485fe54d02634d6b8b79b`.
- 2870 matched Main entries/returns; flag1632/castle1694/entrance2272.
- 25 completed grounded1-2 updates atX40/Y176/engine8/lives2/power1/Star0,
  owner17/variant2/CHR131.
- 1690 M3Movement calls,1644 actual native M3Step calls,58 next-area movement
  calls. Power1 is reached through ordinary inputs; complete natural-item
  collector/erase/popup/combat qualification remains separate.
- Source receipt SHA256
  `c931c3a481e37be321ac9b667c742d47a1d9048077d64ff9378d3f456059bce7`.

All source counts use scheduler units, never physical video/APU timing.

Retained Peach input negative: generic retained route8ea695ebc7c55f9a19282e0b0fc156e4935ce69e4edb02cd9afc7897868d4b7c
releases A as Peach descends above the final stair gap. Source1346 enters actual
death engine11 atX2468/Y242, lives still2 before its later decrement; it does
not clear1-1. There were1345 real movement/1299 native steps and64 airborne
MbFloatReady2 samples. Receipt
`6317aeab95b0d3b1beea98cfad3a85e6d55c9a560cf44d8db83dd7ce31b58b9a`.
This is a failed input route, not a claimed ROM defect. The next Peach-only
adaptation holds ordinary A across the actual final gap to use its intended
source hover; Toad's frozen text is unchanged.

Corrected SMB3 Peach source39162 terminal PASS:

- Lua SHA256 `bf45e99dc32da8c377588c344f8abd79c8970ad774f314529707dbf1d94594d1`.
- 2870 matched Main entries/returns; flag1634/castle1696/entrance2272.
- Same25 completed grounded1-2 endpoint, lives2/power1/Star0/variant3/CHR131.
- 1692 M3Movement calls,1646 actual M3Step calls and58 next-area movement
  calls.118 airborne MbFloatReady2 samples occur across the whole route;
  this is not118 consecutive updates from one hover charge or a changed limit.
- Source receipt SHA256
  `7863b410cc048c1e3d91b2b2abf4f712d163100117ab685efbb59e1859668199`.

Only Peach's new ordinary inputs hold A while airborne at2360<=X<2544, using
the unchanged source hover to cross the final gap. Toad's c8f59 text remains
exact. The earlier8ea6 source death is retained as a failed generic input route.

Root actual Downloads421 Toad10309/c8f59 is terminal NEGATIVE:
1386 physical frames,1202 Main entries/1201 completed returns, first active
Main293/frame309. Actual death engine11 atX1411/Y244/maxX1411, lives still2
before decrement: the second pit is not crossed to its far bank1424. Power0
reaches1 byMain770/X693, then returns0 by901/X768. Last retained grounded
checkpoints areMain1038/frame1172/X1026 and1140/frame1304/X1281; these are not
asserted to be the actual takeoff moments.909 mapped M3Movement and817 native
M3Step calls, no1-2. Receipt SHA256
`6682494587d964d6bc369581a305f46d55ee5d0662b967ead97a666ef18d8836`.
Root reports no files/images or ROM changes. The source2870 full pass remains
source-only; it is not relabeled as this native result. The source/native
navigation difference includes roughly169 added lag frames during gameplay.

Peachbf45 remains source-positive and natively held pending the same early-gap
calibration. Both identities remainU in the expanded checklist. A separate
successor will clock navigation from completed Main state, retain post-damage
form0 behavior, and add bounded actual movement-return/takeoff/button traces.
Neither frozen text is modified and no ROM bug is inferred.
No historical expanded build path was restored or claimed live. No helper was
added or moved; the controller uses the existing stage's stairs and gaps.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb3-alts-full11-source-1114 --max-files 1 --timeout 600 -- python -B tools/audit/check_smb3_alts_full11_1114.py --identity toad3
```

Use `--identity peach3` for Peach, or add `--metadata` for strict metadata only.
The output root remains absent: zero generated build files, ROMs or captures.
Protected roster progress and Steve QA remain untouched. Root owns Mesen.
