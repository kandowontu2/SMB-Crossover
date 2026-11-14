# Current Kirby copied-shell audit, November 14

The reported too-fast/pass-through shell issue is already repaired in the
retained delivery lineage. This audit reproduces a successful normal-controls
green-shell hit on exact installed421, rather than proposing another shell or
inhale patch. No ROM, allocation, helper, CLI or installer changes are made.

Current ROM:
`421379021e775e6e03357c0aa11d4cab04008452f94bc9e8938f0662cc0c979f`.
Complete Kirby PRG74:
`119a6fe415a914c415a51bc46f0cc22569cd4c7e1282d83f512c3b2031573e9d`.
This equals the installed1113 audit's entire bank. Capture-frame and red-catch
inverse preimages/forward source recomposition both match current bytes.
All retained green-route native hook preimages authenticate against421.

## Original semantics and retained repairs

The November1 owner checkpoint, source ZIP
`e465b2c73a0e0ce9a36f55ad3cac648bdf2ec6b1e198c8763974be419688c847`,
contains the actual shell override: copied kinds2/3 use signed integer+3/-3
with zero fraction. The native kicked-shell speed table in current421 remains
`30 d0`; native `MoveObjectHorizontally` splits that signed4.4 value into its
integer/fraction parts, giving the same three-pixel step. Generic projectile
spawn speed4 does not bypass the subsequent shell-specific override.

The copied shell is drawn16×16 around its stored center and uses the native
enemy box selected by `Enemy_BoundBoxCtrl`. The original origin-radius12 check
missed ground contacts with a14-pixel center/origin Y difference. The installed
helper uses signed world/page arithmetic and the native box instead. The
November11 red-only swept path additionally covers its old-to-new horizontal
step against moving enemy boxes; green retains endpoint rectangle contact.

The red outbound turn age remains32 and return speed+/-3. The November12
same-span catch retires it when horizontal distance to Kirby reaches-3..+3,
before the next step can cross Kirby, fixing the older oscillation. Current
whole-bank equality preserves that qualified catch and the previously tested
red enemy-defeat path. The old `src/kirby_weapons.s` text still has generic
speed4/turn24 and lacks later overrides; it is not the installed authority.

Historical evidence stays scoped to its exact versions:

* November1 `c864e46a…`: declared flat native terrain/player/NPC fixtures,
  real inhale/Down acquisition and both grounded shells; no ability/health/
  shot/outcome seed. This was not a natural full-stage proof.
* November10: normal native streamed green Koopa, Down copy2, real Goomba
  defeat at3px/update and full1-1; see `kirby-current-functional-1110.md`.
* November12 installed8fc: normal green acquisition/combat/full1-1 in6296
  physical frames, HP5/lives2, receipt
  `f9cd55629692af89d070d14133872f6f13a3f4abe723b30084fe481c7ea39410`.
  Its red acquisition/defeat/clean-catch receipt is
  `649388c86bbfabb7a073906e49ec66d79b6aeaccca257de43e4897f97823329e`.

Those historical native runs are not relabelled as current421 Mesen runs.
The current preservation and CPU witness below are additional, separate proof.

## Current normal-controls CPU witness

`audit_kirby_shell_current_1114.py` uses the retained green controller source
`730a40160788c5fa41b3bf8b931bfd14834bb463ae75a04b18f07f12e0d2ff20`.
It applies the same five-byte capture-hook authentication update used by the
delivered1112 replay. Only the Lua menu coroutine is bypassed after the
established current native menu arena, real Start/parser and Kirby constructor.
Thereafter only controller peripheral input and the normal Main/NMI scheduler
change. No actor, terrain, position, health, copy, mouth, shot, ability or flag
state is seeded. This frontend is a CPU unit; it is not a fresh native PPU
title-opening or physical timing claim.

The exact source frontend/controller SHA256 is
`2d3a09cc750ecedf7672ab8cee53cae424bc8857736b7867b25917bc3d4599c2`.
The encounter passes after2154 source scheduler/Main updates. `KbWeapons`
executes exactly2154 times, once per observed Main; no doubled weapon update
is seen. The original authored Green Koopa is constructed at1712/Y184, later
captured at target1566/player1555, and swallowed using normal Down to earn
copy2. Grounded fresh B fires at player1758/Y176 against a separate streamed
Goomba originally born at1826/Y184.

Shot ages1..6 advance X1777,1780,1783,1786,1789,1792: exactly3px/update with
zero horizontal fraction. At age6, its center1792/Y198 gives native shell
rectangle `[1784,190,1799,205]`, overlapping the Goomba rectangle
`[1798,198,1808,204]`. The actual `ShellOrBlockDefeat` executes for intended
slot0 and returns to the authenticated Kirby caller; enemy state becomes34,
and the shell is consumed. The14-pixel Y origin difference demonstrates why
the superseded radius12 test was insufficient.

Kirby retains copy2, HP5 and both lives across this combat. One earlier route
injury is retained, matching the historical non-injury-free scope. This one
successful encounter is not exhaustive green/red enemy/terrain/water/pool
coverage or a new current full-stage/native qualification. No naturally
reachable new shell defect was demonstrated, so no new patch is proposed.

Run:

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/kirby-shell-audit-source-1114 --max-files 1 --timeout 600 -- python -B tools/audit/audit_kirby_shell_current_1114.py
```

The producer passed and created zero files; the output root remains absent.
No Mesen process, capture, ROM output, backup or release asset was created.
Closed inhale suites were not rerun. No helper platform was added or moved.
