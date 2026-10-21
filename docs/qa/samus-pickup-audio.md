# Samus pickup audio

Samus's mushroom, flower and star pickup cue was queued by the real collision handler, then lost. `GuestAudioBegin` excluded `Sfx_PowerUpGrab` from the shared effect queues, and the native Metroid adapter had no handler for it before clearing the remaining requests. Extra-life requests had the same gap.

The Samus path now captures pickup and extra-life requests for the shared mixer. MMC3 borrows the second native pulse voice for the effect and restores its music registers afterward. MMC5 plays it on the second expansion pulse while both native pulse music voices remain available. Metroid's own beam/effect handling continues through its buffered native driver.

This follows the pinned hosted source: `Character.hitPickup` plays `SFX_GAME_POWER_UP` for mushrooms, flowers and stars. Samus inherits that behavior. It does not substitute Metroid's longer item fanfare for the website's shared pickup cue.

The new `tests/samus-pickup-sfx.lua` failed on the pre-fix ROM at the first mushroom. It places real items into the native collision path and covers the mushroom, flower, repeated flower at full power, star and green mushroom. Checks observe the physical APU/MMC5 registers, enabled channels, audible volume and changing pitches, the sound during the upgrade freeze, isolation/restoration of native music, and the awarded extra-life fanfare. Native Metroid stores must remain buffered. The fixture explicitly places items through emulator RAM; it is not a controller-only level-clear replay.

Both mappers pass the new regression. Existing Samus upgrade, beam, world-SFX, controls and water checks, plus the other original guests' world-SFX/audio checks, are recorded in [the focused test summary](../../build/verification/samus-pickup-summary.json). Exact ROM hashes and individual logs accompany it. The previous full-suite summary refers to its earlier ROM checkpoint.

```powershell
python tools/run_mesen.py tests/samus-pickup-sfx.lua build/smb-crossover-mmc3.nes
python tools/run_mesen.py tests/samus-pickup-sfx.lua build/smb-crossover-mmc5.nes
```
