# Worker interruption handoff

All three active subagents terminated with a usage-limit error. They are stopped, not running in the background. The overall goal remains incomplete and has not been marked complete or paused.

Root verified these files after the workers stopped:

- Downloads nightly remains `58e50db6ceead7c3706087c92d6e49014f05ff8b80b000be30c27b4e7dfa11f2`.
- Tank private candidate: `build/mario-tank-visible-host-1101-v5/candidate.nes`, SHA256 `616bc1855b7cd5320a57ebd8fe0a053ea287e646921be179f1ed2f8dd2d83293`. This is still based on367, not the current58 nightly. Pickup slot correction has been made. New `art-tail-readers.json` covers banks13/73/12/68; review its implementation, bindings, mixed code/table boundaries and caller domains before granting. `music-tail-readers.json` covers full-roster mask streams in115; Mike's adjacent native music pointer domain still needs closure. Five final ROM grants remain. Conditional RAM and the other13 ROM regions are granted.
- Metal Storm private candidate: `build/metal-storm-native-integration-1101-v12/candidate.nes`, SHA256 `83c9990061715416f8773555e11692747e2ba2a95411caa666c4326966f11150`. Native actor tests pass on a composition preserving current58 patches. Scene/menu integration was being prepared in existing fragment slack; inspect untracked source before assuming that plan was compiled. No native emulator or playable admission claim.
- Shinobi: `build/shinobi-owning-graft-1101-v1/review-checkpoint.json` reports a frozen review packet `source-and-proof.zip`,101849 bytes, SHA256 `05ccb014058d56d76bb8916e4b41645860a87353ae0b974f93b25c783fdca483`. Measured code6811, metadata1696, art3072. Host integration remains false. Original injury/death poses need11 additional8x16 pairs; a proposed compact metadata/art partition has not been implemented. Preserve this frozen checkpoint before extending it.

Karnov controller tests crossed the first pit but died in the following enemy group. No Mesen test remains running. Next route should test crouch-fire: standing shots visibly passed above Goombas. See `karnov-pit-route-progress.md`.

Do not treat the allocation checks or component receipts as full-stage or all-powerup completion. Preserve the user's preexisting modification to `docs/qa/current-roster-progress-2026-10-27.json`. Keep all storage limits and direct nightly replacement policy in AGENTS.md.
