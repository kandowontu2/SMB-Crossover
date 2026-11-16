# Actual nightly timing attribution

Root92156 is terminal PASS on actual Downloads7fb3, SHA
`7fb328a6dcf6b50fd000e81eced4fd4b7390bedec56085d33130434003cc76d0`.
Receipt `732a41808221db005d20dd83b8ebdc9b1b466208ef6d9e27304ffbce4dd2b40d`.
Factory `fa3d4dbc85517e38a9af7ef1b4f18d546bf7e8f91c7cc73fb724b81a90df5508`;
LF Lua `6b3371c8111759feda51a57fa8b37cbd23e5ac1717b8acc7945048d3fab73709`.

The controller and attribution body remain identical to the qualified ACE
observer; only the exact current-ROM prefix/bank hashes change. No game bytes,
native state, settings, captures or output files changed. Both actual current
runtime code and all return pairings were checked. The private ROM remains7fb3.

## Measured cadence

Idle:48 Main returns/48 physical frames,19 missed controller-read frames among
47 fully observed frames; Main distribution0:20,1:7,2:20. Right:32/32,15 misses,
distribution0:15,1:2,2:15. Both windows have no enemies. These reproduce ACE's
uneven update cadence; average one Main per frame does not establish smooth60Hz.

## Attribution

Mean exclusive CPU cycles per call; interrupt time is subtracted.

| Span | Idle | Right |
| --- | ---: | ---: |
| Normal Main,3 checks and drawing | 24821.24 (29) | 25098.65 (17) |
| Catchup Main,2 checks without drawing | 16827.16 (19) | 17058.33 (15) |
| Shared DrawAllMetasprites | 7463.83 (29) | 7459.35 (17) |
| BtGraphics | 1083 | 1083 |
| BtDraw | 2742 | 2742 |
| MetaspriteRenderLoop | 1324 | 1324 |
| BtMovement | 1308.50 | 1571.78 |
| Actual BtPhysicsStep target | 711.50 | 980.59 |
| Regular-NMI AudioUpdate | 3378.07 (29) | 3377.41 (17) |
| Busy-NMI AudioUpdate | 2696.89 (19) | 2786.19 (16) |

DrawAllMetasprites includes the named graphics/draw/render spans, and movement
includes physics. Do not add these overlapping measurements. All head queries
cost123 cycles and side queries118. Audio wall maxima are4989/4520 for regular
NMI and3257/3230 for busy NMI; regular Audio groups include480/360 nested IRQ
cycles in total, correctly subtracted from the means above.

All985 attributed entries have matching returns: head240,side320,BtDraw46,
BtGraphics46,movement80,physics80,DrawAll46,render46,Audio regular46/busy35.
Main/ISR/getter/service pending and unacknowledged counts are zero. Source's
1120 ordinary-model entries are a separate receipt and are not this native count.

Shared drawing and audio are confirmed substantial costs. The helper's next
work is read-only inspection of concrete redundant work and placement/funding,
with no optimization bytes authorized yet. This timing receipt does not itself
reduce lag or qualify other characters, modes, stages or physical consoles.
