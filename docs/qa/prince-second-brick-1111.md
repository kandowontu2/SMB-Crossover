# Prince clears the first Koopa approach

The controller-only Mesen replay on installed MMC5 `409d5a2e` reaches
X1713/Y176 with four HP and both lives after passing the live green Koopa.
It uses the authored bricks and original Prince controls. The passing
receipt is `b5bb394d2788ca8417fade76653a3cece93b8a63153127e4eddf6c57ab3247a3`.
The assembled controller SHA-256 is
`043423503ef04630f511cb1d8591a0619af165dedde1b81bb7d73781bc0006b4`.

| Action | Position | Original update |
| --- | --- | ---: |
| Standing jump from the first coin brick | X1491/Y112 | 2963 |
| Recover and settle left of the next brick pair | X1577/Y176 | 3094 |
| Climb the pair with Up | X1587/Y112 | 3201 |
| Jump immediately from the new foothold | X1587/Y112 | 3203 |
| Pass above the live Koopa at X1590/Y184 | X1625/Y112 | 3229 |
| Reach far-side ground | X1713/Y176 | 3369 |

The second climb finishes on one foot. Holding neutral on the previous
`17122790` build made Prince enter action 7 and displace backward from
X1587 to X1564. A fresh A from the cap starts his original action 3 and
keeps him above the Koopa. The two ledges are existing 1-1 geometry, so
this route requires no helper platform.

The next native Goombas are slots 1 and 2, X1816 and X1840 when the player
reaches X1713. Four ground running-jump timings reached legitimate contacts
before clearing both walkers. The native terrain includes question blocks at
X1744 and X1792, both with top Y144. The climbing probes settled at X1720
and X1744. The former only reached action 28 and the latter was directly
under the block. The intermediate stance beside its left edge remains to
be verified. The full 1-1 clear and earned power-ups remain open.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/prince-second-brick-1111 --max-files 1 --timeout 140 -- python -B tools/audit/replay_prince_second_brick_1111.py --output build/prince-second-brick-1111
```
