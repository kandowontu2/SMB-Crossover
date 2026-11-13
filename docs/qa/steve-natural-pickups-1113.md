# Steve stock 1-1 powerup access

Source CPU qualification passes both authored powerups on the exact private
armor candidate
`62ba7f54117875ec018d6f85fb1c74408aa11f0fe0f6a85b8b4f601034a17639`.
The pure composer is `steve_armor_idle_1113.proposal(aa501)`. The source test
and readonly native controller are in
`tools/audit/replay_steve_natural_pickups_1113.py`. All checks use the bounded
runner and retain zero generated files. Root owns later Mesen qualification.

The test runs the actual menu alternate selection, Start and stock parser,
then waits167 updates for active1-1. It reuses the full-stage held-B and
first-Goomba fight, followed by the measured historical authored-token
controls and `replay_steve_route_1111.continue_route`. Every subsequent
gameplay update runs ordinary Main/NMI with controller input.

| Authored block | Mature native actor | Collection | HUD pattern |
| --- | --- | --- | --- |
| Left336, center344, top144 | X336/Y120, state128, token8C | Update540 at X324/Y112, health6 | Pattern1 after12 more updates |
| Left1248, center1256, top144 | X1248/Y120, state128, token8C | Update1434 at X1236/Y112, health4 | Pattern5 after12 more updates |

The first preparation enters native `JnPreparePickup` with PowerUpType0.
The second authored flower enters with PowerUpType1. Both finish preparation
as source Alpha token8C. The existing native pickup transport sets the
physical PowerUpType to1 for a stationary private pickup. Its source is
`src/mike_jones_pickups.s`, followed by Steve's existing token preparation
and collection bridges. Actual preparation, maturity, native collection,
actor erasure and HUD flight all occur in this route.

The first launch uses approach329, seven neutral updates, nine A updates
within62 total reveal updates, return302, nine neutral updates, then nine
A+Right updates followed by Right until collection. The second uses
approach1239 and return1214 with the same timings. The route crosses pipes
448–480,608–640,736–768,912–944 and gap1104–1136 with original movement.

The Goomba fight awards native score1. Both native `JnPreparePickup`,
`JnCollectPickup` and `HandlePowerUpCollision` execute twice. Total gameplay
length is1,446 controller updates. Terminal state is X1240/Y112,
health4/lives2, original pattern5, pending flight0, robot0 and armor0.

One actual enemy contact reduces health6→4 at update1,406 during the second
collection jump. Native `JnInjury` receives Goomba slot1/id6 at X1215/Y148
while Steve is at X1211/Y157 and ascending. Health6 was retained through
traversal and the second token's maturity. The test records this injury and
the resulting native health write.

The pure `controller(candidate,info)` API derives its readonly Lua from the
frozen full-stage replay, preserves the tested first-Goomba sequence, adds
left input for the collection approaches and checks all three current owner
headers. It observes actual native preparation and collection and requires
both authored actors to be erased before finishing. The compiled Lua hash is
`82ace2fe3ead540390e5a0eb3dd5c9003461238fba925a686fdd5aa7d9a465a6`.

`--lua` runs this exact Lua's active-game decisions against actual CPU
Main/NMI. Actual menu/parser ingress occurs before skipping the Lua title
navigation. OAM DMA is modeled from each actual native DMA write. This gate
passes1,446 updates,1,446 movement projections, two native preparations,
two native collections, pattern5, health4/lives2 and36 matching DMA cells.
Its CPU-bound Lua hash is
`8f46b53608f9a4a9ae14c923c2089c43a005b7052421e472db935157b2c25c24`.
Physical cadence and raster qualification remain with root's Mesen queue.

Both checks operate on the unmodified stock-level62ba image. The test
supplies no runtime position, actor, health, pattern, robot or timer seeds.
It adds zero helper platforms and changes zero ROM bytes. The frozen armor
qualifiers, root candidate/controller and default2aa proposal remain as
previously qualified.

Reproduce the direct controller test from the workspace root.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/steve-armor-transport-1112 --max-files 1 --timeout 300 -- python -B tools/audit/replay_steve_natural_pickups_1113.py
```

Exercise the exact generated readonly Lua with the CPU model.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/steve-armor-transport-1112 --max-files 1 --timeout 300 -- python -B tools/audit/replay_steve_natural_pickups_1113.py --lua
```
