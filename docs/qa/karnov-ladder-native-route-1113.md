# Private Karnov Ladder native route, November13

The readonly factory/controller is ready for root's sole native queue. This
note records CPU evidence; no Mesen run, screenshot, ROM output or public
installation was performed by the helper. The existing4b28/526 source and
all prior qualification files remain unchanged from commit062168a5.

The exact feature is
`526ef1df172c3172fccbd35aa0471a9ff9a5a256a416acba8f7530d147a5b3f2`,
composed over public62. The separately named private level-DATA-only fixture is
`fbe4c2b392eda216ac357f4c69a7bd3ede5720da5bc9bf844b8bbce19d81e156`.
**Never install this fixture.** Its five native question blocks are not the
stock fifth-pickup route, which remains required later.

## Pure API and exact data changes

```python
import replay_karnov_ladder_native_1113 as R
private_rom, lua_text, proof = R.factory(images=True)
# Bytes/text are returned in memory. Root chooses its already-budgeted output.
assert R.digest(R.inverse_fixture(private_rom)) == R.CURRENT
```

`factory(parent=None, images=False)` defaults to reading exact public62 in
Downloads. An explicitly supplied parent must also be exact62; it does not
silently accept another nightly. `fixture(candidate526)` returns the private
image and proof; `controller(candidate526, images=False)` returns the Lua.
`inverse_fixture(private)` authenticates the complete fixture, restores only
its data and proves the forward round trip to exact526. A code-byte mutation
rejects. No existing feature proposal/inverse API changed.

Only14 actual bytes differ, all within these authenticated data edits:

| Native data | File offset | Before | After |
| --- | ---: | --- | --- |
| L_GroundArea6 first15 bytes |20956 |`502107814724570063017701c97168` |`50215800c8003880a8001880fdfdfd` |
| E_GroundArea6 first byte |19023 |`1e` |`ff` |

The header retains the ordinary flat native floor. Five powerup question
blocks use the real area parser at world1-1 left edges80,192,304,416,528;
centers88,200,312,424,536; **top160**. The enemy stream is terminated. The
lower test questions allow mature flower collection with the unchanged
original Karnov jump and a side approach. No code, CHR, jump constant, health,
inventory, position or actor field is patched. Existing native helper
management remains live; the controller requests no helper or new allocation.

## Frozen controller and CPU evidence

Native controller with at most two in-memory stdout PNGs:

- Lua SHA256 `7720a7ecd35482fc7a4c4d6250348f75c64125e99e52bfa4263f63e6b076a76c`,18972 bytes.
- Source Lua SHA256 `298d8ce29a38a4654405e3b22503a9108ddf0ad1d88fc5a725a228588eda509a`.
- Require `SMB_STDOUT_ROM_SHA=fbe4c2b392eda216ac357f4c69a7bd3ede5720da5bc9bf844b8bbce19d81e156`.
- Two optional screenshots are tagged `eight-grown` and `climbed`, emitted
  only via `emu.takeScreenshot()` and base64 stdout. Each PNG is capped4MB;
  there are no file APIs, videos or per-frame dumps. Root owns their capture,
  interpretation and native receipt.

The CPU controller differs only in the literal `WANT_IMAGES=false`; its
SHA256 is `2820afa734e3891e9d21f8894b662bae70a94f4ceaf46e37eca7d992953a4ab2`.
Both compile against the retained exact Lua runtime. An independent equality
check proves that toggling this single output flag produces the native text.
No fake screenshots are supplied by the CPU model.

The same Lua gameplay decisions passed1499 actual Main/NMI updates after167
actual native menu/parser/constructor updates. The CPU starts from the
established menu arena, executes real Select/Start and cold entry, then skips
only the Lua title-navigation coroutine. The native Lua performs ordinary
title/menu navigation itself. The CPU frame helper stops upon arrival at the
genuine IdleLoop+12/SP252 boundary; its binding dispatches that exact arrived
return callback once, without executing another instruction or changing
gameplay state. All A3 and executable C2 bytes stay immutable.

Observed real gameplay:

| Event | Actual Main update | Native result |
| --- | ---: | --- |
| Five C1 head contacts |45,232,538,846,1154 |Player X72/184/296/408/520, Y166; native query row160 |
| Mushroom collection |133 |Actor X104/Y164, stateC0; source shot0→1 |
| First flower |355 |Actor X192/Y135, state80; shot1→2 |
| Boots flower |663 |Actor X304/Y135; owned1, Boots stock1 |
| Bomb flower |971 |Actor X416/Y135; owned3, Bomb stock1 |
| Ladder flower |1279 |Actor X528/Y135; owned7, cycle3, selected2 |
| Actual Select cycle |1408..1423 |FF→Boots0→Bomb1→Ladder2 |
| Down+freshB activation |1424 |Scene1, count0, tip200, owned3 |
| Eight visible cells |1438 |Native world column X576, source center584; bottom192, top80 |
| Held Up24 updates |1438..1462 |Native player Y176→153, selector uses original climb |
| Bottom held Down |1486 |Original scene2, grounded player Y176 |
| Source restoration complete |1494 |Scene0/count0/tip0, owned7, selected2 |
| Final PPU restoration |1499 |All32 pattern cells and five original attribute bytes restored |

All five actors are born from ordinary question handling, pass real native
preparation and observed maturity, then reach HandlePowerUpCollision. The
collector-return observer requires actual actor/tag erasure, native sound20,
popup6 and the exact original shot/option progression. The first four use
slot5; the fifth uses slot4. The controller never allocates an actor slot
directly. No actor or maturity field is seeded by the controller or CPU route.

The grown Ladder reaches actual modeled PPU2C/2D quads, all eight owned
palette2 quadrants, current palette colors21/0F and the Karnov private font
owner. These are the exact approved original32B patterns with explicit native
blue/black color adaptation, not a claim of donor color parity. The final
observer waits beyond source retirement until queued restoration reaches the
PPU, then compares every original pattern cell and affected attribute byte.
Health source68 stays0 (full healthy state), lives stay2, and Boots/Bomb stocks
stay1 throughout. No arbitrary travel, item grant, jump adjustment or helper
request is used.

Run the exact zero-output qualification:

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/karnov-equipment-1113 --max-files 1 --timeout 180 -- python -B tools/audit/check_karnov_ladder_route_1113.py --limit 1800
```

Root still owns native menu/lag-input validation, the two optional screenshots,
native art/restore review, current unmodified-stage regressions, Downloads
installation and any IPS publication. This private data fixture does not
replace ordinary fifth-pickup coverage or the remaining original equipment.
