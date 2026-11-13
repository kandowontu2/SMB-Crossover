# Karnov normal-fire fifth-item suffix

Root's passive diagnostic1b998db9 returned the expected false receipt
`0ba0090d243ee0d29559e3654b69b0698fc84196f9faeb99c061fd5411808b92`.
Nav was already done/unstarted: it bypassed at physical11630 /epoch6516,
player464/128. The hero subsequently backtracked to353/176 while requesting
Right+Down+B (69), with an active slot1 Goomba at464/184. Armed=true,
Bombstate0, selected1 but owned/stock0. The ledge had been crossed; no new
platform or game-code defect was demonstrated. Frozen7d1/d6/1b9 remain intact.

The owning source options adapter tests Kr_C28C ownership before activation.
For an unowned empty Bomb it branches KrOptionsUnhandled and retains the B
pressed bit. Therefore empty selection alone is not established to suppress
normal fire. Existing actual source/native combat qualification also proves
that standing shots pass above low Goombas; original crouch fire is their
low shot. The stationary-low-fire control preserves that source mechanic.

This separate controller starts from exact frozen7d1 / Downloads7ef. Only after
the genuinely activated Bomb has blasted and retired does it use ordinary
Select to return to FIRE255. During the four-item suffix, Goombas only become
low-shot targets when they are in front,21..99px away, and their actual native
shot-center corridor contains no hard blocking tile. It faces right once, then
holds distance and pulses fresh crouch-B. It does not chase actors behind
the hero or through hard masonry. Original B also clears breakable body-height
foreground without requiring a nearby enemy to trigger firing. Other enemy types use ordinary traversal;
their vulnerabilities, collision, physics and actors are unchanged. The
original fifth pickup and complete Ladder assertions remain.

The first source candidate
`2ba46ec0db83a05a97f64d3e82a75c151ce5ee63c19dcec537e87551f978281f`
was an honest negative: four real items, normal FIRE selected1→255 at actual
epoch6414, full health/two lives, crossed353 but stopped jumping at849.
The existing ordinary traversal bound ended at9615 Main/NMI /307.91seconds.
Its last corridor rejection was Goomba916/184 behind masonry, hero849/176.
One actual native projectile contact defeated a Koopa (state0→34, popup2).
The controller had incorrectly treated all solid tiles as impassable to
shots; owning KrCombatBlock allows51 bricks,52 when MmSolidTerrain is clear,
and native bumpable tiles. That conservative control policy needs correction;
there is no proposed projectile or collision-code repair. This source version
is checkpointed as a negative, not native-ready.

The corrected predicate/controller
`1757c338caeda188c2c4447cb1d5c4bfbd5bd0f38c7d55926a70dc04f0c59540`
also remains a negative: full uninterrupted9615 Main /365.11seconds, full
health/two lives, four real items, normal FIRE and353 crossed, ending865/167.
Its actual blocker trace recorded native82 / terrain0 at864, then temporary
tile35 after one original shot activated that brick. The original combat
routine passes35/38/C2/C3/5F/60. The controller must keep these transparent
and explicitly clear breakable foreground with original B, even when no live
Goomba remains to incidentally trigger shooting. No new collision exception
or game-code repair is warranted.

A genuine four-item-prefix-derived development fork, labelled as such,
selectedFIRE but stopped at353 against hard97. Its recreated control metadata
did not preserve the original lift departure, so it was not used to claim a
new full-route defect. The retained listener was closed cleanly. The next
development checkpoint will be after the actual ledge crossing near800.

The experimental source controller is now frozen as
`replay_karnov_ladder_fire_suffix_1113.controller(exact7ef)`, SHA-256
`7d5f87b634174a4e35b282389569b5bb7059d1801d90522413e9051e33b9a50b`
(44,624 bytes). It retains every inherited item, health, life, Bomb and
Ladder assertion. The only added exception handler turns a controller assert
into a false receipt while retaining its text and current state.

Twenty-two synthetic controller component cases passed using the actual
current native MTileAttribute table and the exact source packet SHA
`ae5e53e01d7796f6d5beab97668b4f02a270c5dc60027d1cda181b6dfe11f777`.
The owning actor imports nativeY+32; original FAFD[0]=$20 and FAFD[6]=$18
form standing/crouch shot anchors. Native combat adds8 and its block center
adds4, proving standing nativeY+12 and crouch nativeY+20. Those original
centers select upper/lower native51 or non-terrain52 bricks for ordinary B.
Temporary35 is held through its native animation;35/38/C2/C3/5F/60 remain
transparent to the shot corridor, exactly as in KrCombatBlock. Native hard
97 remains blocking. There is no projectile/collision/terrain-code change.

