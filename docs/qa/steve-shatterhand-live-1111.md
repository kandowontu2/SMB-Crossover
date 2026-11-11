# Steve Hermann’s live Shatterhand punch

The in-memory candidate is
`409d5a2e3b8ca1fdf6fa4512cac399310c44c1837b88b9f7d2a1e5bde858d280`
on the installed Prince brick build
`17122790d711b905c681dced1fd9b3a0e69e1364cb039d514ba635c31a1e4fed`.
The two resident headers contain
`a7102009d541d456ddb444f69f81a4f1`. The source recipe also accepts the earlier
exact Jay nightly `4df81758`.

Steve enters through the existing Mike-family weapons routine after its native
timer, death, active-game and enemy-tracking checks. The alternate selects the
original standing, airborne or crouched punch worker. Its real B edge and
combo counter drive the donor attack phase and source hit-object lifetime.
The crossover gives that stationary hit a signed world coordinate from the
donor offsets, adapts the contact box and damage to SMB actors, and uses the
native defeat, scoring and drop path. The arm cells are original Shatterhand
pose `$7c` CHR data. Steve’s current host body renderer supplies the remaining
body and the native metasprite routine clips and rotates the added arm cells.
The source punch request remains `$0c` and uses the host’s existing Square 1
attack cue.

| Native location | Role |
| --- | --- |
| PRG65 `$A696`, 157 of 162 bytes | Mike-family cold selection for Jay and Steve, with CHR220 as the third metadata row |
| PRG98 `$A01F → $AFDC` | Steve-only attack gate. Mike and Jay continue through the original stock weapon code when they enter this routine |
| PRG94 `$B27F` | Both 16-byte resident headers validated before the worker is called |
| A3 `$B303 → $B3AA` | Variant mux retains Jay’s prior target and Steve’s legacy movement fallback |
| A3 `$B586` and `$BED4` | Hit birth and native gameplay bridge |
| C2 `$DA80` and `$DBD4` | Relocated 340-byte donor leaf and 42-byte renderer packet |
| `$5C80–$5C8C` | Steve state within the Mike family’s scene-reset overlay |

Controller-only CPU replay selects Steve from the real menu, reaches 1-1 in
167 updates, verifies all 1 KiB of CHR220 was copied into C2, and observes
14,350 cold PPU reads. Held B produces one edge and one birth on the third
update. For each facing, six native Main draws match the following modeled
NMI OAM DMA with CHR220 published and 8×16 sprites enabled.

| Facing | Player world position | First arm OAM cells in Y/tile/attributes/X order |
| --- | --- | --- |
| Right | (40, 176) | `b0200038` and `b0220040` |
| Left | (39, 176) | `b020401f` and `b0224017` |

With ordinary Right input, Steve stops at world (216, 176). At the first
naturally spawned Goomba’s approach to (248, 184), a fresh B creates a punch
on update 3 at (239, 188). The punch calls native defeat on update 7, when the
Goomba is at (245, 184). The native Goomba score control becomes 1 and both
lives remain. The replay uses the authored actor without positioning it.

Mike and Jay each match 80 ordinary scripted Main updates against the parent,
including visible OAM, VRAM and CHR registers. Mike makes zero cold PPU reads.
Jay’s extra 2,050 cold reads transport Steve’s row and the modeled gameplay
state remains equal. The existing Steve body’s eight native descriptors use
only CHR220 tiles 0–31 in the 64 checked facing, state and pose combinations.
The two punch pairs use tiles 32 and 34.

All 32 one-byte resident header corruptions decline Steve’s combat and draw
paths while keeping Mike’s shots absent. Eight NMI and eight IRQ cuts return
with their mapped banks, active stack, OAM and Steve state intact. Twelve
directed cases cover the native OAM capacity cutoff, rotation and a player
crossing the world-page boundary relative to the camera. Reapplying the
Prince brick change to the Steve composition on `4df81758` reconstructs the
exact candidate above. The two source changes touch disjoint bytes.

The compiled attack uses the original normal/strong punch phase data and an
adapted enemy rectangle. The visual integration covers the two outward arm
cells with the existing body, including the standing timing and both facings.
The original movement, armor, companion controls and later progression remain
open. This report records the CPU model. The physical Steve and Jay
controller replays are recorded separately. Steve’s complete 1-1 route
remains open.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/steve-shatterhand-live-1111 --max-files 1 --timeout 240 -- python -B tools/audit/check_steve_shatterhand_live_1111.py
```

The replay writes zero files.
