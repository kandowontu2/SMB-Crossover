# DK Jr. late 1-1 terrain

The CPU fixtures use exact 3d327d47, the native 1-1 area parser and frame
loop, and DK Jr.'s original controller. Translated ingress positions isolate
each section. The late girders use actual stock `InitEnemyObject` calls in
free slots. These placements still need production admission and a continuous
emulator replay.

## Unassisted stairs and third gap

Hold Right. Use Right+A for eight updates at each listed supported X/Y, then
release A. On the risers, original source state 1 and native state 0 must
agree at the preceding floor height. The later risers use the native side
stop, 16 pixels left of the next step. A trigger 14 pixels left never fires
at the second riser because native wall collision stops the player first.

| Section | Right+A launch anchors X/Y | Terminal X/Y |
|---|---|---|
| First stair pair and trench | 2130/176, 2144/160, 2160/144, 2176/128, 2198/112 | 2305/176 |
| Third-gap approach, gap and far stairs | 2354/176, 2368/160, 2384/144, 2400/128, 2438/112 | 2545/176 |
| Final staircase from the last pipe roof | 2912/144, 2928/128, 2944/112, 2960/96, 2976/80, 2992/64 | 3026/48 |

At the third gap, X2448 and X2464 are empty parser columns between equal
Y144 stair tops. Right+A from X2438/Y112 runs original landing at X2465,
acquires native ground at X2468 and reaches X2480/Y112 with both lives at
update 70. Right alone from the same ingress reaches original defeat at
X2449/Y202. The full stair policies above also retain both lives.

## Late stock girder placements

The two remaining pipe tops are at X2608 and X2864, both Y176. The ordinary
approach jump reaches only Y160 at either lip, short of the Y144 standing
anchor. The first pipe's bare roof exit also kills via the original 32-pixel
fall. The second pipe roof connects at the same height to the final stair
route. The final stair's exposed drop from Y80 to Y208 kills with Right alone
and with Right+A.

| Stage 1-1 placement, stock ID `$25` box 5 | Left X | Center X | Initial top Y | Oscillator center Y | Offscreen camera-left window |
|---|---:|---:|---:|---:|---|
| Pipe X2608 ascent | 2576 | 2592 | 192 | 177 | 2289–2320 |
| Pipe X2608 descent | 2640 | 2656 | 192 | 128 | 2353–2384 |
| Pipe X2864 ascent | 2832 | 2848 | 192 | 177 | 2545–2576 |
| Final stair descent | 3040 | 3056 | 192 | 128 | 2753–2784 |

The X2608 pair reaches roof X2612/Y144, boards the descent at X2638 with
top Y193, and departs at X2667 with top Y194. The real native Goomba stomp
then invokes DK Jr.'s bounce at X2674/Y169. The original bounce lands at
X2704/Y176 with two lives. The X2864 ascent alone reaches X2912/Y144.
The final girder boards from X3038/Y45 at top Y77, departs at X3067/Y162
at top Y194, and reaches X3076/Y176 with two lives.

From the translated X3076/Y176 ground entry, hold Right to the flagpole base
and use Right+A at X3152/Y176. The CPU replay enters native flagpole engine
4 at X3161/Y160, clears the castle at X3266/Y176 and enters active underground
1-2 at X40/Y48 with both lives on update 1243. This is a separate terminal
section.

The smallest placement change qualified here is four more instances of the
existing native vertical helper. Keep the loaded-room scope and stock slot
retry. Exact 256–287 pixel margins for the two X-low `$10` rows span camera
pages, so the actor page must come from the placement rather than a fixed
camera-page increment. The final fixture preserves the native flagpole and
castle flag actors in their existing slots. The production admission and
its byte budget remain open.

The source checks retain zero build files. Use `--section local`, `--section
stairs`, `--section pipe-helpers`, or `--section exit` for a narrower replay.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B tools/audit/run_bounded_build_v1.py --output build/dkjr-third-gap-1110 --max-files 1 --timeout 600 -- python -B tools/audit/check_dkjr_late_terrain_1110.py
```
