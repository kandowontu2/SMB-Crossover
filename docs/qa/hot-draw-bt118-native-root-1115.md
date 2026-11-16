# Battletoads shared drawing optimization: root native checks

Public Downloads remains exact `67e3b8e7d4b01ea549fe9dc15c09b5a0b5f7085ee396d672a9c963d24287d0b5`.
Private candidate is `bc5e275d1dd4dabab4b5b2def66f7643ae46aee17a31ab37887528b791594040`.
It is not delivered yet. See `hot-draw-bt118-source-1115.md` for the frozen
118-byte envelope, exact inverse, live following108 bytes, public-entry,
foreign-character, lifecycle, fault and reached-interrupt proofs.

The candidate routes Battletoads drawing directly to its existing public
renderer. The source paired public-call comparison saves499 CPU cycles per
call; it retains all three normal Main integrity checks. It changes106 of118
owned bytes, adds no capacity, RAM, graphics or helpers, and preserves every
other public67 byte. Other families retain their independently measured
source costs; this does not establish a full-roster speed improvement.

## Fixed native idle and walking comparison

Both runs use the same frozen cadence controller body, real menu selection,
zero game-state writes and no captures. They start without enemies. These
literal controller-read observations are evidence of a partial improvement,
not a claim of60fps or zero lag.

| Test | Public67 root74578 | Privatebc5 root57898 |
| --- | ---: | ---: |
| Idle missed-read samples | 19 / 47 | 4 / 47 |
| Right missed-read samples | 15 / 32 | 9 / 32 |
| Idle native NMI-skip increment | 19 | 4 |
| Right native NMI-skip increment | 16 | 9 |

Parent receipt `da42be652b380c581d995b50c9012c238402dce7bcdbb0f71f7ea132f064b2b1`;
candidate receipt `be4c190433f0a0518903f48371a3fa68a328cba438f5eb737e624372002c0e7a`.
Both complete353 Main entries/returns with final X83/Y176, HP47/lives2 and
zero actors. The source-scheduled normal Main comparison saves499 cycles
while retaining identical NMI work; that comparison is not hardware cadence.

## Full-stage native replays and retained control failure

Root43350 Rash passes full1-1, flag, castle and entrance, followed by25
living grounded completed1-2 updates at40/176, HP39/lives2, real variant0.
4254 Main/4644 physical frames; receipt
`ba148da382877f4192d40f7cf548be3bf15e4c2560d5448ad2d7716db50d138f`.

The original Zitz controller6334 times out at X2178/Y128, HP39/lives2,
10000 balanced Main/10322 physical frames. Root43350 and unchanged71185
repeat the same negative receipt
`eae3a901a9aa0cb9e0d1b227093d96ed475146e7795575181ba05e142c587d86`.
This is retained and does not authorize delivery.

Root2889 passive observer1050 preserves that policy. Its receipt
`94585faf4f400a927017998df0d2828651929b4f07989f1696744cee040ccf60`
records9707 balanced Battletoads worker calls, zero saved-input mismatches,
and four grounded stair groups with counts3681/5/3681/6. Every group has
A false. The exact-X stall counter repeatedly resets on one-pixel motion;
the forward terrain probe is beyond the nearby stair. No jump is requested
at the stall, so this does not demonstrate a swallowed jump or an engine
collision defect. See `battletoads-zitz-stair-probe-1115.md`.

New ordinary-control factory `replay_battletoads_stair_progress_1115.py`
`fd22928a899457c1ce0d2b6c5e16c891eef735e47fc92d34d655dbfcbf37b752`
recognizes17 grounded samples within two pixels in that measured stair
region. The existing A edge/release safeguards and final endpoint are exact.
It changes no game bytes or cadence benchmark. Both candidate source routes
pass4003 completed Main/2863 Battletoads/58 next-area workers, full flag,
castle, entrance and25 grounded1-2 at40/176, HP43/lives2. Source receipts:
Zitz `a7edf166660e8f217a762627c4f59b4674333e7b5582c2dd3514846f6b44ce9f`;
Rash `71fb696e1983d0ce5930d1c9221087fc971b484670e42d2c231159016e740335`.

Root32009 passes both private native successor routes under
`allocations/hot-draw-bt118-stair-native-1115.json`. Zitz receipt
`0ae6016f90cb30ce75dd38a4b5f7d37efd3cad2813160e63c112cee8c769c0c4`:
4611 balanced Main/5005 physical frames,3037 Battletoads/58 next-area workers,
25 grounded completed1-2 updates,40/176,HP43/lives2,variant32. Rash repeats
the earlier exact `ba148da3...` receipt:4254/4644,2844 Battletoads/58next,
25 grounded1-2,HP39/lives2,variant0. Both use actual ordinary menu navigation
and controls; there are no game writes, captures or output files. The new
policy fixes the replay stall without an additional game patch.

Separate direct-delivery grant: `allocations/hot-draw-bt118-delivery-1115.json`.
Actual Downloads cadence and both full-stage repetitions remain required
before claiming delivery verification.
