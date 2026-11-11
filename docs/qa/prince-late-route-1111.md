# Prince of Persia’s route to the final staircase

The installed MMC5 ROM `677aad54` reaches the final staircase in
World 1-1 with 3 HP and both lives. The Mesen replay starts at the
title and supplies controller input through the stock route. It
uses no shortcut or helper platform.

After the question-block jump to X1853, Prince climbs the authored
brick at X1888. He waits on the brick while the first two Goombas
pass, then advances to X1907 to bring the next two into view.
He retreats, takes one careful left step, turns right, and climbs
the same brick again. Both pairs pass below without hurting him.
Running-jump trials from X1935, X1959 and X1973 ran into the second
pair before gaining enough height.

At each of the first two late stair ascents, fresh A on the first
pose-15 climb update clears the rising steps. At the third gap,
holding A at X2448 catches the ledge. Up climbs, then fresh A and
Right cross the gap. The far-side fall costs one HP, and native
ground is confirmed at X2562/Y176.

The later pipes start at X2608 and X2864. Releasing Right at the
wall settles Prince three pixels short. A Right+B careful step
in original action 30 reaches X2593 or X2849. Up from that idle
stance starts the correct climb, and fresh A from its top carries
Prince across.

At the final staircase, Prince reaches X2945/Y112 grounded on
the native step. Up from that position fails to mount the next
riser at X2960, which occupies the far half of the source actor’s
32-pixel terrain cell. The replay ends here with both lives.
The flagpole, castle and active 1-2 remain to be verified.

| Exact Mesen run | Receipt SHA-256 |
| --- | --- |
| Clears both later Goomba pairs and the first stair, X2228/Y112 | `b5652ef37d075366402dc274726f2bef2d6e9eec7b3f95b7aa09fbe1eac3364b` |
| Catches and clears the third gap, X2562/Y176 | `7d4c343b85f9ce0c0c0e527f58be358a5e24c373da12412da06f0663916dfb1e` |
| Clears both late pipes and reaches the final stair, then Up falls back | `9fbfe04ce7f7eaeea1cda7b8da4c0a0f35e5bda0ef343999ce5476478b6f87a9` |

[Controller and replay launcher](../../tools/audit/replay_prince_full_route_1111.py)
