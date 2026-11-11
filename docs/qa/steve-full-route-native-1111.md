# Steve Hermann clears 1-1 in Mesen

The installed MMC5 ROM `e6b152e2` clears the authored 1-1 route and
enters active underground 1-2 at X40/Y48. The controller starts at the
title, selects Steve by pressing Select twice on Mike Jones, and punches
the first naturally spawned Goomba. Steve reaches 1-2 with 4 HP and
both lives after 5,382 physical frames and 2,748 authenticated movement
projections. It uses no helpers, cheats, or shortcut pipe.

The replay checks six pipes, all three gaps, the flagpole and the castle
transition. For the third gap, a short hop reaches the cap near X2400.
Releasing Right in the air lets Steve land before the fresh jump from
X2429/Y112. The next grounded sample is X2488/Y112. The cap controller
keeps braking until an actual grounded position after X2411. In an earlier
physical trial, accepting the native grounded state on the launch update
removed the brake prematurely and led to a pit death at X2468.

The separate [CPU route](steve-full-route-cpu-1111.md) also reaches active
1-2 and retains all 6 HP. The two routes share the third-gap strategy.
The Mesen evidence establishes a full stage with the current locomotion
and punch. Steve’s other original moves, armor and upgrades remain open.

- ROM SHA-256 `e6b152e26b43449115a7ff21903ae756346052e55dbdd94d8751e8c3a0951f23`
- Passing Mesen receipt SHA-256 `31422854fdd27509d19cdb121cf45b59264bfd19ad61ce7d45fcf3fa21b9fa9f`
- Passing controller SHA-256 `936054172c22f65e099d40f0533dbfd2daa521510db2947bd63d41c602c01129`
- Earlier negative receipt SHA-256 `f4c53f52d414cc528040ca31146f64e534b72511cc291323e146a1a3ac8f7f17`

[Replay launcher](../../tools/audit/compose_steve_full_route_1111.py)
