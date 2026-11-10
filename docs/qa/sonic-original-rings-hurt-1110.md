# Sonic Master System rings and injury

The original SMS game stores rings in packed BCD and clears the entire count
on an unshielded hit. It allocates one animated loss object when a slot is
available. That object controls a separate damage-inhibit flag and has no
collection branch. This trace separates those source rules from the installed
SMB pickup and injury policies.

## Donor instructions

The byte-exact reconstructed `s1.sms` has SHA-256
`6ad738965ece231427ee046b9905cfee470d5c01220afdd934da4673e4a2458b`.
The checks execute its Z80 instructions. Audio RSTs expose the actual cue,
the sprite handoff exposes the actual draw inputs, and enemy attack selection
stops at the original explosion entry.

| Behavior | Donor routine and verified result |
| --- | --- |
| World ring | `01:4C28` reads the original layout at X+12/Y+8. It recognizes the masked ring tile range `$79..$7F`. `01:4DEF` rejects when Sonic's Y is less than scroll Y+16, selects the left/right ring bit using X+12, clears that bit in the original tile and starts a six-update sparkle. Re-querying the same bit does not award it again. |
| Count and life | `00:39AC` adds packed BCD. Ring tiles pass `$01`, while the monitor and signpost pass `$10`. At 100 it subtracts 100, increments lives and queues SFX `$09`. Otherwise it queues SFX `$02`. |
| Enemy contact | The original Crabmeat caller `01:66B2` runs `00:3956` overlap and `00:35E5` contact. Roll bit 0, air-spin bit 2 or the invincibility monitor flag select the original explosion. Walking overlap can hurt Sonic. Ordinary descending contact is not itself an attack test in this caller. |
| Damage | `00:35FD` rejects while the loss-object flag, stun or monitor invincibility is active. Shield consumes shield and starts stun while retaining rings. Otherwise positive rings become zero and the first available of 31 object slots receives type `$55`. A full pool still loses the rings and enters stun. Zero unprotected rings reaches `00:3618`, queues death music `$0A`, writes Y velocity −6 and starts the 96-update restart countdown. |
| Hurt motion | `00:367E` sets Y velocity −4 dry or −2 wet and X velocity ±2 against facing, suppresses input and queues SFX `$11`. `01:510A` clears both attacking flags during stun. `01:51BC` sets injury width 28 and animation `$10`, then clears stun and X velocity only when grounded with nonnegative vertical velocity. The original facing-left branch also sets actor bit 4 after choosing the vertical speed. |
| Lost ring object | `01:7B95` uses Y velocity −4 at spawn and adds `$20` per update before `00:32E2` integrates full 24-bit coordinates. X stays fixed. Alternate ticks expose the original animation and body override. The object sets `$D209.0` while updating and clears it upon despawn when its old integer Y exceeds scroll Y+256. |
| Object activation | `00:31E6` refreshes four object slots per tick. Each slot is considered every eight ticks. Type `$55` has wide camera bounds at `$2E4A`, with an effective 2,042-pixel left margin because six `LDI` instructions decrement BC before the comparison. This scheduler is separate from the object's Y-based despawn. |
| Monitor invincibility | `01:5D1A` sets its independent `$D208.0` flag and `$F0` countdown, then queues music `$08`. `01:4FF5` decrements every fourth source update and restores area music when the countdown reaches zero. The aligned test spans 960 source updates. |

The instruction checker passed 600 award cases, two actual award tails, 576
tile cases including 112 successful pick-and-requery pairs, 240 injury cases,
300 Crabmeat contact cases, six stun cases, eight invincibility phase cases,
two protection monitor tails, five integrated loss-object arcs and 64
activation cases. The dry loss object spawned at Y176 with scroll Y0
despawned on its 81st object update. Other tested positions lasted 4, 65, 70
or 101 updates. Those are direct scheduled object fixtures rather than an
overall fixed invulnerability duration.

## Current native host seams

The native trace reconstructs the exact delivered d254 image. It uses real
authenticated raw43 code and native routines. The item fixture prepares
explicit mature actors after a genuine menu-to-X80 opening.

| Host path | Current ABI and implication |
| --- | --- |
| Enemy collision | PRG126 `$9659` performs native overlap. PRG127 `$EDB1` exposes the typed body callback before native stomp/injury. Raw43 row 11 at `$D121` currently sets `GuestBodyNoStomp=0` and returns C0. A future original attack adapter needs its own roll/air-spin/star and enemy eligibility tests before using a native defeat transaction. |
| Damage protection and status | PRG126 `$976C` checks `CheatsInjuryTimer` before `ForceInjury` at `$9771`. `GuestInjuryStatus` reaches raw43 row 6 at `$D112` through `HuInjuryStatus`. Current row 6 returns `PlayerStatus`. A zero A result takes the native death route. Existing native protection is reusable as a host guard, with separate original stun and loss-object lifetime for a faithful port. |
| Powered damage | The caller loads raw ID 43 before the typed row 5 call. Row 5 currently returns C0 with caller A43. Actual PRG126 `$97A2` checks carry and `$97A4` stores A to `PlayerStatus`. Both directed powered tiers consequently become 43 and enter engine 10. Tier 0 enters native death. `InjuryTimer=8` bypasses this path in all three tiers. The isolated tier correction belongs to its own component. |
| Native item actor | `PowerUpObjHandler` advances emergence before `NrPickupCollision`. The current raw43 maturity route accepts the directed kind/state cases with C1. Actual `HandlePowerUpCollision`/`NrPickup` reaches `MarioSourcePowerupCollision` for all four native items in this build. The directed trace does not reach `HuPickup` row 24. The existing row 33 handles the 60-tick native mushroom/flower transition. Star sets the native timer to 35. A 1-up uses native floaty 11. |
| Native coin tile | PRG126 `$9D51` (`ErACM`) takes the native R6/R7 buffer pointer and R2 row, erases the metatile and invokes native visual removal. `$9D2B` (`HandleCoinMetatile`) additionally increments the block 1-up tally and calls native `GiveOneCoin`, which also awards 200 score. The erase transaction is a reuse candidate after an explicit authored ring tile and graphics policy. The SMB coin economy would change the source ring rules. |

The existing typed status, injury, body and scene entry points provide
potential hooks without adding a new shared dispatcher. A faithful port
still needs an explicit owned ring record, the tile and sprite representation,
world placement rules and owner/lifecycle evidence. Source address `$D2AA`
does not identify a host RAM lease. The delivered metadata and source motion
packet remain frozen for this investigation. Native mushroom, flower, star
and 1-up semantics are independent of future ring or monitor policy.

| Bounded checker | SHA-256 |
| --- | --- |
| `tools/audit/check_sonic_sms_ring_hurt_donor_1110.py` | `749ceaf9ce4057968096ec090a67f18168bab073577e75e79a7c01f55c7ea5bb` |
| `tools/audit/check_sonic_ring_host_boundaries_1110.py` | `45116f6a9c3d86015670600e61c26ef7512486feac9ff06021919b8995324cab` |

Both checks used the bounded runner with zero outputs. This investigation
changes no installed image and adds no helper platform.
