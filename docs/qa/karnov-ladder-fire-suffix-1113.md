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

This separate controller starts from exact frozen7d1 / public7ef. Only after
the genuinely activated Bomb has blasted and retired does it use ordinary
Select to return to FIRE255. During the four-item suffix, Goombas only become
low-shot targets when they are in front,21..99px away, and their whole native
crouch-height corridor contains no solid tile. It faces right once, then
holds distance and pulses fresh crouch-B. It does not chase actors behind
the hero or through masonry. Other enemy types use ordinary traversal;
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

Actual source qualification is pending. There are no ROM/state writes, new
helper allocations or generated output roots; root owns Mesen qualification.
