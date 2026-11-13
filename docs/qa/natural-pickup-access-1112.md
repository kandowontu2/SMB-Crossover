# Current natural pickup diagnostics

Installed ROM remains `cebb0ae64b4e6cc92e473a239cb8fd4011d54cfd5e6814013a3afbd2de2bf7d7`.
These are negative controller-only Mesen observations, not completion receipts.
No emulated state writes, screenshots or capture files. Root queue is idle.

## Prince

Updated `replay_prince_first_pickup_1112.py` to authenticate the current packet
instead of the stale464c8 pin. It now observes the genuine fixed head consumer
entry and its actual caller return address, including returned tile and DY.

Runout360, face right, Up80, observe280, top-walk:476 head calls and476 returns,
all tile0. Native head layout is PlayerSize1/index51/Yadder1. No item spawned.
Prince climbed the left edge of the first brick row and walked to X383/Y112,
HP5/lives2. Receipt `e2ae9dee51bff2370306d92dd70a60ff2f2e0dfd42857ab1543dcc9df4517f40`.
Runout390 instead ends X425/Y176, HP5/lives2;424 calls/returns all tile0. Its
Up action14 transitions17/49 rather than climbing. Receipt
`70dba5e68b5c49231555b1de0cdbf310eb8a3d908041caf55fc5defc3cd91597`.
Thus the observed failure is not an omitted native head call. A reach/contact
solution still needs source/pose evidence; no jump physics were changed.

## Metal Storm

Added `replay_metal_current_1112.py`, adapting retained historical controllers
to current symbols and stdout receipts. No archived dependency extraction.
The historical armor controller loses a life at X280 on this current build.
Holding B makes that approach survive; it then fails to release any item.
Stationary jump targets256 and336 both return to ground without a powerup.
At target336, X340/Y170 is observed before returning to Y176, whereas the
opening jump in empty space reaches Y106. Final position X428/Y176 is the
first pipe, with both lives intact.

Final instrumented target336 run:83 native head calls and83 returns, all tile0;
zero observed native PlayerHeadCollision entries, no spawned or matured item,
armor0/status0. Receipt
`ce147bfb35a5477cbf4cacc3cef4f4c853bf41253f74ae41192b3a12a49e535c`;
controller `3f73a8ba44783f651470d5e13b734beed856d8c48c030ff90c44737557927a5b`.
This suggests source ceiling collision resolves before the native bump sees
the block; it is not yet a proven root cause. The helper is auditing the
source/native block-effect bridge while closing separate flower pickup tests.
The flower grant alone does not fix natural block acquisition.

Storage: removed only root's Prince candidate after confirming byte equality
with installed Downloads. The two active diagnostic directories each retain
one controller, no ROM or capture. Historical v42 Metal controllers were read
in place. Current release remains verified cebb0ae6.
