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

At the final staircase on `677aad54`, Prince reaches X2945/Y112 grounded on
the native step. Up from that position fails to mount the next riser at X2960,
which occupies the far half of the source actor’s 32-pixel terrain cell.
The replay ends here with both lives.

| Exact Mesen run | Receipt SHA-256 |
| --- | --- |
| Clears both later Goomba pairs and the first stair, X2228/Y112 | `b5652ef37d075366402dc274726f2bef2d6e9eec7b3f95b7aa09fbe1eac3364b` |
| Catches and clears the third gap, X2562/Y176 | `7d4c343b85f9ce0c0c0e527f58be358a5e24c373da12412da06f0663916dfb1e` |
| Clears both late pipes and reaches the final stair, then Up falls back | `9fbfe04ce7f7eaeea1cda7b8da4c0a0f35e5bda0ef343999ce5476478b6f87a9` |

[Controller and replay launcher](../../tools/audit/replay_prince_full_route_1111.py)

## Final staircase delivery

The next higher cell above source room row zero arrives as `$FF`.
The raw3 `$BE06` comparison used an unsigned branch and placed that cell
below the current row. One decoded opcode changes the branch from `BCC`
to `BMI`. The bounded row difference is signed. The authenticated runtime
still occupies 6,400 packed bytes. The inverse recovers exact Downloads ROM
`c8d328a27efbc900216985aeb86600a1f626f8cc76e93a91bb30b2c1f8c2e727`.

The CPU test covers 104 unchanged row comparisons, 12 corrected wrapped
comparisons, 55 unchanged flat-terrain updates, and 154 unchanged native
pipe updates. In the authored staircase scene, the parent falls back to
X2913/Y144 and the candidate reaches X3008/Y48.

The controller-only Mesen replay reaches X2940/Y50 in the original
climb pose. Fresh A climbs the upper stairs, reaching X3046/Y50 in an
original neutral pose. A run down the far side lands at X3084/Y176 with
2 HP and both lives. Continued Right stalls at X3149/Y178 by the flag.
A standing jump from X3046 reaches X3154 before landing. The native shaft
collision needs X3158–3161 on this approach before the bottom side probe
passes below the shaft. The far-side landing ends the original jump with
fall damage. This route adds no helpers.

The Downloads ROM repeated the checkpoint receipt exactly at X3084/Y176.
Jay also repeated the full native clear and five machine-gun shots in 1-2 on
the installed ROM. The two changes occupy disjoint bytes. The automatic patch
guard passed before and after replacement, with zero backups.

| Exact proof | SHA-256 |
| --- | --- |
| ROM | `41bd1143994bfa1543da0b4b1032778be613a36a006f948762ca1dcfa57cc28c` |
| IPS | `38315b48d874e9c4d904b8e75a8df6085b155e3639a8d7f15f18416cee6f2ee8` |
| Mesen candidate and Downloads staircase checkpoint | `59c7e34e6e367089370bcf13456cd76fb72ff1c1bb7aac5958f400614ab97b6f` |
| Assembled controller | `8d7b35f9354c0dde782971d35847273d656850b584809cb55fbc6c8c6792b270` |
| Lua continuation | `d34e073c8337ea2eeaa4f648c7406deb9e19d953cee2173535622f6c2ca26191` |
| Installed Jay regression | `c82b2e7374fc117486fd054501ec0951002deb0b040dcd3a4912fb45e5e9dae2` |
| Physical final stair and run to the flag footing | `3b2284e1df246d734d50a83f00b3c0c43f12f12f2afd6dc3f39e84cd4c065318` |
| Grounded running jump trial at X3121 | `d3b8219c0c1a89fbbb025e00172180594fc4dfb05af539d06c35865868d45c7f` |
| Standing jump trial from X3046 on the summit | `e42124e718d8b5807fabbd39df24062ee38926434697190cad1612f84362cdb0` |
| Running jump trial from X3062 on the summit | `a7cf2983b622e0fadde898ef05aac8aa5c4c00197d51594901b1762181df0f3d` |

[Signed row recipe](../../tools/audit/compose_prince_signed_world_row_1111.py) ·
[CPU verifier](../../tools/audit/check_prince_late_stairs_1111.py) ·
[Delivery recipe](../../tools/audit/deliver_prince_signed_world_row_1111.py)
