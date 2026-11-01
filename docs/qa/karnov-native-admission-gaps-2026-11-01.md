# Karnov admission blockers after the native opening

Candidate `f1fadebcf755a5cff09f8857ed054ecff3897ed4e804e8e88e690a2669cc43ee`
passes the cold menu and opening route. It must remain private: that route stops
before enemies and pickups. The following were found by an independent agent's
read-only source tracing and eight in-memory linked endpoint checks. They are
not a native combat replay or a separate frozen test packet.

| Boundary | Current behavior | Required connection |
|---|---|---|
| Injury status, service6 | `KrReject` returns the incoming A. `GuestInjuryStatus` therefore reports A0 even with `PlayerStatus=2`, and A89 even with status0. Actual `InjurePlayer` enters death engine11 with `MmDeathFlag=1` and speedFC. | Return genuine source health/status; consume injury through service5. Native `PlayerStatus` alone is not Karnov's health. |
| Death start/update, services7/8 | Real `PlayerDeath` with engine11, timer80 and Y160 reaches rejection and makes no movement/cleanup. | Connect source death setup and native death progression before allowing an enemy encounter. |
| Pickup maturity/collection, services23/24 | `NrPickupCollision` rejects an emerged mushroom or star; `NrPickup` leaves the enemy object active. | Add actual mature-item admission, collection and source gear/health/option effects; consider service20 tagging where needed. |
| Stomp impulse | `MegaManBounceVelocity → GmStompGate → HuBounceOnly/service27` enters `KrPostTerrain`. The next source update overwrites a native-only impulse. | Give source rebound a distinct boundary from post-BG reconciliation. Audit shared service meanings before assigning rows: service27 is already the public bounce-only route. |

The ordinary head/side/feet boundary and post-BG reconciliation already have
separate CPU coverage. They do not supply injury, pickups or source rebound.
Retain source clock/order, R2..R7, complete cache authentication, both mapper
shadows and all shared SMC operands. Live Main currently has only12 stack bytes
of reserve above the SMC area; requalify it after adding callbacks.

The additional20-case receipt in `karnov-ui-boundaries-2026-11-01.json` checks
actual inventory support, UI/HUD, `NrFullPower` and `NrUi`, cold/initialized and
Easy/Hard. Those paths avoid legacy12-owner index leaves and keep their ammo and
ownership records unchanged. The real cheat ingress already calls guarded
`NrFullPower`; Karnov's full-power action is currently an unsupported no-op.
This is safety evidence, not an implemented upgrade.

The eight extra traced endpoints also reached none of `InventoryIndex`,
`InventoryGrant`, `InventoryRemove`, `InventoryHasRaw` or `CheatsInventoryMax`.
Those raw leaves are intrinsically unsafe for runtime34 and must stay outside
future adapters. No additional active legacy-array overflow was demonstrated.

Combat/projectile block effects, earned options, health, source audio, swimming,
scene transitions and full1-1/shortcut/item runs remain before admission.
The installed nightly still has85 playable identities.
