# SMB1 Toad, Peach and Kamikaze full-stage controls — November14

Exact input: delivered421379021e775e6e03357c0aa11d4cab04008452f94bc9e8938f0662cc0c979f.
This is a controller/source qualification task. No ROM, helper, geometry,
physics, installation, patch asset or release change is proposed.

Actual compiled slot0 Select census, not assumed variant numbering:

| Identity | Select presses from Mario | SelectedCharacter | MarioVariant |
|---|---:|---:|---:|
| SMB1 Toad |2|0|5|
| SMB1 Peach |3|0|6|
| Kamikaze Mario |5|0|3|

The separate factories are `replay_smb1_toad_full11_1114`,
`replay_smb1_peach_full11_1114` and `replay_kamikaze_mario_full11_1114`.
Each exposes `controller(raw)` and `metadata(raw)`; each rejects every ROM
except exact421. Shared implementation: `replay_smb1_alts_full11_1114.py`,
readonly Lua `smb1_alts_full11_1114.lua`, source runner
`check_smb1_alts_full11_1114.py`.

The source fixture uses compiled Select, actual Start, native continue/parser,
constructor, GameLoop and NMI. It starts in the established native menu arena;
the bus does not emulate real frontend vblank. The native controllers instead
operate the title and roster through ordinary inputs. Root owns native proof.
No actor, terrain, health, position, ability, difficulty or cheat-state seed is
used to qualify gameplay. The source fixture's menu arena is explicit.

All176 current hidden/cheat changes are retained by strict typed421 inverse
qualification. Full PRG banks containing native physics1 and Main/collision126
are byte-exact to12397. Selector66, dispatch124, Kamikaze skin81 and resident
graphics127 are also byte-exact. No inference from old expanded build paths.

The navigation inlines the unchanged retained Mario navigation/policy and
near-stair controller sources (d51c479d, feca813d, b1509468); new final-stair
inputs are separate. Native observation authenticates mapped entry/caller-return
bytes, reads stacked return PC/SP on each Main entry, and counts only a matching
returned Main. The25 grounded1-2 samples are taken at completed Main returns,
with entry/return counts separate. A flag entry, ordinary castle walk and next
entrance setup are required; no shortcut can pass this observer.

Retained input negatives, all source CPU evidence on exact421, never ROM bugs:

- `2415799254b11fbbdcebdd55fe2fad2c3d405d980b2ed04b29cf5e3ef04834ed`
  Toad with unchanged short-runup Mario stair policy lost a natural life at
  source1665, maxX2450, terminalX2441/lives1. Preceding terrain was crossed;
  full stage was not. No native run of this controller.
- `ab6057a62f8436b42dca8c1feda926c20333914703db9cd1746a7cda59093379`
  tried a longer runway but waited at the actualX2402/Y128 step forY<=112.
  It was still stalled through5500 source updates; its owned process was stopped.
  It was never a full pass or a native run. The companion Peach52cd and
  Kamikaze1cd1 texts were held, not natively tested.
- `7ad7ce9c2f8f2f7efa4b87f9c6971c97fa590c461ac0e1ff85f7c948b6275613`
  Toad used a fresh-A mount, but braking only afterX2438 stopped atX2450 over
  the gap. Natural life loss at1665, equal1665 Main entries/returns. The retained
  trace exposes signed4.4 velocity24 and PlayerSize1; no synthetic game seed.
- `d1cf50115348d1f12cb45ff4160f4638707f4ac180e0feed7884327c31df85fe`
  added predictive braking but still began its mount only at groundedX>=2396.
  Toad's actual prior ground contact was earlier, so this condition missed it
  and retained the same1665 life-loss route. Superseded by a Toad-only controller
  that owns the complete existing stair approach; no state or terrain edit.

Source full-route passes (source scheduler units, not physical frames):

| Identity | Exact readonly Lua SHA256 | Matching Main entries/returns | Flag/castle/entrance Main | Endpoint |
|---|---|---:|---|---|
| Toad | `294bc876f63bfed77bc0b8fa087036b7b5a01906e99ead2f909e81f20a68ef3c` |2974/2974|1737/1800/2377|25 completed grounded1-2 updates, X40/Y176, engine8, lives2, power0, Star0|
| Peach | `7057409ee03b52b0cd58394164e715521279772884ebae5488a47522b5124744` |2953/2953|1722/1785/2356|25 completed grounded1-2 updates, X40/Y176, engine8, lives2, power0, Star0|
| Kamikaze Mario | `254b0217f91fd95eb79119eada152108d2c9f41c0529cb9586ef7f452e1cc0ff` |2886/2886|1651/1713/2293|Same25-update endpoint; skin mode132 retained|

Canonical sorted-JSON source receipt SHA256 (full receipts emitted to stdout,
no receipt files): Toad `a45971b80df9489be342cb99babd5faf313f033d21c44d993f356b4837d98a2e`,
Peach `40dab0852cebaff81eb03469aa024a8afb31fffdfdb48efdd6d7891f4be2cd00`,
Kamikaze `0b2f61083f2bf12e17f8822fa547a05151e55c50f0826e37e8378eeae63968d4`.

Peach and Kamikaze use exactly the same retained navigation sources and the
frozen shared observer. Their Lua texts are unchanged by Toad's separate
`smb1_toad_stair_controls_1114.lua` injection. These passes do not claim natural
M/F/S/L acquisition; the item gates in the expanded-roster checklist remain.
Strict metadata rejects truncated, physics-corrupt, fa66 and12397 inputs,
forbids file outputs/Mesen and forbids rereading mutable Downloads after the
initial input load. Both physical native routes are assigned to root.

Toad's actual ordinary-input stair mount owns the approach fromX2360, uses
fresh A on the existing steps, brakes using observed signed velocity to land
on the actual upper cap, releases A and jumps across. The unchanged retained
Mario route resumes beyond the existing gap. The final Toad source job82055
passed from compiled menu through the full endpoint; source jobs87259 passed
Peach and Kamikaze. No earlier failed input is relabeled as a pass.

Native receipts will be appended after root's completion.
All runs use `python -B tools/audit/run_bounded_build_v1.py --output
build/smb1-alts-route-source-1114 --max-files 1 --timeout 600 -- python -B ...`.
The named output root remains absent: zero generated build files, ROM writes,
captures or Mesen processes. Protected roster progress and Steve QA are untouched.

Repeat a source route with, for example:

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb1-alts-route-source-1114 --max-files 1 --timeout 600 -- python -B tools/audit/check_smb1_alts_full11_1114.py --identity toad
```

Use `--identity peach` or `--identity kamikaze` for the other independent routes,
or add `--metadata` for strict pin/UI/physics/read-only checks without gameplay.
The output root must remain absent; these tools intentionally write zero files.
