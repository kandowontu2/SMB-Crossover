# Mini Mario performance and fireball verification

## Tested candidate

The combined candidate is `build/mini-two-fireballs-1103/mini-empty-draw.nes`.
Its SHA-256 is `244734bbc2690b4e97e654cc72f8f153bedbe3fcc799f714e9508784e4f33af4`.
The performance work began from Downloads hash `4ff069b3474077a1f3f8924b530780dee7a81c2a32d759f8fbe2defcf91e3f4c`.

## Changes

- Mini uses a specialized renderer that retains the native enemy, platform, block-debris and score drawing loop. Native OAM records match the previous implementation with zero, one, three and five seeded Goombas.
- A guarded background path handles clear space and ordinary supported ground. Coins, blocks with pending head events, pipes requiring native handling and other interactions retain the native routine. The guard matches 120 homogeneous and 192 mixed head/floor fixtures.
- The initialized Mini movement service reaches its existing code through a shorter native transport. Both RAM owner markers and the source initialization state must be valid. Cold contexts retain full authentication. The comparison includes frame-counter wrapping, foreign callers, 278 NMI and 139 IRQ seams.
- The tile query retains its exact inputs and outputs while using a compact encoded attribute table. All 221,952 comparison cases pass. Its second attribute consumer retains the original low two bits.
- Fire Mini Mario supports two active native fireballs, fresh-B admission, left/right firing and an Up-directed launch. A third shot is blocked while both slots are occupied. Each visible projectile is exactly four by four opaque pixels. Both use existing native collision control 8 and the SMB fireball movement, bounce, impact and enemy routines. This is a native-physics adaptation.
- Fresh initialization and loss of the fire tier clear both slots. Unpowered empty weapon updates retain the inexpensive return.
- A two-byte Chip HUD factor preserves all 71,888 queue comparison cases. This funds the two-slot predicate without expanding the allocated ROM spans.
- The initial one-shot build `f552fd7b` incorrectly reused reachable Roll padding. This successor jumps over the reused bytes and retains Roll's continuation. Actual whole weapon calls match the safe baseline with zero, one and three bullets. A controller-only cold Roll launch completes 120 weapon calls and returns, with free buster shots and unchanged health and energy.

## Mesen results

The empty-area replay has 180 idle updates in 180 video frames. Both walking directions, braking, jumping and landing also have one update per video frame. Each of these phases has zero skipped NMIs and zero frames without a controller poll. Mesen's built-in cumulative lag counter is unavailable through this Lua state API, so the receipt records the actual NMI and controller-read measurements.

The controller-only non-shortcut 1-1 replay passes all four pipes and all three gaps, retains both starting lives, finishes the flagpole sequence and enters active 1-2. Its active-stage measurement is 2,703 updates in 3,182 video frames, including 1,157 frames without a controller poll. Busy-stage lag remains unresolved. Whole-stage zero-lag acceptance has not been reached.

The controller-only earned mushroom replay passes the actual block release, emergence, maturity, collection and completed native power transition. The fireball replay uses an explicit powered fixture after a real cold-menu launch. It verifies two simultaneous launches in both directions and Up, held-B behavior, third-shot rejection, native bounce events, clipping, mapped CHR pixels, native palette and separate OAM DMA records alongside Mini. Its 60 powered idle updates have zero lag. Some dual-shot action phases still lag. This fixture does not establish natural flower collection or an enemy kill in Mesen. A separate actual compiled CPU scene verifies native Goomba defeat, explosion, hit sound and the 100-point event.

The three fireball screenshots and the 1-2 endpoint were visually inspected. No video or image sequence was created. No helper platform was added or moved.

## Evidence

- `build/mini-two-final-idle-1103/capture/timing.json`
- `build/mini-two-final-full11-1103/capture/result.json` and `timing.json`
- `build/mini-two-final-power-1103/capture/result.json`
- `build/mini-two-fireballs-native-observer-1103/capture/result.json`
- `build/mini-two-final-cpu-1103/result.json`
- `build/mini-two-fireballs-1103/source-funding.json`, `pool-proof/result.json`, `enemy-proof/result.json` and `roll-proof/result.json`
- `build/mini-two-roll-native-1103/capture/result.json`
- `build/mini-direct-native-1103/CPU.json` and `boundaries.json`
- `build/mini-tile-fast-1103-v1/source-stage.json`
- `build/mini-noop-chains-1103-v1/audit.json`

The exact installed Downloads launch and IPS reconstruction pass. Their receipt is `build/mini-two-delivery-1103/verified-delivery.json`. Reopen the ROM and start a fresh game for this code update.

## Next performance work

Continue with the measured busy-stage costs around scrolling terrain, native collision fallback and multiple enemies. The highest recorded calls include the jump near world X 1513 and the four-enemy area near world X 2031. Preserve the world firebar/lift scan and empty-path shared-state writes. The no-op audit did not qualify a further shortcut saving 500 cycles per update.
