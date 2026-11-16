# Celeste current natural Flower and earned dash

Source only, exact actual ROM
`00bb2664647a4ef47b5dfa01c96d50549581d215a33d19a2a6390d1e09078e21`.
Grant `allocations/celeste-flower-source-root-1116.json` SHA256
`52a351d5d8900a47db049ddcb30806ae4b96b643a2140757af3d44c36120b06e`.
No ROM, game-byte, helper, native, art or physics change. Native is pending.

The existing strict facade `current_celeste_stock_00bb_1116.py` remains
`aba431470999e0335343ec6dcbce3cd1e64d80ab627cfb82fd1afbe1659e85c3`.
The frozen stock factory1b77, template9b961 and S/L factory3c9 are unchanged.
The actual compiled Mario Select6 cycle reaches Celeste variant4/raw0/CHR130.
Cold transport reads all8192 resident host bytes before host BB9A/SP231 and
all3595 core bytes before B018/SP226. There is no WRAM packet or cookie.
The source menu's missing real vblank remains a source-unit limitation; native
must execute the real frontend and independently wait16 returned updates.

Only the two named immutable input members are read from the existing compact
packet, compared against the current source copies, and inlined:

| Input | SHA256 |
| --- | --- |
| celeste_upgrades_11_v8.lua | `3c9415034d4eb234c232e67e0be0746ed3429771acbdb38f6758701a0a6fd098` |
| celeste_small_upgrades_11_v2.lua | `f4901ec32452b16791673b242e8fc629dec65de42f16fc6a433a38dddf8bf35a` |

They use the previously authenticated nav/policy/Sunny closures. No old mutable
runtime/default-build call, extraction, historical game image or graph restore
is used. Canonical current native symbol metadata is reused read-only.

## Original pickup and dash contracts

Actual CmPickup B369 retains X and consumes M/F with carry1, increments tier
to at most2, publishes native status, erases the actor and emits cue32/popup6.
Celeste remains PlayerSize1 at all tiers; no hosted60 growth freeze is imposed.

Actual CmWeapons requires fresh B (or its original4-update buffer), tier2,
engine8, cooldown0, nonzero high-Y, nonwater area, State<3 and stock1. It consumes
the stock, sets State6/native state1, Ready4, Timer12/cooldown12/boost12 and its
original cue. CmDash then selects direction and performs original movement.
The test proves immediate consumption separately from any later legal refill.

## Frozen first policy negative and first injury cause

`replay_celeste_flower_00bb_1116.py` SHA256
`84f7b18bf4d97d18d8f47bf024d8e3ef2f2757ca15f8c1b10ced88ca6a11b1b6`,
LF Lua `fb734f661682915d3a413b873c8f934a51a254f20ec298ffff536652f372952a`,
source receipt `268209fa7c65202bc186135396d5a6ec20e2156c9c9eb2658cc82f76cd3f142f`
is a combined F/dash negative. Genuine Flower/credit/+25 already passes, but
the inherited v8 travel continues until tier is lost, then eventually requests
B at x2661/176/tier1. The strict tier2 dash admission rejects that request.
No dash entry or stock consumption occurred.

Separate same-input loss probe factory
`7040c6bb5a07004350bbdac8ed8831fc3aa46f2a3ff27d631abc8c5209cb5e52`,
LF Lua `02c094dd221b4721121994dd699f6ce7393f805408b4aad60aeea09b1325358c`,
diagnostic receipt `5ae1ebd7bbea1ee75cdc148b87c8126a2eeda7c3457db157b49635a9a0c3d913`
stops on the first real loss. At Main1882, hero2013/176 walks Right into live
Goomba slot4 at2021/184. Actual boxes [115,198,125,210]/[123,198,133,204]
overlap3x7. ForceInjury9771/SP243 reaches CmInjuryStartB3A3/SP230; the original
DECCmTier atB3A8 reduces2→1 and InjuryTimer becomes144, lives stay2.
All1883 owning entries/returns balance. This is real enemy damage in the input
policy, not a dash/game regression. The diagnostic itself is not a game pass.

