# Rogue earned-missile contact control negative — 2026-11-16

This is a retained ordinary-input **control negative**, not a missile-physics defect. Exact owning image is cb95 `cb95eb8dff9929c8162e019d5e3f33e45b570946f5281c07584a9f11cacdba07`. The qualified genuine MF prefix and original damage1 implementation remain unchanged. No game/actor/resource/terrain seeds, helper changes, new ROM, native run, capture or generated output was made.

The initial passive target inspection38617 passes, outer receipt `ead28aed9829e81c4f6a39c7fbcc8190cf3cec079e6aec9bac5d7f16d4f61c11`. At the actual MF endpoint1793 the hero is1238/113 with missiles5/tank1; no native enemy is active. The real roof has51/C4/51 at1232/1248/1264, ending1279. The source missile muzzle1254/123 naturally has no target. `inspect_rogue_missile_targets_cb95_1116.py` SHA `f97d8694a6ba59a8a1718388d51369507cec1663d3e099b99fa5fe1c350689bb`, Lua `eadd9c829a69fa8a7182f3758acf34823ffde0a90685fcf845a4bc1fe4c0800c`.

One new ordinary policy walks off the roof, uses ground-only gap jumps and requests Select/B only for a real live enemy with an unobstructed source missile line,64..144px range and actual vertical overlap. It stops at world2000. Source47215 is negative:2415 balanced Main/Dispatch/Step/Life, alive2000/177/lives2/tank1/gear0/ammo5/max5; **no eligible target, Select/B request or missile shot**. Ordinary injuries leave raw health19h/15h. The engine receipt is `f38ef49bfbabc313bead832e3210f3463473a7d746178e8458c5745b7f714de5`, inner `acdc11353fd5954102735bc325f15ae063cdeef1d49a25bb46dc0bb094fd8a74`. The engine computes that hash before its CLI appends `policy_metadata`; it is not the hash of that augmented top-level object.

Frozen negative files:

| File | SHA256 |
| --- | --- |
| `replay_rogue_missile_contact_cb95_1116.py` | 3138fe3939392064a80049dfeb87cbbc079842b90fc2c6f1d57d9502dbdd41c8 |
| `tools/playthroughs/rogue_earned_missile_contact_cb95_1116.lua` | 0971cffe020d0a820caf83883e12eb2551d06b678028b10d404ba2d47a64cf1c |
| Generated Lua | ff59ba978f0cb3567e0bea4e39845f28610e4693451c9586c83f48f5c2c7fbf3 |

The separately frozen `observe_rogue_missile_alignment_cb95_1116.py`, SHA `8fcc11e55799f8c89a84c78582b67746c561dcfa8c84d2f7ea70cd1461a3822d`, restores that exact input body after removing only its passive aggregate. Source1247 diagnostic completes with original gameplay false, receipt `9a68dd265242083a01da6f6ae823872714f5df684fc247d6caf7cd9115964808`. The first actual Koopa is Main2025 at1712/184; its source target box is `[1714,193,1726,205]`. First ready ground context2046 has hero1547/177, source muzzle1563/187 with radius2, enemy box `[1703,193,1715,205]`, gap140 and clear terrain. Across221 real Koopa observations,189 are ground-ready,44 have the requested range,221 have a clear line, and **zero** have vertical overlap. The standing Goomba body is also below that original muzzle. This does not justify moving the muzzle or changing authorized damage1 to fit native SMB enemies.

One unexecuted observer issue remains explicit: `weaponReturned` compares mutable `RdWAnim` to91h, while a future real impact gate should inspect its reset/frame contract. No shot reaches that assertion here, so it caused neither negative. The frozen negative is retained unchanged; no broad control sweep follows.

Both producers used absent `build/rogue-missile-impact-source-1116`, max1/600s/zero files. Actual native missile motion/expiry/full-stage and the subsequent Bomb acquisition remain separate positive scopes. Enemy impact and actual terrain destruction remain open.
