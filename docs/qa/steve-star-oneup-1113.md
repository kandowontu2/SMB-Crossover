# Steve Star and 1UP effects

The source CPU semantic fixtures pass on installed image
`62ba7f54117875ec018d6f85fb1c74408aa11f0fe0f6a85b8b4f601034a17639`.
The checker is `tools/audit/check_steve_star_oneup_1113.py`. Each fixture and
the unprotected control perform actual cold/menu/Start/parser ingress,
reaching active1-1 after167 updates. All producers use the bounded runner
with `build/steve-armor-transport-1112` and generate zero files.

The two declared pickup fixtures place native actor46 in slot5 at X40/Y183,
relative to Steve's genuine starting X40/Y176. Native `PwrUpJmp` and
`UnionPwrUpCore` initialize the actor, box control3 and ordinary
NrPrepare/JnPreparePickup transport. The test then explicitly supplies the
mature actor state128 and ordinary foreground attributes. Main/NMI builds
the real boxes, detects overlap and calls HandlePowerUpCollision and the
native collector. Both actors are erased during the first update.

The fixture supplies no player position, source health, weapon, pattern,
robot, armor, freeze or timer values. Native preparation retains the genuine
source inventory. Both prepared actors retain native transport tagFC and
receive the ordinary native Star or life grant.

| Effect | Measured native result |
| --- | --- |
| Star collection | Star timer35, area-music request64 and pickup sound32 |
| Star contact | At update189, native ShellOrBlockDefeat defeats the actual parser Goomba, retaining health6 |
| Star expiry | Every timer value35→0 occurs, with expiry at update716 and ground-music request1 at652 |
| 1UP collection | Native floaty control11, followed by lives2→3 and sound64 at update6 |
| 1UP continuation | Exactly one life award across71 Main/NMI updates, retaining health6 |

For the Star contact, Steve is at X290/Y176 and the stock Goomba is at
X301/Y184 with native box control9. Star timer26 is active. The actual native
defeat sets state34 and awards score1. Ordinary Right is the only movement
input and B is unused. The corresponding control reaches the same contact
coordinates without a pickup fixture and executes JnInjury at update188,
reducing health6→4 and setting hurt60.

The Star case invokes GetAreaMusic once during expiry and writes music
requests64 then1. The 1UP case reaches the ordinary deferred native floaty
award. The sound and music findings concern native queue requests and their
Main/NMI continuation. Physical audio, cadence and raster qualification
remain with root's Mesen queue.

Both successful effects preserve tier1, selected weapon0, all ten ammo
values0, source pattern0, pending0, robot0, armor0, upgrade state0, native
status0 and freeze0. Star retains both lives. The 1UP retains its third life.
The tests add zero helpers and change zero ROM bytes.

Reproduce the fixture semantics and ordinary-contact control.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/steve-armor-transport-1112 --max-files 1 --timeout 300 -- python -B tools/audit/check_steve_star_oneup_1113.py
```

The natural stock route also passes after the semantic measurements. It earns
the first Alpha336, hidden1UP1024, second Alpha1248 and Star1616 in2,027
ordinary Main/NMI updates. Each authored actor is revealed, matured and
collected by the game. This route supplies zero runtime state values.

The hidden block has left1024, center1032 and top128. Steve reveals it from
X1021/Y176. Its 1UP matures at X1024/Y103. After34 chase updates, collection
occurs at actorX1058/Y164 and playerX1059/Y176, at update1,252. Native life
award and sound occur at1,257. Health6, pattern1 and all three lives remain.

The authored Star brick has left1616, center1624 and top144. It is revealed
from X1613/Y176 and matures at X1616/Y119. Straight Right outruns the native
actor. The passing controller instead follows eight pixels behind its
observed world X, with a four-pixel deadband. Collection occurs after85
chase updates at update2,003 and requests Star35/music64. After24 further
Main/NMI updates, terminal state is X1693/Y176, health4/lives3, pattern5,
robot0, armor0 and Star34.

The natural route includes native enemy damage and native drop healing.
It does not assert an injury-free run. The two Alpha grants preserve their
ordinary pattern1→5 behavior while Star and 1UP retain their native effects.
It crosses the four early pipes and the first two pits with the installed
source movement. No helper or physics changes are needed.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/steve-armor-transport-1112 --max-files 1 --timeout 300 -- python -B tools/audit/check_steve_star_oneup_1113.py --natural
```

A readonly four-item Lua binding and complete input-stream comparison are
the next source gate before root's physical test. The compact CLI receipt
keeps fixture semantics and natural-route results distinct.
