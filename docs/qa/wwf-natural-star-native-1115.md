# WWF natural Stars: current Downloads checks

These ordinary-controller Mesen runs use the installed Downloads ROM
`7a80f0f37e316436be0825bbd6fd9d372af6b0b7741f84ea87356282033d9b79`,
default Easy, hardware sprite limit and deterministic cold boot settings.
They earn the actual Mushroom and Flower, complete each 60-update interval
and 25 later wrestler movements, then approach the authored Star block at
world X1616/Y144. No gameplay state, item, health or position is seeded.

Root runner: `tools/audit/run_wwf_star_current_native_1115.py`.
The frozen uniform source factory is
`2cfb4f215c16b53e466c23c2f0339f9d9d0d5e85d964316ede5de4a48525e8c8`.

| Identity | Main returns / video frames | Native receipt SHA256 | Result |
| --- | ---: | --- | --- |
| Hogan | 3094 / 5818 | db6e69abb259dc520df431d661fec35f3345efa49284dc3b2d8db09168cc75ca | PASS |
| DiBiase | 3204 / 6025 | fedfaa39bc1de7e63690e4ac95f794801567852ac148229235a9f4920796e1e7 | PASS |
| Bigelow, original policy | 2883 / 5240 | a7fde09808c3b909c94282f68f7f894c7c6dbab50f3ee0f3f384e6ed8b3c3898 | Retained negative: gap death before Star |
| Honky Tonk Man, later edge | 3424 / 6453 | 965b8ed28cfeb945efc398d2f88e7eb7bf151530edb6a10fb065179a15ccb000 | PASS |
| Savage, original policy | 2917 / 5236 | 24f6fe8def09aa61f0b0f485a0896e7e126608107f312a683537996abb2a9396 | Retained negative: gap death before Star |
| Bigelow, later edge | 3182 / 6022 | 97d1f350bc734c4ba2a80949e6056756ef23f08437550bf00855db0b2541eb24 | PASS |

The passing runs observe the mature Star's physical collector, actor
erase, popup6/timer48, actual Star timer35, music64 and sound32 producers,
1000 added score and exactly25 later wrestler movement calls. All retain
power2/lives2. Hogan ends at1647/176; DiBiase at1657/176 and Honky1649/176.
Honky and the later-edge Bigelow each record ten actual carries by the
existing horizontal helper40. Bigelow ends at1656/176.
This verifies the
sound producer, not a listening review. Expiry and protected contact are
separate gates.

Bigelow's Mushroom and Flower both pass, with Flower recovery/+25 complete
at Main2515 (1236/112, power2/lives2). The original policy requests the gap
jump at Main2662, then reaches death at Main2732 (1400/243), while native
horizontal helper40 exists at1405/208. The assertion finishes at Main2883.
The same policy had passed the source model; this native timing difference
is retained. The later-edge controller then passes natively without changing
the existing helper. Its factory is
`cd3e0f19001abb96aa8f1ba0d77addba6aa293b9093633fb737d1c4404d98e20`,
Lua`33e3288072ee95025c9a0ac0f1958ba0cfad6a48423d8c717db87648638c05b6`.
First carry: Main2745, player1413/176, actor40/slot5 at1400/208,
passenger5, actual B683/SP237. The Star is born3061, mature3128 and
physically collected3156; score2900 becomes3900. Exactly25 later movements
finish at Main3182 with power2/lives2.
Savage's original policy also dies in that gap (1399/243, lives1/power0),
after the genuine Mushroom and Flower transactions pass. The batch stops
on that negative, so it does not execute Andre. Later-edge successors for
these identities remain separate from the frozen original controllers.

Each run preserves the installed ROM, private candidate and sidecar guard.
No capture files, videos, extra ROM copies, helper placements or game bytes
are produced. The shared root emulator queue and bounded two-file output
slot are retained. Full stages and Hard results keep their separate scope.
