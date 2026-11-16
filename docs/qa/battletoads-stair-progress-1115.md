# Battletoads stair control successor — November 15

Status: new ordinary controls source-qualified on privatebc5 and both actual
native full routes passed root32009. Delivery is separately root-owned and
still pending. No game bytes, physics, actors,
terrain, health, source state or ability state are changed. Candidatebc5 is
not delivered by this helper. Old C/F, fixed80
cadence bodyf769, Zitz6334 and passive1050 remain frozen.

## Actual native cause

The earlier Zitz6334 timeout is preserved in
[battletoads-zitz-stair-probe-1115.md](battletoads-zitz-stair-probe-1115.md).
Root43350 and unchanged replay71185 failed identically at x2178/y128 after
10,000 Main/10,322 physical frames, alive HP39/lives2. Root2889 then ran the
read-only passive1050 observer. It completed with the original full-route
failure, receipt
`94585faf4f400a927017998df0d2828651929b4f07989f1696744cee040ccf60`.

All9,707 actual worker entries had acknowledged returns. A/Saved mismatches
were zero, both globally and in the stair window. There were4,745 decision
transitions, four aggregate groups and zero overflow:

| Group key | Count |
|---|---:|
| `0/0/0/false/false/0/0/1/false` | 3681 |
| `0/0/0/false/false/0/1/1/false` | 5 |
| `0/0/0/false/false/1/0/1/false` | 3681 |
| `0/0/0/false/false/1/1/1/false` | 6 |

Key fields are actual worker A jumpbit / Saved jumpbit / btHeld jumpbit /
requestedA / last-setA / sourceEven parity / source-floor before / floor after /
whether returned Zspeed is zero. **No group requested or supplied jump.**

Representative actual tail: Main9994/frame10315/movement9701 at2177/128,
native state0/grounded, route phase, still0, supporttrue, obstaclefalse,
dangerfalse, jumpAge−1, lastAfalse, requestedAfalse and last-setAfalse. Held,
SavedJoypadBits and actual worker CPU A were all1 (Right only). Source before
was floor0/Zpos0/Zspeed0/Y160; after floor1/Zpos0/Zspeed255/Y161. HP39/lives2.
Across the tail, X oscillated2177↔2178 and exact-equality still reset0..3.
Both front samples at X+42 were empty; X+32 support samples stayed empty until
tile84 at Y216/232, so the original generic policy saw neither obstacle nor
unsupported terrain. It never reached its exact-X still threshold.

This is a demonstrated controller sensor/stall-detection failure, not input
loss, rejected jump or a measured game/physics defect. Source-positive routes
and the prior native negative remain separate evidence.

## New ordinary input policy

`replay_battletoads_stair_progress_1115.py` adds one progress predicate to the
existing jump condition. It applies only to char33, world0/level0, areaType1,
engine8, grounded, X in `[2160,2208)` and Y in `[112,144]`. An X/Y anchor remains
valid while movement stays within±2 pixels. More than2 pixels of horizontal or
vertical progress, airborne state or leaving the domain resets it. The17th
stationary sample can request a normal A jump through the original
`grounded and not lastA` condition and sets the original jumpAge in the same
branch. Existing hold/release logic, Right/B decisions, clear endpoint and
16,000-physical/10,000-Main timeout remain unchanged.

The policy adds no guessed collision tile, forced jump velocity, helper,
position write, health seed or state transition. It uses actual completed
movement decisions; it does not advance on idle wall time. The fixed80
literal-read cadence controller is not modified or regenerated as a new body.

Factory SHA256:
`fd22928a899457c1ce0d2b6c5e16c891eef735e47fc92d34d655dbfcbf37b752`.
API `controller(raw, 'rash'/'zitz')` accepts only exact owning67 or exactbc5,
through the existing strict typed boundary. For each identity, parent/candidate
policy bodies are byte-identical after the config line; hooks and ROM pin bind
the actual input. All old factories remain strict.

