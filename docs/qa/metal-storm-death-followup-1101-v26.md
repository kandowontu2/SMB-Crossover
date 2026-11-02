# Metal Storm death follow-up

Status: unresolved; candidate not delivered.

Candidate SHA-256: `91660ff4182edf8bf0a2498966d959b2c170ba2060192eac49e1c54dfcaf779e`.

The controller-only armor route in `build/metal-storm-natural-armor-1101-v26/native/capture/result.json` failed at 1,600 frames. After contact near world X=280, engine state 11 persists with two lives and no completed death. No mushroom spawned or was collected. The route hit the earlier coin block, so it does not establish a mushroom collision defect or successful collection.

The donor trace in `build/metal-storm-natural-armor-1101-v26/donor-death.json` resumes original frame/NMI execution after a controlled lethal-contact fixture. It shows scene 2, explosion actor type 2 at frame 34, animation progression through frame 79, substate 3 at frame 82, and scene 3 at frame 142. This is source lifecycle evidence, not a native host playthrough.

Host inspection: `player.s` PlayerDeath dispatches expanded guests and returns without NativePlayerDeath fallback. DeathMusicEnded sets GameEngineSubroutine to 6 to enter the ordinary lose-life path. Metal's missing death callbacks therefore cannot rely on Mario's falling-body completion. Implement original death initialization/ticking and its graphics, then explicitly enter the host life-loss path after completion. Verify actual candidate instructions and bank mapping before wiring that handoff.

Next: repair the death lifecycle, verify life loss and respawn in native play, then correct the armor route to the mushroom near world X=336. The Downloads nightly remains unchanged.

V27 source progress: `tools/reference/metal_storm_death_leaves_1101_v27.inc` relocates original bank 0 $966A..$9735 and its 15 data bytes. The assembled code occupies 227 bytes, within the currently remaining 238-byte helper tail, leaving 11 bytes if integrated unchanged. `tools/audit/check_metal_storm_death_leaves_1101_v27.py` passes 210 initializer comparisons across coordinate underflow/wrap cases and all 48 explosion updates against the actual original instructions. The final source phase is 3 with a 60-update wait clock. This is not wired into the candidate yet. The renderer still needs explosion actor type 2; death-start/tick callbacks, the initial freeze, moving-platform coordinate adjustment and final host life-loss handoff remain outstanding. The $9736 table is 5,3,4,3,1 frames per pose, three updates each. The final CHR high byte is $B1, verified directly from the donor (not extrapolated from earlier entries).
