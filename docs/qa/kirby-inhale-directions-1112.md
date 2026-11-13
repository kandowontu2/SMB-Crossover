# Kirby inhale direction checks on current nightly

ROM: `cebb0ae64b4e6cc92e473a239cb8fd4011d54cfd5e6814013a3afbd2de2bf7d7`.
All four runs use actual Mesen, cold menu selection, default Easy, no cheats,
ordinary controller input and the naturally spawned first Goomba. All finish
with HP6/lives2, no injury, mouth7/copy1 and the actual enemy erased. This is
first-Goomba coverage, not water, Hard or every enemy type.

| Direction / start | Frames | Capture | Receipt SHA256 |
| --- | ---: | --- | --- |
| Right, medium | 511 | gap11, action age0 | `05e7a4566586a59f73ccf4a8ff600b526bc5a599d177fd25c975a3019e3589cb` |
| Right, close startup | 527 | gap9, age7, one frame after fresh B | `4b057d9eea5160b1d63b021bbe2d50b32ee41ded269c0682a28f7123a8aaf7e3` |
| Left, medium | 736 | gap11, age0 | `377256f2c5cd829440300c084d11def25fa80f8fa82a3f67ae4145c8247a5e51` |
| Left, close startup | 731 | gap11, age7, one frame after fresh B | `727c225e4cd25cbeef269ceabb1cb56384ec193f129a2d114a102ca31bcd9e0e` |

Right controller SHA:
`943e6886e3d76e427c54e7df107fdbeb768e26ac16bd3f6e8ad79c9f0a8b674a`.
Left medium controller SHA:
`6aa82c0f0b97e88f98e124eefbd8aa8c0cc0419c181b2706ea241961d31c5965`.
Left close controller SHA:
`5b33d4b604a92e09e251690e24aae15aa18bf3f6259e660bdfe9dc27d9d520c1`.

The new mirrored replay floats over the Goomba, uses a normal B air puff to
deflate, lands to its right, turns left and starts inhaling. It observes the
original exact mapped hooks for fresh input, capture and erase, with mirrored
facing/input/gap assertions. No source movement or game code was changed.

Initial controller attempts failed before a qualified inhale: a late jump hit
the low block and landed into the enemy; passive float descent took so long
that the Goomba escaped left. Earlier takeoff and normal deflation solved those
controller approaches. Those failures are not evidence of a new inhale bug.

Generator: `tools/audit/replay_kirby_left_inhale_1112.py --variant 1|2`.
All runs were bounded and created no captures. The single generated controller
was removed after validation; source and receipts remain. No ROM/release update
is needed for these verification-only changes.
