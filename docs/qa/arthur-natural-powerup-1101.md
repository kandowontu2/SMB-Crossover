# Arthur natural powerup follow-up — November 1

Current tested ROM: `6f319d2039f920bc85e4a6bfe6ee3327996b42020e03c09e671142eada2a6428`.
The nightly is unchanged. These cold-boot, controller-only runs write no
emulated terrain, actor, health, inventory or outcome state.

The first-block mushroom hypothesis in
`prepare_arthur_natural_powerup_1101_v5.py` failed: Arthur starts armored, so
the actual block chooser releases a flower. The screenshot and current native
chooser source agree. This run does not qualify a mushroom pickup.

The flower follow-up genuinely bumps the block, observes the released item
and its native mature state, then attempts to reach it by double jump. The
first route waited for an exact apex height at input polling and never moved
right; the second route attempts the actual crossing. Neither collects the
flower or reaches the source torch pickup event. Both failed assertions remain
recorded; no natural powerup completion is claimed.

The read-only write diagnostic isolates a real collision defect:

| Observation | Value |
|---|---|
| Physical frame | 984 |
| Player world X before / after | 305 / 289 |
| Player Y | 130 |
| Write PC / physical PRG bank | `$A2BD` / 10 |
| Side / fraction / probe X | `R0=1`, `R4=1`, `R5=65` (world X=321) |
| Player / source mode | Ascending (`1` / `1`) |
| Lives | 2 retained |

The original GNG side probes are native X−8 and X+8. Since Arthur's native
center imports host X+8, the current host X+0/X+16 queries are intentional.
The generic wall clamp instead assumes host X+14 and subtracts 15 after
rounding, producing the erroneous whole-tile displacement at X=305. Keep
the original probes and repair Arthur's separation under an exact owner check.
The proposed correction still needs CPU and native regression verification.

Compact evidence is under `build/arthur-natural-flower-1101-v6/`:
`native`, `native2`, and `diagnostic`. The diagnostic's
`capture/displacement.csv` records the first bad write; its collection result
is deliberately failing. The preparers bind the exact ROM, controller and
runner dependencies and keep each run below four screenshots. No videos or
frame sequences were generated.
