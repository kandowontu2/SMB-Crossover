# Metal Storm flower integration — private candidate

Parent: `cebb0ae64b4e6cc92e473a239cb8fd4011d54cfd5e6814013a3afbd2de2bf7d7`.
Candidate: `1595c7fcb6449fe20809124edbb4aa3e58fa69452c2f51bfc286485d93c6f3f7`.

The actual mature native flower now executes the original item0 grant and
retains normal erasure, score, inventory cleanup and pickup sound. It leaves
armor independent. Both source shot slots produce original type81, including
all four aim directions. The unsupported GravityFire mode remains gated.

`compose_metal_flower_1112.transform` changes86 owned ROM bytes, with checked
preimages, complete cookie updates and exact inverse. It composes with current
Prince changes. Existing extra allocation grows257→313/352 bytes; actor and
renderer allocations do not move.

Root repeated `check_metal_flower_1112.py` successfully under the bounded runner.
Checker SHA: `23b43a42a239cd40c6ed797bdfeecef38a89583fae3df7f5334d09dcc5fcc904`.
Coverage:96 native-pickup/original-grant pairs;36 unchanged mushrooms;12 Star/
1UP controls;48 immature rejections;32 full-header rejections;9 foreign-owner
pairs;22 actual public movement/donor shot phases and2 native Goomba defeats.
Three actual cold readback faults withhold both headers. Changed pickup code
passed19 IRQ and19 FF lag-NMI cuts, minimum SP166 in the direct pickup fixture.
This is not deepest GameLoop stack or nested-interrupt proof.

Root physical Mesen full1-1 route passed into active1-2 in5328 frames, lives2.
Receipt: `4d689229dd14f84a1575f87657f265a20168aa2c9b95e7c0cdb79b626edff327`.
Controller: `fdd959bee291f844257714c9963d26a28cec30c44f4a42e240701cf82a55a8c5`.
The controller earned no powerup on this route. No capture files were created.

## Required before natural-upgrade delivery

The source head contact is real but never forwarded to native block effects.
In the current parent, stationary jump X340 touches native mushroom metatile
C1 through source query X336/Y158, source velocityFA. Native Y is164 at that
moment. The source resolves the collision before the later native head probe,
which returns zero. Receipt:
`724017b601dfb33bc293a54f0ee5f03ae7ed5aba30624d8e6943ad6614900096`.

Helper source audit identifies original B856 as the head-only convergence;
feet probes enter B859 directly. B856 currently checks donor hazards then
snaps through FF36; E0 native terrain has no relevant donor hazard flags.
The planned fix records the exact head cell before that snap and forwards it
through typed HuHead row10 while retaining original source physics and native
block effects. It must reject stale events, feet/shots, changed cells and
noninteractive states. Source allocation and interrupt checks remain required.

Candidate remains private at `build/metal-flower-native-1112/candidate.nes`.
The generated controllers were removed after retaining their receipts/hashes;
their source generator is `tools/audit/replay_metal_current_1112.py`.
Downloads and Current release remain cebb0ae6. Helper is implementing the head
bridge in separate scoped files; root owns all subsequent Mesen runs.

The root replay now has `--mode upgrades`: ordinary controller input approaches
the first mushroom, crosses the four pipes, approaches the authored flower at
X1248, and requires both mature item observations plus a real type81 source shot.
On installed cebb it correctly stops at the existing first-item gap (phase0,
no birth/armor/weapon, lives2). Receipt
`c354c12ca29861861209534f773e4b79a6e39583ff008cb00d6f229ca53cff82`.
Later controller phases are prepared but not yet reached or qualified.

Refined source audit: the capture seam should be Ms_B798/current AD54, after
the source contact/distance test has actually accepted the head hit. B856 is
too early because FF36 can still reject. Preserve BA02/FF36 unchanged. The
helper is resolving the actual public head dispatch before assigning a getter.
Additional helpers are independently auditing Prince raised-hand reach and
Steve's unfinished same-pattern robot armor transformation; neither has changed
the nightly. Root's Mesen queue is free after the negative upgrade replay.
