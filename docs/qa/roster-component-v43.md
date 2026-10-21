# Ryu wall and vine attack admission

Accepted component checkpoint43a passes all761 unchanged-fixture emulator slots
in one full run and all68 independent source-derived Ryu cases. A401-file
source archive rebuilds both ROMs byte identically from fresh extraction. The full roster audit,
weapon review and final recordings remain unfinished.

The pinned Crossover2.02 Ryu source rejects a primary sword press in ST_CLIMB
and ST_VINE. Its state check also clears sword hit rectangles while attached.
Special input rejects ST_VINE; Jump Slash requires ST_JUMP, while projectile
subweapons can still be thrown from a wall.

## Reproduction and repair

Accepted42 reproduces the independent source-input failures on both mappers.
The68 seeded arena cases contain32 failing cases and36 passing controls,
with56 failed assertions. Real controller input establishes wall attachment
and triggers attacks; initial arena/inventory setup is explicitly seeded.
These are mechanics components, not power-on stage traversal proofs.

The repair rejects new primary wall/vine attacks and new vine specials.
An already admitted sword attack continues its timer while wall/vine contact
suppresses its rectangle generation. The special dispatch retains legal wall
projectiles. A separate selected5 check rejects wall Jump Slash before ammo,
activation or sound effects. Airborne Jump Slash and wall shuriken retain
their exact tested one-time costs of5 and3 Ninpo, respectively.

The first patch removes unreachable legacy throw code, giving a net reduction
of2 bytes in bank37. The selected5 guard adds6 bytes to bank61. There is no
new RAM, FIXED-bank code or farcall. The native controller reader and resident
injury bridge are unchanged. Graphics and mapper headers remain identical.

All68 unchanged source-derived cases pass on43a across both mappers. Sources,
frozen fixtures, per-ROM callback bytes, raw logs and CSV receipts are bound
by `build/verification/ryu-gates-v42-actual-negative-a/report.json` and
`build/verification/ryu-gates-v43a-source-positive-a/report.json`.
`tools/audit/run_ryu_gates_v43.py` drives these checks independently of the
existing full emulator suite. Neither suite's oracle was relaxed.

## Remaining scope

This repair does not establish full source equivalence. Ryu's current/cached
body geometry and input phase, Jump Slash animation-phase transfer and
cancellation, projectile debit timing, Bill Flare behavior, final-hash routes,
all-weapon/upgrade coverage and audiovisual review remain unfinished. Old
routes on34/38d/40 do not certify43. Dense-scene lag and sprite flicker remain;
43 adds no new general performance claim. Shadows remain off by default with
the gold option row from32 and the graphics/audio changes from42 retained.
