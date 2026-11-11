# Donkey Kong Jr. late stock platform admission

The existing allocator now admits thirteen stock actors in World 1-1. It
adds four vertical girders after the eight opening girders and the horizontal
second-gap platform. Each new row uses the native `$25` constructor and
bound-box profile 5. The late rows use the same offscreen admission margin
and wait for a free native actor slot.

| World 1-1 placement | World left X | Center X | Initial top Y | Oscillator center Y |
|---|---:|---:|---:|---:|
| Pipe X2608 ascent | 2576 | 2592 | 192 | 177 |
| Pipe X2608 descent | 2640 | 2656 | 192 | 128 |
| Pipe X2864 ascent | 2832 | 2848 | 192 | 177 |
| Final stair descent | 3040 | 3056 | 192 | 128 |

The CPU suite passed 46,080 allocator cases, 12,800 paired old/new schedule
checks, 24 foreign room or high-camera cases, 180 real actor-pool birth and
retry cases, and 3,240 paired refresh checks. Both source images passed
complete cold readback. Four separate parser-backed native Main runs
admitted the new girders at camera-left X2289, X2353, X2545, and X2753.
Thirty-two lag-NMI and 32 IRQ cuts resumed the exact ordinary Main state.

The late DK Jr. source changes 280 bytes and composes with all 49 Sonic
snapshot changes. The combined image also repeated the CPU second-gap
landing and far-bank crossing with both lives. The translated late obstacle
and flagpole replays are documented separately. [Late terrain and route](dkjr-late-terrain-1110.md)

On the combined candidate, a continuous Mesen replay from the title screen
crossed the third gap at X2482/Y112 and both late pipes. It reached the
connected final staircase at X2909/Y144 with two lives. All four new stock
actors spawned 287 pixels offscreen and entered view at a relative X of 255.
The first three late girders supported the pipe crossings. The final
descent girder reached the visible screen, and its rider crossing still
needs a continuous replay. The run ended at the final stairs at Main 9623.

An earlier takeoff at the second riser reached X2144 with a different camera
and horizontal phase and repeatedly clipped the jump at Y158. The retained
controller uses the longer verified approach through all three gaps. A
shorter route needs to preserve the launch phase as well as the world
coordinates. The final-stair revision records the native HUD timer and
tries explicit takeoff positions for each riser.

- DK Jr. CPU candidate SHA-256 `f837a0259b069392003a8dbd1a71571f86189a309c92a6c68b468e8794321dab`
- Combined candidate SHA-256 `e295500856ed5a9bfc718699d52bc5b36ecdc2717bed31cf275d87c1af25bf09`
- DK Jr. cold owner cookie `a7280130b1118ac41a70e81c2eda030f`
- Stock vertical birth hook RAM3 `$BD41` and stock constructor return hook RAM2 `$D1F0`
- Continuous Mesen partial receipt `7da1995d1181f612449cb2e133fb190df48f86bd858f9fa0a537343659cb1771`
