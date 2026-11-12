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

## Native rectangle construction

`steve_throw_enemy_rect_1112.s` now builds a 16-bit world rectangle from the
installed native `BoundBoxCtrlData`, enemy position, and bounding-box control.
It avoids the clipped eight-bit screen rectangle, so right-edge carry and
offscreen positioning cannot silently wrap the hit area. X and the stack are
preserved. Its caller must express the robot center in the same world space
and include native Y page 1 before calling the overlap leaf.

The bounded `check_steve_throw_enemy_rect_1112.py` passed 1,512 combinations of
six native slots, enemy controls 3–11, seven X coordinates and four Y positions.
The 79-byte leaf matched the installed table through page carries, with no
outputs. Player-only controls with signed offsets are outside this contract;
native actor admission must reject inappropriate controls before using it.
This has not yet been mounted or used to apply damage.

The combined `SteveThrowEnemyOverlap` entry adds an 11-byte wrapper that builds
the rectangle and calls the expanded overlap leaf while preserving the native
enemy slot in X. The carry flag remains the hit result across stack restoration.
The audit now also passes 24,192 composed boundary cases through both routines,
including exclusive-right/inclusive-bottom edges and page carry. The rectangle
segment is now 90 bytes including the wrapper; the overlap leaf remains 81.

## Native target search

`steve_throw_target_1112.s` adds a 51-byte search across the six native enemy
slots, in descending order. It applies the existing companion hostile-actor
filters and admits only bounding-box controls 3–11 before calling the combined
rectangle/overlap entry. It intentionally does not reject enemy hurt cooldown:
the return receipt must be issued even when outgoing damage is suppressed.

The bounded `check_steve_throw_target_1112.py` passed 81 composed cases, covering
page-edge hits/misses, four cooldown values, rejected inactive/high-bit actors,
excluded enemy IDs, defeated states, invalid Y pages/controls, and slot order
when two enemies overlap. The search preserves the stack and cooldown bytes.
This is still detached; native damage and defeat effects are not exercised.
