# Bub/Bob nightly delivery — November 2

Installed directly, without a backup, at `C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes`.

- ROM SHA256: `613b3300b09e530ec920835b95df53f3115d865ed854e273809d4cafa52407ce`.
- Sole Latest release asset: `SMB-Crossover-Latest-WIP-MMC5.ips`, tag `Current`.
- IPS SHA256: `69446d424d8c3b21592d76a605d17ea2c8fe5804b1c1fecca074e2e098a8488b`.
- Clean SMB World base SHA256: `0b3d9e1f01ed1668205bab34d6c82b0e281456e137352e4f36a9b2cfa3b66dea`.
- IPS reconstruction matches the installed ROM. Before/after patch guards pass with no same-name automatic patches. GitHub Latest API confirms this one asset and digest.

Actual Downloads Bub cold selection, idle, walking, jumping and bubble controls pass. Candidate native tests also pass Bub/Bob cold selection, controls and bubble rides, plus Bub trap/pop, Easy stomp and ceiling contact. The additional Downloads Bob run exceeded its host runtime bound during a connection interruption; it is not a passing replay.

This is a playable WIP, not complete roster qualification. Full 1-1 and all-powerup tests remain open. Idle/walk are roughly half rate. The unchanged-ROM `native-event-bub-full11-close20` run terminated with `Actual original route bubble did not launch`; its receipt records successful crossings of the first two pipes, and the negative capture is retained for diagnosis. No helper platforms were added for Bub/Bob.

Live delivery receipt: `build/bub-delivery-1102-v9/published-receipt.json`. Source event checkpoint: `docs/qa/checkpoints/2026-11-02/bubble-native-event-v9`. Earlier native checkpoint: `docs/qa/checkpoints/2026-11-02/bub-native-v9`; its manifest defines its narrower coverage.
