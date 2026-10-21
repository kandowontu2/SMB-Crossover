# Hosted water behavior

Reference: `super-mario-crossover.swf` from the requested site, SHA-256
`46bdcf0b60721bbe0f006cdb083f503e0312feacede6f65f2942f7a5a406b1eb`.
The inspected source is its decompiled `com/smbc/characters` package, rather
than the later public v3 release. Flash coordinates are twice NES coordinates;
velocity converts by `/120`, acceleration by `/7200` for a 60 Hz update.

| Character | Water jump/paddle power | Submerged gravity | Above-surface gravity | Air jump rule |
| --- | ---: | ---: | ---: | --- |
| Mario | 200 | 350 | 700 | Fresh A paddles again while submerged |
| Mega Man | 550 | 500 | 1100 | Ground jump only |
| Samus | 500 | 400 | 700 | Ground jump; A exits Morph Ball |
| Bill | 550 | 500 | 1000 | Ground jump only |
| Link | 530 | 500 | 1000 | Ground jump only; cannot start during a grounded sword attack |
| Simon | 550 | 750 | 1500 | Ground jump plus one second jump |

Values above use the source's Flash units. `Character.updateObj` caps bottom
walking at 90 and downward speed at 250 before gravity. It selects water gravity
only when `hTop > 64`; equality remains above water. The ROM evaluates this using
the pose's hit rectangle and Q0.16 position, including half/quarter-pixel heights.

The SWF's rectangle transforms supply the following heights in NES pixels:

| Character | Standing | Air | Crouched/short form |
| --- | ---: | ---: | ---: |
| Mario | 15.75 small / 31 large | Same as power form | 15 crouched |
| Mega Man | 24 | 27.5 | 15 sliding |
| Samus | 31 | 25 | 13 Morph Ball |
| Bill | 31.5 | 16.25 | 15 crouched |
| Link | 15 | 15 | 15 |
| Simon | 30 | 25; 30 for whip/throw | 15.75 crouched |

Mario's horizontal acceleration is 400, with a 150 air limit. B does not enable
running underwater. Coasting uses `0.05^(1/60)`, stopping below 40; grounded
direction reversal uses `0.0001^(1/60)`. His paddle impulse is -200 and fresh A
can repeat it. Upward release friction is `0.0001^(1/60)` for Mario, Samus and
Link, `0.000001^(1/60)` for Mega Man; Bill and Simon retain their fixed jump arcs.
The source's moderate swim animation timer is 75 ms.

`MegaMan.lastCharacterCheck` restores slide speed to 225 after the common bottom
cap, and the water slide distance is 100 Flash pixels. Samus's Morph Ball,
bombs and beams remain available. Bill's aiming and shots, Link's sword and
boomerang, and Simon's whip and axes retain their normal controls.

`enemies/PitVacuum.updateStats` explicitly requires `player is Mario`. Its pull
adds 400 horizontally and 600 vertically in acceleration units; it bypasses the
ordinary water fall limit for that update. Mario uses 575 input acceleration
while being pulled horizontally. Guests are immune.

The current ROM's requested Luigi alternate shares Mario's complete swimming
and whirlpool behavior. His higher jump and lower braking traction apply only
to dry native movement.

`tests/water-common.lua` runs all six characters in the actual 2-2 room on both
mappers. It uses explicit fixture setup, and checks movement, jump/re-paddle
rules, release friction, surface boundaries, fall caps, weapons, poses, water
music and currents. It is not a full water-level completion replay. Numerical
movement is quantized to Q8.16 and native NTSC frame timing; existing NES art,
bubble effects and enemy collision geometry remain subject to the parity audit.

The later2.02 Link movement migration uses his direct175 horizontal assignment,
then the shared90 underwater-ground cap; it has no horizontal acceleration or
air coasting. `tests/link-source-movement.lua` independently checks first-update
start, reversal, release/both directions and sword states in dry/wet ground/air
arenas. The older hosted-source Link acceleration expectation in the common
water fixture is superseded by that2.02 rule.
