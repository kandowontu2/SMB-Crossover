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
