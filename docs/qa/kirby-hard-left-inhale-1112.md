# Kirby: Hard-mode close left-facing inhale

Actual Mesen controller-only test on the installed Downloads nightly
`cebb0ae64b4e6cc92e473a239cb8fd4011d54cfd5e6814013a3afbd2de2bf7d7` passed.
The controller selects Hard through Options, selects Kirby, jumps past the
first naturally spawned Goomba, lands, turns left and inhales at close range.
No emulated-state writes, cheats, captures or gameplay changes.

- Physical frames: 818; health 6 and lives 2 throughout.
- Fresh left+B at frame 815, separation 13 pixels.
- Actual capture and native enemy removal at frame 816, separation 11 pixels.
- Mouth 7, mouth copy 1; no injury callback or injury timer.
- Receipt SHA256: `8fdbd98f762441fb9b1537576516674f3b8fdb7bc384e71bdd16123dccc688a5`.
- Generated controller SHA256: `b56b9e17a9ef2b93fec1063dbc289565f456e374d3eb46340c6f4339dfd87e4b`.

Replay: `tools/audit/replay_kirby_left_inhale_1112.py --variant 2 --hard`,
through the bounded runner with output `build/kirby-left-inhale-1112`.
The disposable controller is removed after validation.

This extends the Easy direction tests; it does not establish all enemy types,
underwater behavior, all copy powers or full-stage completion.
