# Shinobi's first Mushroom block in 1-1

On Downloads `93f140ba`, Mesen selected Shinobi through the normal menu.
Shinobi reached X327 on the ground with full health and two lives. Both
jump attempts entered his original jumping state. His upper collision
probes found the question block at world X339 and the neighboring brick
at X331, both at Y156. His original movement stopped the jump at Y172.
The native block bump never ran, so the Mushroom never appeared.

The replay counted 500 Shinobi movement returns over 1,049 video frames.
It wrote no captures and changed game state only through controller input.
Mesen diagnostic receipt
`13ee0716e457c5506267c4166b5031d7fe648955117c89d8c13cd56dd7ad8222`.
The source replay reproduced the four upper collisions and zero block
bumps. Receipt `3ce683402e2a384f380280f43c61a8ce9fb47d5e6c7869b49285b96af6ed54ec`.

The current source dispatch also returns carry clear for Shinobi's
item-contact and pickup-effect callbacks. The engine skips the native
overlap check when the contact callback declines. That left all four
pickup tests open on `93f140ba`.

## Block bump and Mushroom on the test build

The bridge passes the first eligible upper contact to the native block
bump after Shinobi's original movement has finished. When the right
probe touches the question block and the left probe touches the brick,
the question block gets the bump. The three pending fields at
`C811..C813` belong to Shinobi's existing authenticated RAM bank and are
reset on each accepted movement update. Collision direction and the
native water, block timer and hurt checks govern the bump.

In Mesen on `a6d51fcc`, the original jump activated the question block
in column X336, row Y144. The Mushroom appeared at X336/Y136 and Shinobi
completed 25 more original movement updates. Receipt
`06fc72d5dd11022fa4aa6c253c1a0f5ea6b4f98c2596204de1636ea5d97c886e`.

The second test build `3ce7788d` admitted the Mushroom once it had risen.
Shinobi collected it at X394/Y176. His original food reward ran at full
health, set the status that makes the next upgrade block give a Fire
Flower, and played the pickup cue. He retained both lives and 1,000
points through 25 more original movement updates. Receipt
`f7c4c14bed0167a717b54781d086074ed643a9c75adea7f224c146c30f16d62e`.

The linked-code checks preserved the outputs of 2,313 terrain lookups and
768 body-box calls. The terrain lookups took 0–11 fewer cycles in those
cases. They also checked 768 pose and animation-header lookups, 48 item
maturity cases and 42 native pickup-dispatch cases. The latter cover
food heal, Fire Flower weapon upgrades, Star and 1-UP behavior in
controlled states.

The same build passed the full above-ground 1-1 route in Mesen. Shinobi
defeated a Goomba, passed the flagpole, and retained both lives through 25
original movement updates during the entrance to 1-2. The run reached
X3266 in 1-1 and finished after 8,914 video frames, with no captures.
Receipt `04a12ec3c2a7afd27b580ef81ae52a5d826a8d92e0d9a4d422e34b3a3b2f880b`.

Downloads now contains the exact `3ce7788d` build. Mesen repeated the
Mushroom run from Downloads and returned the same pickup receipt
`f7c4c14bed0167a717b54781d086074ed643a9c75adea7f224c146c30f16d62e`.
Both patch guards passed without a same-name patch. The file was replaced
directly. The previous ROM can be reconstructed in memory from the
documented source preimages.

## Fire Flower and the upgraded shot

On the Downloads build `c6915886`, Shinobi collected the Mushroom,
crossed the four opening pipes and first pit, and hit the Fire Flower
block at X1248. The Flower matured at X1248/Y119. The live collision
boxes overlapped and Shinobi collected it at X1249/Y176. The weapon
tier advanced from 0 to 1, and the pickup awarded 1,000 points. He kept
the upgrade through 25 original movement updates with four HP and both
lives. A crouch and B press then fired the upgraded shot, which moved
69 pixels. Mesen receipt
`979806204fffcfa53d9354c18c792c2fa27f4a8d5cb9e37ad4917aeedc49f483`.

The hidden 1-UP and Star still need ordinary playthrough checks.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/shinobi-pickups-1123 --resume --max-files 8 --timeout 335 -- python -B tools/audit/compose_shinobi_pickups_1123.py --run
```

To reproduce the original block failure on `93f140ba`:

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/shinobi-first-mushroom-source-1123 --resume --max-files 8 --timeout 300 -- python -B tools/audit/probe_shinobi_current_head_1123.py --run
```
