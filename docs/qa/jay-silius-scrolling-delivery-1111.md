# Jay McCray clears World 1-1

Choose Mike Jones and press Select once to play as Jay McCray. Jay uses the
Journey to Silius movement, turn and crouch timing, stock gun, and starting
three-way weapon throughout 1-1. Press Start to pause, press Select to switch
weapons, then press Start to resume. Jay starts with 63 ammo. The stock gun
is free, and the three-way shot spends two ammo per press. Eligible Goomba
defeats can produce a pickup that restores up to 16 ammo.

The controller-only Mesen replay selected the three-way shot through the
native pause menu, used it, crossed all six pipes and three gaps, touched the
flagpole, entered the castle, and reached active underground 1-2 with both
lives. It recorded 2,297 Jay movement entries after scrolling and matched
1,113 projectile cells to hardware sprite DMA. The short hop from
X2176/Y128 lands at X2200/Y112 before the paired staircase jump.
The Downloads launch repeated the candidate receipt exactly.

| World 1-1 placement | Initial left X | Center X | Initial top Y | First visible relative X |
|---|---:|---:|---:|---:|
| Third pipe, ascent | 688 | 704 | 192 | 255 |
| Fourth pipe, ascent | 880 | 896 | 192 | 255 |

The stock 32-pixel vertical actors spawned offscreen at relative X286 and
X287. The controller boarded at X685/Y113 on top Y145 and X882/Y159 on top
Y191. Jay's original jump reaches 52.5 pixels, and the two pipes rise 64
pixels above the floor. Both lifts use the native constructor and carry.

The CPU checks cover original control timing, native pause and input edges,
collision on both sides of a scrolling page boundary, and fallback to the
native pit death sequence. Four controller routes hit a Goomba with stock,
center spread or angled spread rounds and kept native defeat scoring. An
ammo pickup route used a Goomba from the native parser and verified the
pickup arc, landing, refill and sprite DMA. [World contact](jay-silius-world-hit-1111.md)
[Ammo pickup](jay-silius-enemy-ammo-1111.md)

The cartridge loader verifies six rows before admitting Jay's code. The
CPU checks passed eight copy faults and 27 interrupt cuts. A warm owner
reuse performs zero additional PPU reads. Mike Jones and Steve Hermann
matched 60 original gameplay updates each in the pause regression.

The current weapon selection covers the stock and starting three-way rows.
The four later donor weapons, source sound playback and further area
verification remain open.

- ROM SHA-256 `4df817587ea5b0aff3f278a4201976745bad4d9dd1b2a99d6cb5fd3b9c74dadc`
- IPS SHA-256 `8e631e876d64396f3f869ebcecdda4ec53dc82ffa93401d2dbf0f63ddcc51954`
- Full-stage Mesen receipt `8c428c3613ee1d54b9d5d85442bad40b3807c8dd24f5aeff416d4043d2be0ba4`
- Controller SHA-256 `3491acebcc4d9491063857456cd45a73e9c4f129a0abb4725edd59bd4c66d921`
