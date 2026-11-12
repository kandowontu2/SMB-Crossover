# Steve throw: player recoil and recovery

This is a detached CPU proof, not a delivered gameplay feature. The Downloads
nightly remains `80e6aa3e32574f38b23fa6da6ab3c94bbe7b5ae11b29339b32b11a624fe6f1ed`.

## Source and behavior

- Worker: `tools/reference/steve_shatterhand_throw_player_1111.s`.
- Comparison: `tools/audit/check_steve_shatterhand_throw_player_1111.py`.
- Shatterhand USA donor SHA256:
  `fbdfaab40aedda270d7473be37566b59e68811d932740c105d84fa6b1a7f19e1`.
- Launch is 58 bytes at the proposed `$C4A0` allocation. Recovery is 74 bytes
  at proposed `$C980`. The original action records add 20 bytes including
  their two offset-table entries. Neither allocation is wired into gameplay yet.

The worker copies facing to the robot, calls the throw core, applies opposite
player recoil, and preserves the current horizontal projection. Air throws
seed `$E0` vertical speed and exhaust upward hold. Ground throws remain crouched
through the recovery animation even if Down is released. The shared animation
decoder plays the original `$AC/$AE` and `$B4/$B2` records. A terminal `$80`
action marker keeps the last pose for one draw, then relinquishes movement.
Landing and explicit cancellation clear the action clock.

The donor compares against both speed caps after steering. Throw recoil can
exceed the ordinary walking range, exposing two branches in the existing port
that bypassed the opposite cap. `motion_source()` in the proof retargets those
branches without changing code length or labels. At the current `$DEC0` origin,
the operand changes are `$DFA1: 38 -> 10` and `$DFB1: 28 -> F0`. These are fixture
changes only; the live motion source and ROM have not been changed.

## Verification

Root independently reran the bounded proof successfully:

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/steve-throw-player-root-1111 --max-files 1 --timeout 180 -- python -B tools/audit/check_steve_shatterhand_throw_player_1111.py
```

It compared 60 launches (states 5/6/7, both facings, two selector values, and
five input combinations), 288 recovery updates, donor landing cancellation,
and explicit scene-cancel behavior. The fixture stubs terrain seams to supported
ground and unobstructed air; it executes the original projection, steering,
action dispatch, and animation routines. This does not prove live terrain,
controller ordering, rendering, or enemy contact.

Worker SHA256:
`919a68235276d082ea017f3d6e64e39f5612c2abf0942c8818185986c412240b`.
No generated files or captures were retained.

## Remaining integration

`check_steve_throw_input_order_1111.py` traces a naturally earned Alpha bot in
the installed ROM. During a latched lift the actual order is movement, lift
decision, companion tick, lift orbit, player attack, punch control. A physical
fresh B edge is `$40` in `JnPressed` at every one of those entries, while the
currently unbound `SteveLiftPressed` remains zero. Holding B on the following
update produces no new edge. Thus the accepted throw can clear the native B
edge immediately after the lift decision, before both weapon consumers run.
Do not clear it before the lift decoder has accepted the throw.

Bind the worker to the authenticated scatter payload, append the two action
records without overflowing the existing lift allocation, and connect fresh B
before ordinary punch acceptance. Connect the recovery poses and CHR307 switch,
robot contact and retirement, then verify controller-only gameplay and the
Downloads launch context before delivery.
