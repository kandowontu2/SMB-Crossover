# Current Final Fantasy earned-powerup check

All four classes pass a natural mushroom → flower → upgraded-attack
continuation on current c10, SHA256
`c10b7d87f466bf028096bddd33b7ac2baee242870ee83ccc4eebd529af57bd7f`.
White Mage separately passes an earned Heal after genuine Goomba injury.

These are logical **CPU/controller/NMI** tests of the actual current menu,
GameLoop, 1-1 parser, item production, collisions and private callbacks.
After confirmation, the tests change only controller input/scheduling.
No terrain, actor, health, equipment or position is granted. No ROM, Mesen
capture, output directory or other generated file is written. This is not a
physical cadence, audio-output or full-stage qualification.

The mushroom block is at worldX336. It releases naturally at epoch412 and
collects at548 through nativePowerUpObj → NrPickup → HandlePowerup →
FwHostCollect → FfHostCollect/FfPickup. All four classes reach Power/Earned1;
White has one Heal charge, the others zero. Native sound queue32, erased
actor flag0 and floaty6 are verified. Exactly60 transformation callbacks
at epochs549..608 finish at engine8/Active0/Timer0. Ordinary movement then
advancesX405→421 by619 with both lives.

The continuation steps off the native lower brick roof and bumps the actual
flower block at worldX1248/Y144 from below. It waits40 updates for emergence
and the passing enemy, then collects by ordinary movement/jump. The actual
flower is born at continuation536 and collects at629, playerX1237/Y108.
All four classes reach Power/Earned2; White's charge count becomes3 and
the others remain0. The same erasure, floaty and native sound-queue checks
pass, followed by exactly60 freeze callbacks and16px resumed movement to
X1253 by700, lives2. Native BG collision calls, proper class palettes,
outlinesOff0 and visible shadow OAM remain intact in this CPU fixture.
The fixture starts the option byte at zero; physical cold startup defaults it
to one. Consequently this result does not prove mandatory FF black masks with
the global option off. The later physical-start observer caught that scope
error; the game's existing conditional FF ink path still needs a separate
visual check against the user's always-on FF-shadow requirement.

Further ordinary controls cross the second pit and attack a naturally
streamed Goomba:

| Class | Earned attack | Actual native result |
|---|---|---|
| Fighter | Melee150 | Goomba state34, HP0; defeated |
| White Mage | Melee50 | Goomba HP25 |
| Black Mage | Tier2 Fire150, projectile kind1 | Goomba state34, HP0; defeated |
| Thief | Melee25 | Goomba HP50 |

The three melee hits occur at continuation148, playerX1500/Y176, enemy
slot0/X1526. Black casts at128 fromX1467; its actual projectile reaches
FfHostDamage at163 againstX1518. Every native damage callback returns carry
set. All classes retain Power/Earned2/lives2 without injury. The different
remaining HP values are expected class attack strengths, not missed hits.

White's separate earned-Heal route takes a natural Goomba hit atX705/Y176:
Power1→0, Earned1/charge1 retained,90 hurt and12 knockback. Fresh Up+B after
knockback starts30 preparation updates. Completion restores Power1,
consumes the charge1→0 and queues native sound32; finalX687/Y176, lives2.

Frozen zero-output sources:

| File | SHA256 |
|---|---|
| `tools/audit/check_ff_white_mushroom_current_1110.py` | `c6c3a7dca9cea3bf4577d5038f74a22261be8989edc1ad87ddd8590d0e581de0` |
| `tools/audit/check_ff_all_mushrooms_current_1110.py` | `e122dc0dc793eeb7aa002389ea1112302f3cc008b19b77d38d75f695cdcc5f7e` |
| `tools/audit/check_ff_white_earned_heal_current_1110.py` | `d6b7c5a81d7f772a644df763d31a6938ee5a30e9e1515f6653dce9c49f75225a` |
| `tools/audit/check_ff_flowers_current_1110.py` | `e990661e7b9fe754dede187b39dd0dfda6367f051cdd701b01ddc9b03aad50ec` |
| `tools/audit/check_ff_earned_attacks_current_1110.py` | `dd8015682993e4a13190e9a9e200a1ae4b227767172b5ad6036831447110b44e` |

The attack checker reruns the complete first two earned pickups for each
class. Reproduce it without generated files:

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/ff-earned-attacks-cpu-1110 --max-files 1 --timeout 600 -- python -B tools/audit/check_ff_earned_attacks_current_1110.py
```

The later `check_ff_star_life_current_1110.py` adds actual earned Star and 1UP
routes for all four classes on this same c10 image. They verify native deferred
life awards, Star protection, timer expiry, palette phases and music recovery.
See `ff-head-corner-1110.md` for subsequent private full-stage repairs and their
separate qualifications. Bolt/Ice/Light, every possible attack and complete
native emulator review remain open. Existing helper positions did not change; see the
[helper inventory](helper-platform-inventory-1101.md).
