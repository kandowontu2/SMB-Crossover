# Current nightly: DK and all six WWF opening sprites

Root16107 is terminal PASS for seven separate actual Downloads Mesen runs
on590e0ae60414d98d4b0a4d74874af58b93c6e720e8156220e0648966128b5f1f.
Each uses the real compiled character menu and ordinary controller input.
All runs preserve installed/candidate bytes and clear sidecar patch guards.
No ROM, graphics, gameplay or helper change is proposed from these checks.

Root visually inspects15 PNGs: one live Goomba and one naturally mature
Mushroom per identity, plus DK's ordinarily emitted barrel. Goomba and
Mushroom shapes/colors are correct in these openings; the reported
corruption is not reproduced. DK's body, barrel and Mushroom coexist.
Both lives remain in every sampled state. The image routes stop before
pickup; they do not qualify pickup freeze/recovery or later powerup states.

## Exact native runs

| Identity | Main returned / physical frames | Lua SHA256 | Receipt SHA256 |
| --- | ---: | --- | --- |
| Ted DiBiase | 935 / 1521 | 3007638ffaeb70a1e0a87dfffa2ad410a92cee2ff12efd6b92ae68875c2ab9e2 | f24b68d61562ad2fa80da98431df56c36ee492ca230d7a65bdaa0917b7f04766 |
| Bam Bam Bigelow | 921 / 1510 | c517479155f651f443e8a42d5605e5bda7778c9493619c1be248d31ea3a2f8f5 | 973f53f1d3054e62bf1b99dd12e5e3cc7028a44f7758484c38aa005dff257653 |
| Honky Tonk Man | 946 / 1527 | 0017d5ee8e1940ccaba131880e642709c7b25949bb4768d93d4032743d03dfa2 | ee35bb8b230b66ff5fa1365faf5b13052bb780e82431ca500a3fdfc2772eda16 |
| Randy Savage | 965 / 1544 | 4278e1ae8a3789fc31e965bc1bcc6cca6d2158012ac19f23855642b36409976b | b9c1ff19e56d13a6db1b6b70a599131d52f289d1e7773f648d33d79f57066735 |
| Donkey Kong | 690 / 746 | 196a8402e6a036fb2a76363f68b255518b30577d8ecb6b15162eaf7d1e5f3bc8 | a1189eacb16304673883767eae61126dc3db3df7f198bc1e644ac3685f3fe3ed |
| Hulk Hogan | 908 / 1490 | 136ec5809a05b1d38651419aa3e093a8e94e1696ebee8741cbae0f838c7d6aa4 | b0de5d0f9d67b960d8e965079825bcd7bb2cf1d2cd49aea28e02601dc0e0ed85 |
| Andre the Giant | 963 / 1536 | b3afacc5d3d92b79245ffb9831e4d8fd2f4c2aa3b98cefad0ec323ab6051f237 | 228d1e7fca5dea58d14daaa2ec79ebc9414cf575ea1e8b36fa491be85e97dfab |

Hogan and Andre's four PNG hashes equal their earlier ae66 pictures,
although their ROM-bound receipts differ. All seven rows above are new
actual590 runs; no historical receipt is relabelled as current.

## Actual pattern and mapper evidence

Hardware windows1/2 remain physical16/17 at every picture. The wrestler's
private body uses window0; DK's barrel uses window7/physical823. An
independent direct read from the installed ROM compares32 actual OAM-selected
32-byte pairs: four per wrestler, eight for DK including the Mushroom
still present during the barrel picture. Every observed byte matches.
Goomba keys are17/544/16 and17/576/16; Mushroom16/960/16 and16/992/16;
barrel823/448/16 and823/480/16. This is actual OAM/latch-selected pattern
data plus inspected native PNGs, not only software bank-shadow checks.

| Identity | Goomba PNG SHA256 | Mushroom PNG SHA256 |
| --- | --- | --- |
| DiBiase | 6dbb37f612ebb7df226a424ce848e602c5ca30769c1f312c9bccca4b64650143 | 8f749266736a91de8f7c781f34034ad391b91ef59e7e0aec2236bb161c5692bc |
| Bigelow | 9fda782861d325d7fb56f7aded86ba04cd6f07828f2d21ad530789ebb4009a3e | f402a655a6bf6e152634eada91126d5712bb20455358da11f0e7a12c07782ca7 |
| Honky | 73b3107217bb4473aaffb4de7f0feb755726489a1e2e65fc45e3fef4aaa2e2bb | cceaeb08fb0d07cb406cb308777db828e9ce978775ce6489af27be5b2ddaca53 |
| Savage | 26472bccb83f205408deefdc5ed821745646551b95d2af69e52f9e9a13db4c5a | 4c2e719a99101b92be1830e5fd28786978df042d41b6efe2fb8b4dc2005888f2 |
| DK | 120a0ebac0c651bc92c4b593f8bc04723f3fdef1018c542d33e6bfb34543c1a3 | d1893aa7f48c869c75a1eeb8747f0c43640225c7dbc2b368c83721df3e269cc5 |
| Hogan | 07affc626261432af5b003c6a03e1b1dc4396b0f6b2bb4facfccf5f2ff55f3a1 | dde006cb9f9706990a8db2b4d7cc6198ffd18bc8651d7415429a3e7499af101c |
| Andre | 8480b92b50c60f4a57ffa76c55d0c8804e66a682cce9789e8e45609284259088 | d0aa42b630c74bab1c40cb3c033cae5f705e0868ab0fab0b0097c7ca74dbf278 |

DK barrel PNG: e826b2cd572b4e7448cc5661f5faa9ed5cab1c080447c0f52d20ea5fa46185ec.
Each PNG is2675–3175 bytes except DK Goomba2654. They stay in RAM/stdout;
there are no image files, videos, state dumps or new capture trees.
Seven individual runs use at most3 pictures each, within the4/run cap.

## Reproduction and limits

`replay_named_world_images_590_1115.py` authenticates exact590, explicitly
inverts only the known Prince/BT-service/score/BT-camera/Gimmick successors
to exact DK1daca, and inverts DK's three operands to the WWF82 parent.
It authenticates frozen factories and native16/17 pages, updates only
ROM/hook-bank config after checking every hook byte, and asserts unchanged
control/observer bodies. Metadata12110 checks the real compiled menu names,
roles and navigation; every actual native run repeats those identity gates.

Factory SHA256:9f6236e3b54fbd837ba72dd5a7f6d5f625024839a3b8d95315a4b67b5e6b07bf.
Root runner SHA256:e7250c171e9cc971f1e5591e6320a00b84cfcefb9d89f1c4882082b93b61d88a.
`run_named_world_images_590_1115.py` runs through the shared bounded wrapper,
resuming the existing `build/smb2-flag-native-1113` slot with max-files2.
That slot retains candidate590 and the final Andre controllerb3af. Root's
single Mesen queue is free after terminal16107; unrelated sessions remain
untouched. No backup, patch asset, release or gameplay seed is created.

These observations do not certify later terrain/enemies/powerups, full
animation, general palette mixing, scanline overload, all stages, audio or
performance. Prince's separate current graphics delivery is documented in
`prince-window567-native-root-1115.md`. The shared reset and older DK fix
remain in590; no new defect or repair is inferred from a non-reproduction.
