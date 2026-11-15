# Classic DK functional 1-1 source investigation

Root's delivered current is exactcf7
`cf7b6d2964ae0ef18d08c726f66afe9bf5be3dc6f3ec9c7a43279121ee09d968`.
`current_dk_gameplay_input_1114.py` authenticates the owning Gimmick inverse
to exact1daca and strict forward roundtrip, then rebinds only image-controller
provenance and changed bank hashes. Actual runtime bytes remain cf7; the
frozen classic/common/Gimmick composition and controller APIs are unchanged.

Classic DK uses real native SMB movement and A jump. `DkMovement` calls
`DkEnsure`, clocks the authored attack and tail-calls `CrossoverVanillaMovement`.
The jump-profile routine changes only MegaMan/Luigi. Fresh B throws barrels;
earned tier2 Down+B selects a vertical barrel. There is no additional DK
jump or ground-pound movement ability to infer from the original NPC.

## Retained first-pipe negative

Session88805 completed the genuine compiled-menu three-image opening in352
source Main updates, receipt
`a2a30d36070c53d8cdff6353fd5401234f4b8a40bef22b24c535150f24577544`.
It then retained the earlier first-pipe controls: approach x396 grounded,
hold Right+A38 updates, continue Right, for250 total source updates.
Diagnostic receipt:
`c0ea82e7633ef8e876f9e01f66786c06c2b1a8f619dfb11070c8428a81c52eb2`.

The jump is genuine: takeoff x396/Y176, prior A0, native speed16/16.
The first returned jump update reaches x397/Y172, state1, VY252 and force30.
It reaches x402/Y157 on the fifth update, where VY changes from252 to0,
then descends and lands at x416/Y176. It subsequently stalls x417/418 at the
first pipe, with engine8 and lives2. Only one actual jump-profile call and15
JumpSwimSub entries occur. This rules out a missing A edge at takeoff. It
does not yet identify the instruction causing the early upward cancellation.

The initial first16/last16 writer ring missed that causal middle writer.
The subsequent same-control head-cause arm5777 retained it explicitly:
receipt `c582ed81be4a14443894542d016a7a629677ab4d8a0e91095fd812d74020646c`.
Native PRG254 PC8DC7 writes VY252→0 at Main32/x402/Y157. The actual
BillBGHeadConsumer return at9BC5 reads tile81, R2=112 (world row144),
R5=133 (the left probe at world389), pointer03D8. By the later VY writer,
world384/Y144 is tile35: the native head transaction has temporarily cleared
the contacted cell. This is an ordinary bump transaction, not proof of
permanent brick destruction.
Later empty-cell sampling alone would have missed the genuine head contact.

## Ordinary first-pipe retry passes in source

Session62476 preserves the same genuine opening and250-update negative
prefix, then supplies two ordinary Right updates with A released, followed
by fresh Right+A38. The second actual jump is acknowledged at Main252,
x418/Y172/state1/VY252, with A sampled128. It clears the pipe and reaches
x513/Y176/state0/engine8/lives2 after89 successor updates. The full physical
body is past the pipe: left500 exceeds pipe right479. Receipt:
`abbbe842dbf514e0c680fe16568893b9be23fbd324aa800e6d7a9547b955f22f`.
The first-pipe failure therefore supplies no basis for adding a helper or
changing DK's jump/collision code. This remains source proof, not native proof.

The new full-stage controller's initial strict/compile gate96390 passes on
exactcf7, rejecting truncated/unowned-byte/fa66/12397 inputs, without mutable
nightly rereads. Initial Lua SHA256 is
`1dbddab40b17764b04841e72a170bf3fd0b89ef872b38e3081126b30c764dd8c`;
policy SHA256 is
`4637f7d0946c03cb46609873e159d3c449696d3c85da31eddd0dc1937cc96c5a`.
It bases decisions on actual DkMovement followed by authenticated Main
return, caches buttons for input polling, releases A after a real early
landing and requires flag/castle plus25 actual living grounded1-2 movement
updates at40/Y176.

## First full-route source negative

