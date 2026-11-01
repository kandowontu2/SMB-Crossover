# Current Downloads launch verification

Tested `C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes`
directly with Mesen, SHA-256
`367266d2ec4e62fcefc15fffb3a05095a16060ad52f9d68348f213d94b31268c`.
The patch guard found no matching IPS/BPS/UPS.

Controller-only cold start: Start, Left to Rygar, Select to Karnov, Start.
After 510 frames, selected character was 34, game mode 1, task 3, menu 0.
Mesen exited successfully. The root visually inspected the gameplay PNG:
Karnov was present in 1-1 with his HUD and no obvious screen corruption.
This verifies selection and gameplay entry, not completion of 1-1.

Evidence: `build/karnov-downloads-current-1101-v2/probe/capture/result.json`,
`binding.json`, `karnov-selected.png`, and `karnov-start-result.png`.
Two PNGs total 7,934 bytes; no video or frame sequence was created.
The other project's Mesen process 254176 was left untouched.
