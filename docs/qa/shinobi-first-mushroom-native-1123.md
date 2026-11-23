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
overlap check when the contact callback declines. The repair needs to
forward the block Shinobi actually hits to the native bump routine,
then allow and handle the resulting pickup. All four pickup tests are
still open.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/shinobi-first-mushroom-source-1123 --resume --max-files 8 --timeout 300 -- python -B tools/audit/probe_shinobi_current_head_1123.py --run
```
