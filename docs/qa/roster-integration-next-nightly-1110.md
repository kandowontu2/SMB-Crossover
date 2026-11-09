# Next roster nightly

The installed ROM is now `94650fbc11ede25b9d08e579bdc6b1d6da81fca8f29c6b0c25dadad2e685ede1`. Actual Downloads Giant and Mini replays passed. The sole Current IPS is `621ac2b2de662dd9029e310a2e22a05e00092194b024cde4b327988310fc2948`, reconstructed byte-identically and published as Latest. Evidence: `build/mega-giant-delivery-1110/verified-delivery.json`.

## Mega Giant Mario

Candidate `94650fbc11ede25b9d08e579bdc6b1d6da81fca8f29c6b0c25dadad2e685ede1` cleared 1-1 into active 1-2 with both lives in `build/mega-giant-current-native-1110/native-end/capture/result.json`. This is a controller-only clear, not an all-powerup audit. The run recorded 1,106 missed controller reads; performance is unfinished.

Root accepts the exact finite CHR allocation documented in `build/mega-giant-chr-lease-1110/proof.json` (SHA-256 `ee31c25a0183cc18abd3af62a426cec78b0170daaf024c6b4034c5ff5ade989a`). All bound files were checked unchanged. The 24 changed even pages from 168 through 214 have no foreign claim in the audited source domains or observed menu writes. This does not establish all-scene gameplay correctness.

Delivery checks passed: candidate Mini and actual Downloads Giant/Mini replay, IPS reconstruction and sole Current asset replacement. Mini retained its exact 3,494-update cadence without active missed reads and boarded all three original helpers. Giant's launcher supports an explicit expected digest and existing external symbols without creating Downloads sidecars.

## Requested manual platform assistance

Mini Mario and Karnov must gain an Up + Select ability to spawn one small vertical native platform directly beneath the current player. Repeating the combination replaces the previous manually spawned platform. Select alone must not trigger it; holding the combination must not repeatedly recreate it. This is an assistance tier for ordinary gameplay, not a restriction to stage 1-2. This feature is not yet in the installed ROM. Preserve authored helper platforms and unrelated native actors.

## Prince of Persia

The primary terrain context repair now has space inside the existing allocation. Sharing two identical pose records recovers 29 bytes at `$D672..$D68E`; the decoder remains at `$D68F`. All 239 decoded records and 408 native poses remain equivalent.

`build/prince-d6c0-align-1110/funded.json` (SHA-256 `d66ccbcfaa6fd51efffce7705b5d60304be2b3a7aa3c237e26405d01c6355058`) qualifies memory-only candidate `529e51490f610f690ad16c84a868615820cf4e438154127925e15feb5fd7bff1`. Five alignment controls and 324 IRQ plus 324 forced-blank NMI checks pass. Existing wall-height behavior is intentional in `prince_host_world_1102_v8.s`; this repair targets horizontal context, not that policy. Native replay is still required.

## Getsu Fuma

Sword admission and three empty-service bypasses are separately qualified in `build/getsu-sword-idle-1110/proof.json` and `build/getsu-empty-services-1110/proof.json`. The latter saves 3,510 cycles per sampled idle/walking update; the former saves 319 per idle update. These are CPU measurements, not a native frame-rate claim. Rebase onto the public shared-side optimization and native replay remain required.

## Storage

Removed 52 byte-identical old emulator process inventories, retaining one exact copy of every digest. The mapping is in `cleanup-duplicate-session-inventory-1110.json`. Gameplay receipts, source and unique captures were retained. After cleanup, build storage was approximately 3.05 GB and 19,894 files.
