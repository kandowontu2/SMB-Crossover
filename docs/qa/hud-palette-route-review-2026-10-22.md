# Current HUD, palette and Rygar route review

The playable ROM remains the admitted Water CW checkpoint. This review does not install the private HUD candidate or claim the shared palette issue fixed.

## Private HUD successor

The earlier deferred HUD producer was rebased additively onto current CW, preserving Cheats, Sophia head origins, terrain publication, score anchors, cannon cooldown, Water and firebar admission. The pending byte moves to7FFD, after the two Cheats bytes. Its native block-update consumer now treats pending numeric work as busy. Both mapper builds and both literal baselines build successfully.

The original bank5 reservation now contains the installed103-byte Sophia helper. The first CX build therefore overflowed103 bytes and is retained. Private CY relocates the379-byte HUD flush to bank24 BA00-BB7A. Its private partition reserves B700-B9FF for the frozen725-byte Ryu leaf, BA00-BBFF for HUD, BC00-BFBF for additional Ryu code and BFC0-BFFF for scores. This is private only; the main linker/partition is unchanged.

Native consumer tests on both mappers cover126 pending/header combinations and the disabled-pending control. Pending work preserves both replacement flags; without it, the first native slot writes its packet and the second correctly waits on the now-busy queue. The earlier test incorrectly expected both slots to write; that failed DA result is retained. The CZ path-binding failure is retained too. CW's pending-state negative is a counterfactual control, not an installed-CW bug, because CW has no deferred producer.

A second compiled comparison found a real remaining ordering defect in the private algorithm. It executes current native numeric production and the candidate, with foreign writes before or after the same request. There are14 cases per mapper. All before-numeric and unrelated-write controls match. Five after-numeric cases differ on each mapper: partial score, full score, vertical score, mirrored-name-table score and partial coin writes. The candidate appends numeric packets after those later writes, or removes a foreign full-score packet as if it were its own. The busy guard alone cannot make that correct. The original DC harness used the wrong player request nibble; corrected DD uses the actual P1 request02 and retains DC.

The candidate remains uninstalled. The next design must preserve a numeric request's queue position, distinguish its own packets from foreign packets and coalesce only requests superseded by later requests. Full-size marked placeholders filled in place before publication are a candidate design, not a verified implementation. Marker ownership, queue capacity, consumers, direct-call outputs and attained interrupts still need proof.

## Bass's underground brick colors

Current compiled DrawBlock assigns ordinary bouncing bricks sprite palette3. Current guest face setup writes0F/37/17 into that same palette in1-2, replacing native underground0C/3C/1C. This directly explains the brown/orange effect in the retained1:38 film. Debris also selects palette3.

The actual mapped Bass CHR records show28 base-pose palette3 parts with color2 skin pixels and two hurt parts with all three colors; his special poses also use colored palette3 parts. Disabling pure-black outlines does not free those colored parts. Restoring the native palette globally would recolor faces and specials. No such shortcut is installed. Coordinated palette assignment/art packing must preserve both player colors and world effects, then measure any added OAM pressure. This is current code/CHR evidence, not a newly recorded ordinary encounter.

## Current ordinary Rygar route

An old1-2-only guide was initially started without its1-1 prefix and failed immediately. A full retained-movie guide now supplies only ordinary buttons from current telemetry. Actual enemy reactions, fresh B presses at the observed ceiling wall and two separate jumps onto/across the1-2 pipe let the current CW run clear1-1 and1-2. All attempts, including deaths and the overly broad brick-response attempt, are retained.

DM reaches1-2 at frame4027 and1-3 at7574, then dies at8785. DN independently replays the complete8785 controller/trace rows byte for byte, including cycle counts, with full read-only OAM/CHR/audio/scroll capture. Its expected native exit is1 for that1-3 death; it is not a through2-2 success. The shorter4100-frame DK replay independently confirms the first-level prefix and stops at its explicit limit. Neither replay grants powers, positions, ammo, enemies or terrain.

The current DN route has12308 active visible PPUSCROLL writes, all on scanline31, with no late split in the bounded window. This does not certify every frame's appearance or sound and does not close the old movie's late split. No new final A/V recording is delivered by these controller proofs.

The injury observer identifies DM's1-3 collision as a red Koopa, slot1, at1713/88. The landing response DO gets beyond that encounter but later dies over the next tree gap at1875/245. Do not infer a ROM physics bug or blindly extend the enemy-ID filter; the next route work needs actual platform/landing geometry. The complete through2-2 route, every ability/upgrade, other characters and final recordings remain unfinished.

Evidence aggregate: `build/verification/hud-palette-route-review-dp/summary.json`. All captures and negatives are retained under the user-raised100GB cap.
