# Current590 WWF ordinary powerup checks

These checks use the default Easy setting. Hard-mode behavior and audible
audio output are not certified here; each later section keeps its ROM pin.

Root79649 runs Hogan on actual Downloads590 with Lua
2ea835ed05463ddefe8e907dc464a77822ee457160a2aeb894d74072cf823165.
Factory ce286247d8663878373fd144a0053d8a698e9b4f35fd049fd86fb855738bfe37
and template e941920234332e5a08f5fd458f19597ca03663f94927ec7e2ae9fc09e0bdac21
are frozen for this attempt. Native receipt:
0001d9fdfb35562f7d0d8401d684535953dc2aa711aeb3d985466cd8ac61ec78.

The real Mushroom gate passes. Birth is Main848 at336/135, maturity912
at336/119. Actual physical collection sees player401/176 and actor413/164
at988 prior returned Main, returnB809/SP245, carry1/erase/popup6/cue32,
engine9/active1/age0. Exactly60 native powerup-update calls recover power1
and score100-to1100 atMain1049;25 later WfMovement calls reachMain1074.

The combined M/F attempt is a terminal negative. It reaches1184/176 at
2394 returned Main/4404 physical frames, alive with both lives and score1400,
but has lost the earned armor to an ordinary enemy before its Flower
approach. The assertion requiring power1 correctly fails. No Flower birth,
collection or power2 is claimed. The source M/F passes for all six roles
remain source-scoped. This input-policy failure does not justify a game
patch or seeded armor. A new ordinary policy must retain enemy defense
through native travel before retrying.

The requested six-role native batch stops at this first failure. No native
run for DiBiase, Bigelow, Honky, Savage or André occurs in79649. The native
collector result here qualifies Hogan's Mushroom lifecycle only. General
abilities, artwork, audible SFX, performance and full-stage gates remain open.
Zero images/capture files and no ROM changes are produced.

The typed16a landing-defense successor, factoryd5b646d9/Lua360b1478,
also stops before the Flower collector: root60935 terminal negative
af6d88188406835f9662f1800cc31ab541dcf2fed0d2e2ecece7ab1cbb49c4be,
2186Main/3993physical at1242/176 in flower-align, power0/lives2. Its Mushroom
60/+25 gates pass. It retains armor longer but does not qualify the Flower.

Root85386's next ordinary policy, initial factory7e6149b7, completes its
Lua pass condition, but the Python wrapper fails while validating the
receipt: the custom Lua JSON encoder serializes its numeric-key0/1 item
table as an array containing only entry1. The raw native result is not
printed before that wrapper exception, so no receipt hash or complete
M/F native qualification is claimed from85386. The successor must preserve
numeric-key0 tables and print the result before post-run validation. No ROM
patch follows from this reporting bug.

## Current16a native M/F passes

After preserving the initial formatting failure, the successor keeps the
same controls and correctly encodes tables containing numeric key0. Its
factory is6203ea553d475bccf812e421779a25f7a09b7b73c709650fce55df6df9a181d7.
Root64263 independently passes the complete natural M/F checks for five
roles on the actual installed16a path. Each real pickup matures, is
physically collected with erase/popup6/cue32, completes60 guest updates
and25 later WfMovement calls. Both lives remain; final power is2.

| Identity | Main / video frames | Receipt SHA256 |
| --- | ---: | --- |
| Hogan | 2426 / 4458 | 071e322ef9fc65b06e86c1a3f351787f8e6bd2d18cf991799c1b048a6986509c |
| DiBiase | 2555 / 4694 | 575b0a405dc46e7141121e3f9e29b4a9637f25041dbe8057b7a68b73e38442b5 |
| Bigelow | 2515 / 4646 | e449b5a18b1db0a929dcbac2c41b75bc0281cabfcafe43f4c1d31c1198cbaec1 |
| Honky Tonk Man | 2736 / 5041 | 708f49c157da5a9effa5671cc2969089dd4bf1542d5268824dc45092cce6eeeb |
| Savage | 2549 / 4645 | 03d2814decaa199f0502499d6b3ceeed2253e1028ec784ca659766aa4a51f186 |

André is a separate terminal negative in that batch, receipt
24a09fc1f0c4ba8d6fa71c21dddc906d6e9b0c150e777eda96cf2c3f5778b903,
Lua54b824a2,1034Main/1691physical. His real Mushroom reaches the collector,
which returns with erase/popup6/engine9/active1/age0, but the assertion
reading Square2SoundQueue at return sees no cue32. That observation alone
does not distinguish an absent producer from NMI consumption before return.
A new passive write observation must resolve it; André's60/+25 and Flower
remain unqualified. No game byte is changed by these controller tests.

## André: cue production observed and both pickups qualified

Root19710 preserves the same ordinary gameplay policy and adds only a
passive observation of writes to Square2SoundQueue while a real collector
is active. Factory440bbaf77683e74e96c6c3bc9d88a337cff60a3f69f8c25c0e2642ea97c59aa6,
Lua8d82673e2d9ca4b93a92b728265f7141d9697a13aebc72f360de22bdd5aba10f.
Receipt25750237bc296f3357c443795dc42e26f7eb5599a5242a2d19b4420494b4091b
passes on the actual installed16a path:2549Main/4635physical,
1237/112/power2/lives2/score2600. Both real actors mature and are physically
collected, each completes60 actual guest updates and25 later movements.

For the Mushroom at1034 prior returned Main/frame1691, the observer sees
an actual cue32 write during collection; the queue is0 at return. For the
Flower at2463/frame4525 it sees an actual cue32 write and queue32 at return.
Thus the earlier return-only cue assertion was insufficient. This witnesses
queue production, not an audible-output test or a new SFX repair.

Together64263's five passes and19710 close natural M/F transaction and
resumed-movement gates for all six WWF roles on16a. Star, hidden1UP,
endurance/gear, all abilities, audible audio, art and performance remain
separate. Historical full-stage receipts are not promoted to16a.