| Actual ROM | Rash LF controller SHA256 | Zitz LF controller SHA256 |
|---|---|---|
| Parent67 | `c43c13d0c706c88c155e13d1c28f0c2268dc3b40efb78385ea64c6ace0e561cb` | `756aab11e5842991de6cc6bddf7f10fd1b6c0775ee87d16dd1d99b83f21a3225` |
| Privatebc5 | `38b61529d2760e8e7999990dd6ce771bb192c310b3093457f9d7159c57ee8aa4` | `0b86eaa340cdb4263057c0fae5cfb8ca893ce89ef750ce07322be8c94a2847d1` |

## Terminal source checks

Unit/strict9119 PASS, receipt
`06b2a198964e24c66ae33a319d9c5f2a0a365670aa27bd4599f249db1ac2b840`.
The explicit controller fixture reproduces2177↔2178/Y128: no request during
the first16 samples, trigger on17. Forward/vertical progress, air and all
outside-domain cases reset without false triggering. These are policy-unit
inputs, not gameplay-state seeds or a traversal receipt. It also proves
strict wrong-input rejection, compiled LF texts, unchanged choose/setInput/
endpoint/timeout sites and exact frozenf769 body preservation.

| Source full route | Receipt SHA256 |
|---|---|
| Privatebc5 Zitz56720 | `a7edf166660e8f217a762627c4f59b4674333e7b5582c2dd3514846f6b44ce9f` |
| Privatebc5 Rash10274 | `71fb696e1983d0ce5930d1c9221087fc971b484670e42d2c231159016e740335` |
| Parent67 Zitz99166 | `02285e3842fef0a979add23dc1c84b6ce2bd010e2d62bb065f0b0b6bd2be63d0` |
| Parent67 Rash35543 | `707338674a403d804a865f66726a6dbcb014d75aefd1bf82c720c8499dcc7c7b` |

Each actual candidate run used compiled name/Select/Start, real parser and
constructor, frozen base inputs plus only the new ordinary progress predicate.
Each completed4,003 Main,2,863 BT movement calls/58 in1-2, flag2805/castle2868/
entrance3406 and25 living grounded1-2 updates at40/176/Yhigh1, HP43/lives2,
power0/Star0, actual variant0/32. Source model video/cadence is not hardware.
Source never exhibited the native2178 stall, so these positives preserve the
known route and do not substitute for root's actual new native clear.

Both same-intent parent67 source routes passed with the same4,003 Main,
milestones and terminal fields. All four parent/candidate/identity source runs
are terminal. The policy body is identical per identity after the config line.

## Root's separate actual native successor qualification

Root32009 completed both exact privatebc5 controls, with no game writes,
images or generated files:

| Actual native run | Main /physical | BT /next | End HP/lives | Receipt SHA256 |
|---|---:|---:|---:|---|
| New Zitz0b86 | 4611 /5005 | 3037 /58 | 43 /2 | `0ae6016f90cb30ce75dd38a4b5f7d37efd3cad2813160e63c112cee8c769c0c4` |
| New Rash38b61529 | 4254 /4644 | 2844 /58 | 39 /2 | `ba148da382877f4192d40f7cf548be3bf15e4c2560d5448ad2d7716db50d138f` |

Both execute the full1-1 flag/castle/entrance path and25 living grounded1-2
updates at40/176 with actual variants32/0. Rash's receipt is exactly its old
passing native receipt. Zitz's new ordinary jump policy clears the previously
observed controller stall. No physics or candidate game byte was changed.
The original6334 timeouts and passive1050 negative remain valid evidence,
not superseded game failures or erased receipts. Native health differs from
source as recorded; no source health is substituted.

Fixed80 cadencef769 remains unchanged. Root's earlier matched privatebc5
cadence gain (idle missed4/47 versus19/47, Right9/32 versus15/32) is separate
from these full-route gates and still does not establish zero lag. Root is
preparing its source push, direct Downloads delivery and actual-context repeat;
none of those actions is performed or claimed by this helper.

All source producers use absent `build/battletoads-stair-progress-1115`,
max-files1/600 seconds, aggregate stdout and zero generated files. No helper
emulator, ROM file, Downloads write, installation, patch, capture or release.