The frozen initial controller above completes1058 genuine source Main returns
in session43163, with1058 actual DkMovement calls. It crosses the four opening
pipes and first two gaps, reaching maxX1522. The first terminal death is at
Main1058, x1524/Y166/state1/engine11, lives2/tier0. Receipt:
`38cf09c00be4151ebcfa9708c1efc63d53586b458503999c81eb08fe61efb549`.
The last retained waypoint is Main955/x1282/Y176 grounded. There is no
flag/castle/1-2 proof. A passive injury/contact observer is required to classify
the next interaction before changing controls or game code. This source
negative is retained; the initial full controller/policy remain frozen.

The unchanged-controller passive arm5814 reproduces that exact source receipt.
Its first actual InjurePlayer entry is PRG254:976C, Main1058, X/ObjectOffset2.
DK is x1524/Y166, VY251 (rising), speed39, source tier0. Live Goomba2 is
x1550/Y184/state0. The actual screen boxes are DK `[99,166,141,198]` and
Goomba2 `[141,198,151,204]`, with camera1412: inclusive corner contact occurs
while DK's feet are still at its head. This is contact during rising, not
evidence of a bad stomp response. DkHostDeathStart follows at PRG164:BE4D.

The preceding approach is consequential. At Main1034, x1477, DK still moves
33/16 pixels per update despite neutral input, with two live Goombas x1538
and1562. A fresh B begins Main1037; the first Goomba is defeated at Main1053
on the barrel's age16 publication. DK lands at x1517 on1055, releases A on
1056, and requests a fresh jump on1057 atx1522, when the second Goomba is
only28 pixels ahead. The next update reaches contact at26 pixels ahead.
The neutral wait therefore provides insufficient braking/reaction distance
for this42px body and16-update barrel windup.

A separate controller-only successor keeps the frozen baseline intact. It
countersteers, retreats to112px front gap, establishes actual right-facing,
then uses fresh ordinary grounded B throws while stationary against all live
front Goombas. The measured fatal overlap corresponds to DK right29 and
Goomba left3; no engine, collision size, health or helper change is proposed.
Successor2721 is a retained controller negative: it stays x562/Y176/engine8/
tier0 from Main500 through6000. The owner deliberately stopped its verified
Python process35300/parent37064; the bounded wrapper terminated1 with zero
files. There is no terminal stage receipt or passing result. The broad wait
can select an enemy beyond a pipe and is unsuitable as a general route.
The frozen wait policy SHA256 is
`1dc325e6c6b37f21bd8a0127e7dbfe671c453c0f852cf0c581b43f9b78e3182c`.
Root directs a simpler separate all-live-forward64px danger-jump successor
from the already pipe-crossing baseline. No game fault is inferred from this
barrel-wait stall.

## F11 global danger-jump negative

Downloads advanced to exactf11
`f11a25b892779cb0d5192457f7feff548f35019818cd75dfef5bdf3f2419b865`.
A new strict typed input authenticates the owning BT inverse to exactcf7;
the older cf7/1daca/Jr. APIs remain unchanged. Its first global danger64
controller is frozen at Lua SHA256
`f22845fc6ab354bb171f79b2c646dc6c7d7ba2e3fc8cd586738ad29563871906`.
Session82724 strict metadata passes, but the source route is negative after127
Main updates, receipt
`2865a031fba5303b2ac565cc7c8b685cdd84ee9ab784f2e543a6db72f71e441e`.
Replacing the neutral wait globally disturbs the previously successful opening:
first injury x299/Y176/state0 versus live Goomba x325/Y184, again at gap26
and actual boxes `[99,176,141,208]` / `[141,198,151,204]`. A is released
after an early landing. No head cause was retained for this early interaction,
so no ceiling/collision defect is inferred. The next separate controller must
preserve the proven baseline prefix through1440 and scope its reaction to the
measured paired-Goomba encounter, with a passive head-response witness.

No full1-1 clear, native playtest, new helper, game change or delivery is
claimed. Source jobs use absent `build/dk-full11-current-1114`, max-files1,
timeout600 seconds, and zero output files. Root owns the single Mesen queue.
