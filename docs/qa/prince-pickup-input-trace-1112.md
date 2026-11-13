# Prince first pickup: input diagnostic

Current Downloads ROM: `464c8f1af0401ba7d5393e331833af5bdd68882c536dfc3c77534b71508213c0`.
Controller-only Mesen, no state injection or captures. The bounded runner reused
`build/prince-first-pickup-1112/controller.lua` (one file).

The approach evades the first Goomba, runs to X400, turns left and settles at
X333/Y176 with HP5 and two lives. Up and A are distinct original actions:

- Up enters action14, poses67 onward. Native Y stays near176 instead of rising.
  Receipt `4d63a6d80c055bc07500ab28c9d29292a7602afa77135389d84187a3dc402c67`.
- A enters action3, poses16 onward, moves left to the camera boundary X305,
  and returns to action0. Sampled Y reaches174, not the block overhead.
  Receipt `d05acc71d7dbade1f856cf22c98ba9db839e5bcfcdaf1f6e4004df53a7603fc7`;
  script `f298396036f78e044189f43323e681c7498dfbe9e823f48987565917e0e71be7`.

Neither attempt spawns the item. Global minimum Y161 belongs to the earlier
Goomba evade and must not be described as the standing jump apex. The diagnostic
exits1 intentionally when no item spawns; this is not a passing pickup test.

Next: inspect the source coordinate/terrain bridge during original jump pose
updates, including camera-boundary clipping. Establish whether this is a native
vertical publication error, source terrain response, or incorrect approach
before changing gameplay. These results do not prove a missing block-bump call.
Prince's earlier full1-1 clear remains separate evidence. No ROM changes made.

## Source-coordinate follow-up

Physical write callbacks narrow the A-button case: C611 receives only two writes
during the entire attempt, 128→122 at PC $A251 (phase145/pose24), then122→128
at PC $A25C (phase149/pose25). Origin stays77/high0 throughout. Thus the trace
does not show a large source jump being erased by a repeated host Y write.
Investigate original action3 pose commands/projection before changing floor
clamping. The current callback watches CPU C611 only when mapped to RAM2;
it is not proof against writes through another alias.

Receipt `3a967dcf6a500b533749476677db82b0cbb756f367d6cc4dd2293a420894d4d3`;
script `051560564983fb76f52fb3820710b37d0eb84f2559c81937310211c07b73ebbf`.
All100 update samples are retained in the in-memory receipt; stdout displays
only changes in source Y, origin, projection delta or action. No captures added.

## Original ROM comparison resolves the shallow-hop question

`check_prince_original_jump_commands_1112.py` executes actual original ROM
SetAction and AdvanceActor instructions, using the retained original RAM seed.
The ROM is SHA-pinned by the existing donor oracle. Bounded execution passed:
standing action3 has Y128 except pose25/Y122, then returns128 at pose26.
Running action4 reaches114. Action14 animation commands alone leave Y128.
This exactly explains the observed standing-hop source writes; do not increase
its height as a supposed porting fix. Action14 also needs its terrain/climb
context assessed separately. This check does not execute terrain or projection.

Initial checker attempts omitted the actor-slot register at AdvanceActor entry;
those failed the execution bound and were harness failures, not game failures.
The corrected call explicitly supplies X0, matching the original slot0 ABI.
No output files were generated. Next investigate reachable block interaction
with intended climb/reach controls rather than retuning authentic action3.
