# Mini moving fireball art provenance

Read-only receipt `e5cfbd90db168d8877a6d011479869db1a412255de57d641ab3bd950a217a13f` authenticates the existing functional 9826 image and the actual GBC donor. No art replacement, new game image, CPU route, screenshot or native run is proposed or executed here. The user's later exact-GBC appearance request must be resolved before treating the earlier 4×4 visual request as current authority. Root holds that preference question; the functional 20-byte repair remains independent.

The actual donor is `C:/Users/kando/Downloads/SuperMarioBrosMini.gb`, 2,097,152 bytes, SHA256 `837d39a438f85c5b3ef32c4e41c6c4403147046a7e93bdeac039a09a4a202c81`. Its active 8×8 tiles have GB row-interleaved bitplanes; the existing builder maps palette indexes `[0,2,3,1]` and moves the active tile ahead of a blank tile for NES 8×16 rendering. All four current moving/impact pairs match this exact conversion.

| Frame | Role | GBC active / pair file offsets | Current CHR967 offset / tile | Opaque pixels | Half-open bounds |
| --- | --- | --- | --- | --- | --- |
| A | Moving | `10FF30` / `10FF20` | `2E0` / `6F` | 23 | `[1,1,7,7]` |
| B | Moving | `10FF50` / `10FF40` | `3E0` / `7F` | 23 | `[1,1,7,7]` |
| C | Impact | `10FF70` / `10FF60` | `3A0` / `7B` | 8 | `[2,2,6,6]` |
| D | Impact | `10FF90` / `10FF80` | `3C0` / `7D` | 44 | `[0,0,8,8]` |

Each NES pair's second tile is blank. A's physical file offset is 2039536, pair SHA `aba9fa8b8bdbe98cb45b6a64dac08951bc8dd5bebae4a2c17055d488e97f4715`; B's is 2039792, pair SHA `3444e08ba8503e2128e8aedd09c162e4ba5e9a214d24d53b9ff3288380c25b8c`. Their first 16 bytes are exactly the bytes observed by root's native picture scope79115:

```text
A 0038367e5e4c20000000380c0c000000
B 00384e1e3a3c1c00000004041c180000
```

`prepare_mini_fireball_contract_1103.py` measured a different, deliberately adapted 16-pixel 4×4 warm-core graphic from `mini_mario_fireball_1103.s`. That source explicitly says “no resampling claim.” It is historical provenance, not the present tile. `prepare_mini_fireball_art_1108.py` later replaced moving and impact frames with the pinned donor assets and explicitly reported `live_art_extent=[6,6]` alongside `native_collision_extent=[4,4]`. The apparent discrepancy is a superseded visual contract, not evidence that current pixels were corrupted. The actual current moving silhouette is 6×6; control8 does not prove 4×4 art.

The retained phase worker uses native X+4, normal OAM Y+1, flipped OAM Y−7 and attributes02/C2. With 8×16 sprites, the complete 16-pixel flip and its Y compensation retain the donor silhouette's intended placement. Root observed PPUCTRL168, tiles6F/7F and actual slot5 bank967. This read-only receipt binds the source and exact tile data; it does not independently execute the renderer.

Metadata967 is a mixed immutable carrier, not a free art/code hole. A occupies physical `D2E0..D300`. B occupies physical `D3E0..D400`; the cold loader first copies its pose/restore workers from earlier D300 staging bytes, then reconstructs the runtime attribute table over D300..D400 in RAM. Physical CHR art stays intact. No executable funding or padding is inferred from these tile ranges.

The whole Mini packet remains 7,168 bytes, SHA `021e14f6ca810695ae3e4c744f7b9bdec60cd1608c12866cf609a982e8bf006b`; code5120 SHA `1167be90991080be8d47b09922e51083f78c12a6b987b2ed0bf4ecb6972627a6`; metadata967 SHA `60d569192113a91f872dcc78c15ddaabe6f805a1124c11feeac58dd91efc32b0`. Its sole immutable 16-byte cookie is at physical536595 / PRG65:B003, `a72901021e14f6ca810695ae3e4c744f`. Any future approved art change must update that payload-derived cookie and both loaded full-cookie witnesses plus their strict native observer bindings. None is changed here.

Exact source pins:

- `prepare_mini_fireball_contract_1103.py`: `e0ec815ec9fe7a6debc8582e9985dfb9de9ca06cc1eab8bdabbf6613d4d0d2f7`
- `prepare_mini_fireball_art_1108.py`: `ff4f95fe0c779c745f249b516e27254d0f965b6d07dd02a9f9efcc994796fa34`
- `extract_mini_fireball_art_1108_v1.py`: `58ddf5d160bf31fa1f48854026aa266ed4b016e03319037e2fe2565bdf533bc7`
- `mini_fireball_art_1108.s`: `4c852862cb848823b28d47fb39c7dac2ff94489e0e0a8cca79aaab18f99f1822`
- `mini_mario_fireball_1103.s`: `fece86b43bcffa05508d3ec2d25a684d3e03a88746805b29f1a7a5d75f7437d8`

The inspector is `tools/audit/inspect_mini_fireball_donor_1116.py`. It ran through the bounded runner with absent `build/mini-fireball-donor-source-1116`, max1 / 600 seconds, and created zero output files. Functional C/F/Lua, game bytes, helper inventory, Downloads and the shared native slot are untouched.
