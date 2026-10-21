# Special-button audit

The hosted page labels **S** as Alt Attack. The linked older SWF and Crossover
2.02 have different ability sets.

## Exact linked build

The pinned source is in `reference/crossover/decompiled/scripts/`. ButtonManager
maps S to key code 83 and calls `pressSpcBtn()`.

| Character | S in the linked build | ROM equivalent |
| --- | --- | --- |
| Mario | No special action | No separate attack |
| Mega Man | No special action; charging uses held/released attack | Hold/release B charges after the mushroom |
| Samus | No special action; bombs use attack in ball form | B plants bombs in Morph Ball |
| Bill | No special action | B fires his current gun |
| Link | Throw boomerang | Select throws boomerang |
| Simon | Throw axe, including crouching throws | Select or Up+B throws axe |

Only Link and Simon override `pressSpcBtn()` in this six-character build.
The other four do not use the special-button flag for an attack.

## Crossover 2.02

The expanded reference is in `reference/crossover2/extracted/scripts/`.
Special and Select are separate Flash buttons. The NES uses Select for the special action and paused Left/Right for inventory selection. Mega Man and Bass use Select to cycle during play and B to fire; paused Select returns to the primary weapon.

| Character | 2.02 special-button action | Current ROM status |
| --- | --- | --- |
| Mario / Luigi | No normal gameplay special attack | Same |
| Bill | No separate special attack | Same |
| Mega Man / Bass | Cycle acquired weapons backward; Select cycles forward; both select the default weapon. B fires the selected weapon. | Shared inventory and seven special weapons are implemented. Select cycles forward; paused Left/Right cycles both ways; paused Select selects the buster. Bass also has source world/HUD icons, enemy energy drops, exact NSF effect selection, flame orientations and Pharaoh following/stock rules. Mega Man now has separate source-composed special arms, suit colors and Rush's fall/wait/spring/exit states. |
| Samus | Fire an acquired missile; classic mode toggles missile mode | Missiles, missile mode, Ice/Wave beams, Varia, Screw Attack and Morph Ball ownership are implemented, with missile ammo drops. |
| Link | Use selected boomerang, bow or bombs | Short/magic boomerangs, bow, bombs, rings, separate arrow/bomb ammo and pickups are implemented. |
| Simon | Use selected axe, dagger, cross, holy water or stopwatch | Axe, dagger, cross, holy water, stopwatch, shared hearts and Double/Triple Shot are implemented. |
| Ryu | Use selected ninjitsu, including airborne Jump Slash | All five ninjitsu forms, sword extension, the ninjitsu scroll and shared small/big refills are implemented. Jump Slash and normal flips have separate source animations. |
| Sophia | Fire selected standard or homing missiles | Standard missile triplets, homing missiles, their separate ammo, Crusher, hover/wall/ceiling ownership and max speeds are implemented. See the update ledger for remaining trajectory/rendering approximations. |

Pit and Rygar were not in 2.02. Pit's Select hammer and requested flower-level
flight are ROM additions. The unfinished published Pit source's `pressSpcBtn()`
only calls its parent. Rygar currently has no separate special attack.

## Bass's upgrades

In 2.02, Bass's `MUSHROOM_UPGRADES` list is empty, but the Bass Buster explicitly
raises its on-screen bullet limit from **three to four** with the mushroom.
The ROM implements that. Bass does not gain Mega Man's charge shot or change
his basic-buster suit palette with a mushroom.

The source has separately acquired **Super Arm, Metal Blade, Hard Knuckle,
Pharaoh Shot, Charge Kick, Flame Blast and Water Shield**, with weapon energy
and selection. These are now individually acquired and selectable. Each weapon
has its own 112-unit energy supply. Energy Balancer becomes available after a
weapon. The first post-damage mushroom restores the powered form; the following
recovery flower restores the saved inventory. Native inventory tests cover the
whole sequence without injecting upgrade ownership after the starting fixture.

The seven weapons have source-derived costs, pools and primary motions. The
Bass audit now covers world/HUD pickup pixels, small/big energy drops, exact
NSF effect choices, the Water Shield clip adapted to DPCM, all flame contacts,
Pharaoh following/low-stock release, star ammo and armor reflection/piercing.
Full source/hardware parity remains unverified; see `docs/qa/bass-inventory.md`
for precise evidence and the NES palette/audio constraints.

Primary inspected classes: `Bass`, `characters/base/MegaManBase`, `Link`,
`Samus`, `Simon`, `Ryu`, `Sophia`, and the older hosted character classes.

Scrooge is a native DuckTales addition, not a 2.02 character. Luigi is a Select alternate at Mario; Scrooge occupies his former portrait slot. See [the implementation and validation ledger](../qa/remaining-inventories.md).