A genuine unchanged menu/controller prefix reached800 at7136 Main with
four earned items, real Bomb use/retirement and normalFIRE255 selected. An
in-memory clone of that state passed the ordinary-input suffix in1039 Main
/88.67seconds. It recorded nine terrain-fire calls, three actual native
Goomba defeats (state→34, popup1), real mature1104/103 flower collection at
hero1106/80, SFX32/popup6/erasure and original Ladder ownership4. At1200 the
Ladder grew eight cells /32patterns, Up moved176→154, and Down restored all
32patterns/five attributes and ownership4. Terminal1200/176, full health,
two lives. The fork's only new observed dynamic helper was the inherited
1-2 collection girder left1127/center1143, initial top208, width32,82carries.
The Karnov/Rygar Select alternate/raw34 uses no new authored helper or extra
353 platform. This is explicitly a prefix-derived development proof,
not a final uninterrupted or physical-native claim.

The final uninterrupted source replay passed the exact same7d5f87b6 in
341.58seconds /8175 logical Main/NMI scheduler iterations. It used the real
menu/constructor and retained60 ordinary opening updates, then one continuous
controller VM: no history insertion, model clone, state seed or runtime grant.
The five actual collector epochs were442/1786/2898/6277/7913. Fifth collection
was native mature1104/103 at hero1106/80, slot5/state128, with erasure,
SFX32/popup6/inventory0, source cycle3/owned4/selected2. Boots were activated
at3145 and consumed naturally; the real Bomb blasted and retired. The empty
Bomb selection changed1→FIRE255 through ordinary Select at6414.

The uninterrupted model recorded nine terrain-fire calls and four actual
native fire defeats: one Koopa and three Goombas, all state→34 with native
popup2/1. Original Ladder growth reached eight cells /32 pattern cells at
site1200; Up moved176→154, then Down restored32cells/five attributes and
returned ownership4. Source cave palette2 remained21/1C. Terminal was active
1-2,1200/176, damage counter0, two lives, shot2/cycle3/selected2/owned4,
Boots/Bomb stocks0 and scene0.

The complete uninterrupted source helper observations, all existing ordinary
Up+Select actors for Karnov/Rygar Select alternate/raw34, initial top208 and
width32, were:

| Stage | Source left | Center | Carries |
| --- | ---: | ---: | ---: |
| 1-1 |1201|1217|71|
| 1-1 |1712|1728|296|
| 1-1 |1767|1783|203|
| 1-2 |113|129|71|
| 1-2 |1127|1143|82|

These are logical CPU-model observations. Root's separate actual Downloads
native proof has its own physical positions/counters: notably the first
1-2 helper is left112/center128 there. Root owns that native QA and the shared
helper inventory; this source record does not overwrite them.

Root also reported actual Downloads7ef native PASS with passive two-image
observation, receipt
`b12de68301957240b311aa34defb6b715424d369b31cbd395297ef9ae1c3a763`
/observer Lua
`f722c5b476c91c42f7d8812f52724c9b07aeee9088214dbe0d0fc905bc985657`.
The base controller remains exact7d5f87b6. Native14,891 physical frames and
8,190 controller epochs are separately reported measurements. The old4,475
normal-return counter is incomplete and is not called all Main. Native
Ladder climbing176→130 differs from this logical model's176→154; both retain
the same controls and native full restoration. Root reviewed both actual
in-memory images and writes the authoritative native scope separately.

All helper jobs are terminal, and no source edit remains pending. There are
no ROM/state writes, new helper allocations, output files or new output roots.
Root alone ran Mesen; the installed ROM remained unchanged7ef. Natural5th
Ladder coverage is now qualified. This does not qualify Karnov Star/1UP or
the remaining Clapper/Glasses/SwimmingMask/Shield equipment. GitHub releases
stay empty under the new user policy; no IPS or release was uploaded.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/karnov-equipment-1113 --resume --max-files 1 --timeout 180 -- python -B tools/audit/replay_karnov_ladder_fire_suffix_1113.py --component-check
python -B tools/audit/run_bounded_build_v1.py --output build/karnov-equipment-1113 --resume --max-files 1 --timeout 600 -- python -B tools/audit/replay_karnov_ladder_fire_suffix_1113.py --cpu --limit 12000
```
