# Metal Storm death follow-up

Status: unresolved; candidate not delivered.

Candidate SHA-256: `91660ff4182edf8bf0a2498966d959b2c170ba2060192eac49e1c54dfcaf779e`.

The controller-only armor route in `build/metal-storm-natural-armor-1101-v26/native/capture/result.json` failed at 1,600 frames. After contact near world X=280, engine state 11 persists with two lives and no completed death. No mushroom spawned or was collected. The route hit the earlier coin block, so it does not establish a mushroom collision defect or successful collection.

The donor trace in `build/metal-storm-natural-armor-1101-v26/donor-death.json` resumes original frame/NMI execution after a controlled lethal-contact fixture. It shows scene 2, explosion actor type 2 at frame 34, animation progression through frame 79, substate 3 at frame 82, and scene 3 at frame 142. This is source lifecycle evidence, not a native host playthrough.

Host inspection: `player.s` PlayerDeath dispatches expanded guests and returns without NativePlayerDeath fallback. DeathMusicEnded sets GameEngineSubroutine to 6 to enter the ordinary lose-life path. Metal's missing death callbacks therefore cannot rely on Mario's falling-body completion. Implement original death initialization/ticking and its graphics, then explicitly enter the host life-loss path after completion. Verify actual candidate instructions and bank mapping before wiring that handoff.

Next: repair the death lifecycle, verify life loss and respawn in native play, then correct the armor route to the mushroom near world X=336. The Downloads nightly remains unchanged.
