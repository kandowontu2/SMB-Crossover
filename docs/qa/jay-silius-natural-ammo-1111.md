# Jay's first natural ammo pickup

The CPU replay passed on the installed Downloads ROM
`4df817587ea5b0aff3f278a4201976745bad4d9dd1b2a99d6cb5fd3b9c74dadc`.
It selects the spread weapon with the native pause menu, uses the first
Goomba spawned by the unmodified level parser, and uses controller input
for the shot and collection. The worker and its redirect are verified in
authenticated RAM before the replay starts.

1. Start World 1-1 as Jay. Once the weapon state initializes, press Start
   to pause, release it, and tap Select for weapon 2. Wait for the pause
   timer and Start latch to clear, then press Start to resume. The replay
   starts walking with player world X40/Y176, camera X0, ammo 63, and
   `FrameCounter` 170. These values provide an alignment point for Mesen.
2. Hold Right until player world X reaches 215, then release Right.
   Wait for the first live Goomba's world center X to reach 272. The
   center is `256 * Enemy_PageLoc + Enemy_X_Position + 8`. In the CPU
   replay, Jay is at X216/Y176, the camera is at X104, and
   `FrameCounter` is 168 at this point.
3. Give four more idle Main updates. At `FrameCounter` 172 and Goomba
   center X270, tap B for one update and release it. Ammo drops from 63
   to 61. The center round at X253/Y191 defeats the Goomba at center X268
   four updates after B. `FrameCounter` 177 produces roll `$D8` and the
   pending item `$23`. The score popup and native defeated state appear.
4. Stay idle until the item lands. It becomes active (`$22`) 24 Main
   updates after defeat and lands at X268/Y200 on update 49 after defeat.
   Hold Right for 27 updates. Jay reaches X252/Y176, consumes the item,
   and restores ammo from 61 to 63. The pickup requests sound `$18` and
   both lives survive.

The Mesen trace can read `DropStage` at `$C0D7`, `DropTimer` at `$C0D8`,
and `WeaponAmmo` at `$C0BE` while Jay's private C2 RAM is mapped. The
natural pickup route was verified in the CPU model. The Mesen stage
clear has its own receipt.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/jay-silius-natural-ammo-1111 --max-files 1 --timeout 600 -- python -B tools/audit/check_jay_silius_natural_ammo_1111.py
```

Checker SHA-256
`84e4912268b02ab2de4dc1ed7a5ad37608919c03c6c49656748498e652ddfc89`.
The bounded replay generated no files.
