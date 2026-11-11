# Jay projectile contact under scrolling

The released projectile worker at `$B24A` accepts enemies on page zero
and compares their world X to the projectile's projected screen X. After
scrolling, those coordinates have different origins. The replacement keeps
the same Goomba eligibility and strict 20-pixel bounds. It converts the
projectile's Q4 world X to whole pixels and subtracts it from the Goomba's
full page and pixel position plus the eight-pixel center offset. This
includes a carry when the center crosses a page. The existing flight and
terrain checks execute before contact. The first valid slot in descending
order consumes the projectile and enters the composed ammo capture and
native defeat routine.

The worker occupies 164 bytes at A3 `$BE30..$BED3`, and `$B24A` jumps to
it. It reuses C2 `$C0F7..$C0FA` after flight finishes. The terrain query,
status, and collision-class outputs at `$C0F0..$C0F6` stay available.
The composed image uses ammo capture at `$BAA8`.

The CPU checker boots the composed cartridge and checks both the redirect
and copied worker bytes in authenticated RAM. Its 1,900 boundary cases
cover both directions across page edges, 0 and 15 Q4 fractions, and the
19/20-pixel contact boundaries. They include 108 cross-page contacts and
96 contacts where the enemy center carries into the next page. Eight
guard misses and one multiple-enemy priority case pass.

The following controller routes use the first Goomba spawned by the
unmodified level parser. Both lives survive in each run.

| Weapon and test | Main update | Camera X | Shot world X/Y | Goomba center world X/Y |
| --- | ---: | ---: | --- | --- |
| Stock, same page | 102 | 77 | 330 / 191 | 348 / 192 |
| Stock, opposite pages | 259 | 104 | 252 / 191 | 270 / 192 |
| Pause-selected spread, center round | 124 | 110 | 323 / 191 | 337 / 192 |
| Pause-selected spread, downward round on opposite pages | 266 | 104 | 250 / 175 | 266 / 192 |

Restoring the old `$B24A` instruction produces no page-one defeat over
135 updates with the same initial stock controller sequence. The test
checks the native defeat state and score for each successful route. The
scope covers existing Goomba contacts and excludes other enemy classes.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/jay-silius-world-hit-1111 --max-files 1 --timeout 600 -- python -B tools/audit/check_jay_silius_world_hit_1111.py
```

The tested installed parent is
`852712c9a2afce71c45f9f2c970e1f5c7969c58d878cfa0a250d2bdb7ba93383`.
The composed image is
`4df817587ea5b0aff3f278a4201976745bad4d9dd1b2a99d6cb5fd3b9c74dadc`.
The worker SHA-256 is
`9e94f8b79f35be305572084227805fb14902fb8ceec54fd80000b18331bd2acc`.
The bounded checks run in memory and generated no files.
