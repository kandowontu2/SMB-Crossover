# Goku current full-stage qualification

The installed menu-family nightly, SHA-256
`22d09909bf952ef007d1582589dc869073262784bf38b92d2c7b206ce3c45b19`,
passes a controller-only non-shortcut Hard 1-1 run into active 1-2.
The terminal receipt reports 5,837 physical frames, 4,033 gameplay updates,
lives 2 → 2, world 0 / level 1, engine active, player X40/Y48, and minimum
stack pointer 190. Mesen exited normally with status 0. No game-state writes
or cheats were used.

The source-specific controller avoids repeatedly attacking during ascent.
The final correction waits for a grounded takeoff at X1360 or later for
the X1376–1424 pit; the earlier attempt jumped too soon. Goku retains the
existing native vertical helpers at left X688 and X872, initial Y208,
32 pixels wide (centers X704 and X888). No ROM, physics, or helper change
was needed for this qualification.

Producer: `tools/audit/prepare_goku_gap_1102_v4.py`.
Terminal result: `build/goku-gap-1102-v4/native/capture/result.json`.
This does not establish all powerups, Easy mode, the shortcut route, or a
frame-by-frame audiovisual review of the entire game.
