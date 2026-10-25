# Little Mac NU clears

Both modes now have cold-menu controller discoveries and independent fixed
replays on frozen NU, ROM
`b90ede8fa3afaceefe3ef3090424f4d6b6662c139a1a3d6df52e64b7ec00b240`.
Easy passes 4,933 frames; Hard passes 4,023. Each has zero deaths and 25 frames
of actual movement after entering underground 1-2. Complete input and trace
bytes match within each discovery/replay pair.

The missing Easy clear was a controller-policy problem. The generic policy
jumped about 32 pixels before the second pit; Mac landed in the gap. A Mac-only
8-pixel support lookahead produces a later ordinary jump and a natural landing.
No game code, collision, terrain, equipment, health or physics was changed.
The unsuccessful baseline remains retained with the successful full captures.

Root independently verified all 9,547 retained evidence files and the bound ROM,
source, input and trace hashes. Actual CHR ownership checks pass in both modes;
53 Easy and 49 Hard route samples were inspected, with no obvious corruption.
The root also inspected the native overview sheets and Easy pit comparison.
All 8,556 full replay PNGs are retained outside the capped workspace.

Evidence: `build/verification/mac-easy-nv/manifest.json`, `hard-manifest.json`,
`root-review.json` and `root-hard-review.json`. These are NU clear proofs, not
an every-powerup pass or an assertion that a later changed ROM is fully tested.
