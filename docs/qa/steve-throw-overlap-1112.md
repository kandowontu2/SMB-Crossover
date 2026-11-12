# Thrown robot overlap geometry

`tools/reference/steve_throw_overlap_1112.s` implements an 81-byte leaf for
the source-documented expanded enemy rectangle: eight pixels on each edge,
exclusive right edge and inclusive bottom edge. Coordinates are signed
16-bit screen pixels biased by $8000 by the caller. Native screen-neighborhood
rectangles must have nonnegative dimensions below 240 pixels; this leaf does
not validate that caller contract or support expansion wrapping at $FFFF.

The bounded comparison completed successfully:

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/steve-throw-overlap-1112 --max-files 1 --timeout 120 -- python -B tools/audit/check_steve_throw_overlap_1112.py
```

All 7,776 cases matched the rectangle predicate and returned with a balanced
stack. Cases cover negative and positive screen coordinates, page boundaries,
8/16/32-pixel dimensions, and points immediately outside, on, and inside each
expanded edge. No output files were generated.

This is detached geometry evidence. It is not a donor CPU comparison or native
enemy-contact proof. The future caller must derive the correct native enemy
rectangle without losing signed screen-edge positions, admit eligible enemy
actors, set the return receipt before checking enemy hurt cooldown, and apply
the original two-point outgoing damage and separate robot incoming damage.
Do not reuse the existing projectile finder unchanged: its point bounds and
early cooldown rejection implement different behavior.

The private full-flight candidate remains `bc7d0ff551d91bc41e339c575442a911b5395026be91b3486b2066ad6a6c65eb`.
Neither this geometry leaf nor native damage is mounted. The Downloads nightly
and Current IPS remain unchanged. The helper resumed the separate original
robot-destruction implementation after the pause.
