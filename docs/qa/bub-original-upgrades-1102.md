Bub/Bob original upgrades — private integration, November 2

Downloads remains the verified `9cf99b438e6f5bc614dc4ccc433707a3796702b7f33a04318a428a1155397f15` nightly. No installation or release-asset replacement was made during this pass.

The current private candidate is `build/bub-upgrades-root-candidate-1102-v72/bub-original-upgrades.nes`, SHA-256 `b7e2a161ea2781a8346b126b9c759f7c60f2583e2a18e58f8ca888d041c0bd53`. It is not ready to deliver.

The original Bubble Bobble dispatcher at bank6:9A3A gives item4 mask01 and item2 mask06. The intentional host adaptation maps a mushroom to item4, then a flower to item2, yielding source flags01 then07. These flags affect the actual original routines; they are not native PlayerStatus substitutes. The old delivered pickup path did not grant those source upgrades.

Private implementation and checks:

- Relax243 original conditional macro branches to equivalent relative branches, recovering729 bytes. Verify every encoded target and retain original source/native state parity in1,000 actual paired GameCore updates. Native adapter entry addresses remain fixed; all original moved ingresses are relinked.
- Correct actual pickup row24 (row14 is Side), and admit raw39 through the real native rare-character classifier. The joint38/39 gate has131,072 instruction-level ingress cases;130,048 foreign cases retain exact target andAXYP/SP.
- Invoke the genuine native collector for item erasure, power animation, SFX request, star and1up bookkeeping. A C0 callback return does not automatically collect an item on this owning path.
- Implement missing powerup-update row33. Both actors complete two genuine60-update transformations through PlayerChangeSize/native dispatch, retain source flags01/07, and resume engine8 with native power1/2. Their full1KB source state and coordinates remain frozen during each animation. Genuine pickup SFX is queued; acoustic fidelity is not established.
- Remove a redundant nested JSR in the native callbacks. The retained predecessor actually corrupted live SMC under IRQ nested inside lag-frame audio (minimumSP120). Native tail gateways pass933 focused nested IRQ cuts, minimumSP122; the final pickup body separately passes2,996 IRQ and2,996 genuineFF lag-NMI cuts. Every lag test traces INC NmiSkipped once and rejects the regular NMI branch. Only the actual asynchronous native07DA audio-duration byte is normalized.
- Execute current shared cold/readback/warm authentication. All32 header-byte corruptions reject; code/helper readback faults and WRAM protection fail closed. No new carrier pages or unconditional RAM are allocated.

Actual emulator findings, all retained as negatives:

- Candidate72's old full-stage controller retreats into the second pipe atX647. This is a controller geometry failure, not evidence that source branch relaxation changed movement.
- Controller73 clamps that retreat but rides too late at the third pipe: actual earned restartX721/Y144 hits its side before gaining height.
- Controller75 jumps at a source gap of24 for tall pipes. It crosses those pipes and reaches the final-pit staircase, then fails the actual-foot-support assertion. This historical run did not clear1-1.
- Controller74 naturally defeats the opening Goomba and attempts the first mushroom block. It fails the no-death assertion after repeated bump attempts. It does not prove an earned pickup. Read-only source review identifies a real head bridge mismatch: source ceiling sweep/clamp cancels ascent before the native head probe can hit the block. The helper is implementing a deferred bridge through actual HuHead row10; no such fix is included in candidateb7e2.

No new helper platform has been added. Existing helper inventory remains authoritative in `docs/qa/helper-platform-inventory-1101.md`.

November 3: both identities now clear the complete non-shortcut1-1 in the exactb7e2 candidate. Bub controller78 passes13,540 physical frames/5,243 Main updates/61,613 checks; Bob controller79 passes13,510/5,197/61,036. Each retains two lives, naturally pops17 enemies, earns six original bubble rides, traverses all four pipes/three pits and reaches active1-2 with zero source/hardware failures. Both endpoint images were viewed. Controller78 accepts native state2 during a settled sourceSelector0/zero-Y-speed/aligned-Y phase only with actual solid foot support; actual original jump entries still require native state0 and physical support. These are controller changes only. Exact source/controllers/results and two existing endpoint PNGs are frozen in `docs/qa/checkpoints/2026-11-03/bub-upgrade-full11-v80`.

The block bridge remains separate: helper55's shallow return of the actual recorded tile/row/column/pre-clamp displacement lets unchanged native PlayerBGCollision release a real mushroom in a CPU fixture for each identity, without another native call inside the resident callback. It is not yet qualified or emitted. The deeper54 approach actually corrupted the stack and is retained as a negative.

Next: qualify the real ceiling-to-native-head event and its pending-state lifetime; exercise block emergence and mature collection in Mesen for both identities; test earned upgrades and validate exact Downloads launch context before publishing. Prince and Donkey Kong Jr. remain separate private integrations. The measured authentication-cache proposal remains unqualified and is not in this candidate.

November3 native follow-up: candidate `cf7f157aa39493149b24039c190f09244ce68bc47f0a87f06f01adb47a2c70dd`
passes actual first-mushroom collection for both identities and separate full1-1
runs. The source head projection uses107 recovered bytes; an additional10-byte
initialization leaf clears only native starting tier on cold/new-life creation.
Warm Fresh retains the native tier and original source upgrades, with no added
stack depth. Eighteen paired lifecycle cases and ten IRQ/ten genuine FF NMI
checks at the new instructions pass.

The real menu trace found the missing initialization: browsing SMB2 Mario wrote
native PlayerStatus1, and Bub inherited it while his source upgrade flags were0.
The first block therefore produced a flower. Resetting Bub's own initial tier0
restores the mushroom progression. A separate controller correction aligns both
original source head probes inside the actual question block at336..351; Mario's
old center-probe alignment first contacted the neighboring brick. Earlier runs
remain negatives and were not relabeled.

Bub's earned-mushroom run passes1,911 physical frames/6,701 checks; Bob's
passes1,948/6,666. Both observe the immature then mature item, genuine native
transformation, source flags01 and two lives unchanged. Full1-1 passes13,460
frames for Bub and13,513 for Bob, with17 natural pops and six original bubble
rides each, no helper platforms and active1-2 reached without losing a life.
All four endpoint images were viewed. Compact exact inputs/results are in
`docs/qa/checkpoints/2026-11-03/bub-earned-native-v90`.

This candidate remains private. Parent head tests pass3,570 IRQ and3,570 genuine
FF lag-NMI cuts; an unconditional foreground audit finds no I1 instructions in
these actual episodes. Expanded post-head/nested IRQ work includes deeper
rendering with the newly queued sounds and an exact pending mapper-write
boundary; it is not yet a complete pass. Plain-brick audio, earned flower,
final cold/lifecycle binding and actual Downloads launch remain required.
