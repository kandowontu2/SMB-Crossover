# WWF opening enemy and powerup graphics

Actual Downloads input:
`ae669c7ec7536f1c912b3000597be7b3416c20f312638b2589f52fab55f0bc01`.
Root71314 executes two separate compiled Select/Start native routes, using
the frozen strict current factory7eff456f and ordinary inputs only. Both
finish successfully, with two PNGs each in memory and zero capture files.

| Wrestler | Lua SHA256 | Receipt SHA256 | Main / physical |
| --- | --- | --- | ---: |
| Hulk Hogan | f7a3481ec32c0a8f74159ec1243664fb35c3a4ea04953b8605184766a29bdd5a | d09e3f89ae5d01360d22c99e8fa8af830708e92239b22b81baecc8ad4d50b52d | 908 / 1490 |
| Andre the Giant | 3bec48449168a32fbaa98caf1aa99b397b8eb471e0a3101c101b5b371f764db2 | 65297fc03f39237afc564dc96463f9b67717e1a13740de26721c3c325ecb7eb0 | 963 / 1536 |

Root visually inspected all four native images. The live Goomba and the
first mature Mushroom have their normal shapes and colors in these shots;
the reported corruption is not reproduced in this opening-area sample.
Actual hardware sprite windows1/2 contain physical16/17 for both wrestlers;
only the private player window0 differs (446 Hogan,630 Andre).

An independent direct read of current ROM pattern bytes matches all eight
observed target pairs: Goomba17/544/16 and17/576/16, Mushroom16/960/16 and
16/992/16, once for each wrestler. Each pair is32 actual pattern bytes.
This compares the actual OAM-selected pattern data, rather than inferring
correctness from software bank shadows alone.

| Picture | PNG SHA256 | Bytes |
| --- | --- | ---: |
| Hogan Goomba | 07affc626261432af5b003c6a03e1b1dc4396b0f6b2bb4facfccf5f2ff55f3a1 | 2701 |
| Hogan Mushroom | dde006cb9f9706990a8db2b4d7cc6198ffd18bc8651d7415429a3e7499af101c | 3139 |
| Andre Goomba | 8480b92b50c60f4a57ffa76c55d0c8804e66a682cce9789e8e45609284259088 | 2705 |
| Andre Mushroom | d0aa42b630c74bab1c40cb3c033cae5f705e0868ab0fab0b0097c7ca74dbf278 | 3136 |

The native image controller ends at the mature Mushroom, before collecting
it. The separate source audit's60-tick pickup freeze and25 movement calls
remain source evidence, not native evidence from this run. These two
wrestlers and opening states do not qualify all six wrestlers, later
areas, every animation, sprite overload, general palettes or performance.
No gameplay/art/ROM change is inferred or proposed from a non-reproduction.

The source lifecycle/cookie/readers audit is in
`wwf-world-sprite-lifecycle-1115.md`. Root's bounded native runner is
`run_wwf_world_images_native_1115.py`; it reuses the existing two-file flag
slot, leaves other Mesen sessions untouched and preserves both ROM hashes
and patch guards. No backup, video, state dump, patch asset or release exists.
