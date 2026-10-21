# V12 swimming-entry audio regression

The v11 systems suite failed intermittently for Pit (music stopped) and Bass
(a song counter wrapped from uninitialized SRAM). Read-only execution tracing
found a concrete foreground overwrite: PlayerEntrance called SetupBubble with
X=12 after guest palette setup. Bubble_Y_Position is $D3, so its indexed stores
at $ACC7/$ACEB overwrote XgAudioPtr+1 at $DF with $08 and $F8. The next NMI then
read invalid macro data and eventually an unwritten compression-history byte.

V12 explicitly chooses bubble slot zero and drift variant zero at water entry.
CrossoverInit also initializes XgAudioSong before the decoder increments it.
No audio acceptance threshold was weakened.

The independent expanded-water-entry fixture selects the real 2-2 room before
Start, then only reads decoder state. It checks valid bubble slots, no foreground
decoder zero-page writes, bounded history stores, initialized song count,
previously decoded match sources, valid macro pointers, and continuing music.
The v11 Pit negative fails on its invalid entrance bubble index. All six
compressed-audio guests pass on both v12 mappers (12 cases), and Pit/Bass systems
pass on both mappers (4 cases). The full v12 suite is separately tracked.

Evidence: build/verification/water-entry-v11-negative/mmc3-pit.log,
water-entry-v12-summary.json and water-entry-v12-systems-summary.json. Immutable
ROM hashes are in build/checkpoints/roster-audit-v12/manifest.json.