## Local ordinary-control successor

API `replay_celeste_flower_local_dash_00bb_1116.controller(raw,'flower')`,
`metadata(raw,'flower')`, `family()`.

Factory SHA256:
`528c17f0896d79744058ea6941d41b13f2c600d832629b4141ec16b34a646179`.
LF Lua:
`05b6e7c41db900ab6bc8827ee4d83136bdd761483ba945b385af0a7a1a5ec976`.
Checker `check_celeste_flower_local_dash_00bb_1116.py` SHA256:
`3d36be2dfcbc5b470a12b62c678bf105917bd37f2c8a002132058910c4ef6c00`.
Source receipt:
`d5cbf7bae21b50471af344002d72569b8b67da543e73cb4a1134f0230c36aeb2`.

This preserves all inputs through the real Flower's credit and25 returned
updates. Genuine M is born163/mature230, actual9B28/SP243 collector461 sees
hero285/174 against M296/184, overlap1x12. CmPickup C1/native fallback0,
erase/cue32/popup6, delayed DEC897C/SP245→83D6/SP247 credits0→1000 at466.
Exactly25 returned CmMovement/postBG/clock finish at Main492/82BE/SP252,
285/176/tier1/size1/lives2.

The real Flower is born1069 at1248/136/state1 and matures1134 at1248/119/128.
The v8 enemy guard, jump and actual wall-grip controls reach the mature actor.
At9B28/SP243/Main1430, hero1249/99 versus Flower1248/119 has inclusive11x4
overlap. CmPickup returnsC1 at016E/SP234, tier1→2, fallback0, erase/cue32/popup6.
Real delayed score writer at1435 gives1200→2200. Exactly25 returned movement,
postBG and clock updates finish Main1461/82BE/SP252 at1249/112/size1/tier2.
The capped early head-query samples precede block contact and are not offered
as the actual birth-causing head witness; actual actor birth is observed.

Only after that endpoint, new ordinary inputs step left off the row, land
1173/176 at1502, release and brake at1170/176/vx0 at1508. All eight queried
floor/head cells x1170..1282 in16px steps are84/0; the current nearest-enemy
check rejects any enemy within96. Fresh Right+B then reaches actual CmWeapons.
Return016E/SP237 observes stock1→0, State6, Timer12/Ready4, size1/tier2.
Eight actual CmDash B802/SP220→B1AF/SP222 returns include three6px steps,
1170→1176→1182→1188:18px original horizontal motion.

At completed Main82BE/SP252/1517, hero1188/175 has size1/tier2/lives2, stock0,
State6/Timer10. All1517 Main, CmMovement, postBG and clock counts balance;
56 post-F CmWeapons and8 CmDash entries/returns balance, and every pending
transaction is clear. This endpoint is during a real dash, not a grounded or
full-stage claim. Source and future native counts must remain separate.

All producers used absent `build/celeste-natural-flower-source-1116`, max1file,
600s, with write/native traps and zero generated files. Last source handle9363
is terminal. No Mesen, ROM, patch, release, capture or backup output occurred.

## Root native follow-up

Root reports actual Downloads00bb run26052 passed independently, receipt
`083deff3a20a0d3a2fe10f6a2e5d8c8acf8729348c7ab12c84b2566ed52782a4`:
1844 completed Main,1530 original owners,1856 physical frames. Real mature
Flower contact11x4/C1, tier2, actual1000 credit and25 returned owners finish
at1788. Fresh B consumes stock0, State6/Timer12/Ready4; eight returned CmDash
calls include three6px steps=18px. Final1188/175/size1/tier2/lives2.
These native counts are separate from source1517. Root owns the authoritative
native QA and current checklist; this addendum records the supplied outcome.
