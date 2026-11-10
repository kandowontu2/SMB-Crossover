# Sonic rollback snapshot pacing

The snapshot copies the same 180 bytes of source state and four self-modifying
code bytes into the same rollback buffer. Four 45-byte lanes reduce the copy
overhead by 1,027 cycles per original Sonic update. The existing rollback
path restores the full snapshot when terrain data is unavailable. The 49 ROM
byte changes are confined to two Sonic code pages and its authentication
cookie.

| Controller-only World 1-1 replay | Parent | Candidate |
|---|---:|---:|
| Physical gameplay frames | 4,888 | 4,825 |
| Gameplay frames without a completed Main update | 2,162 | 2,099 |
| Completed Main updates through active 1-2 | 3,041 | 3,041 |
| Lives on entering active 1-2 | 2 | 2 |

Both runs end at X40/Y48 in active underground 1-2. The candidate also passed
the five-ring pickup, visible ring loss and recovery replay, and the separate
earned mushroom replay. The candidate still has substantial frame pacing
headroom. A larger shared side-probe optimization remains separate.

The exact Downloads ROM reproduced all three Sonic receipts. Its separate
Donkey Kong Jr. replay crossed the four opening pipes and both early gaps
with two lives and matched the previous gameplay receipt after normalizing
the ROM hash. The automatic patch guard passed before and after the direct
replacement. No backup or capture file was retained.

The source suite checks actual cold readback (22,486 PPU reads and zero warm
reads), six foreign cold pairs, 14 transfer faults, 34 header rejections, and
52 matched native epochs including two full rollbacks. Thirty-nine NMI cuts,
39 IRQ cuts and a nested IRQ exercise the new snapshot loop and its mapper
boundaries. The natural CPU ring sequence retains the original hit,
knockback, recovery, and drop lifetime.

- Parent ROM SHA-256 `3d327d47b8127c1e76d9868191d34b8ebb1ca9ec29d6bb609ccab9c60c6cb3d8`
- Candidate ROM SHA-256 `8c1ebb1bfbe21499461c5fd65ea75b784460ac2cb81a712a9db9941aa7cec711`
- Reconstructed IPS SHA-256 `390c95dbf17b6356293a52c16a88a801fdc6b357e2ca830cabb3d88bb48dad7f`
- Parent full-stage Mesen receipt `1b540a0e7066a5402465576d6644eacf3c1820197e75f80be0a21b9bf737d3a6`
- Candidate full-stage Mesen receipt `c1cba1931533a260963dffcf6f4bd9476925c0ce5c10d0740f2d6c46a01a1b86`
- Candidate rings Mesen receipt `9f2c8f769a654d7a49d684efaf50954c08587f86fd955820cc6b8f70fea15745`
- Candidate mushroom Mesen receipt `3f7f6580f51a6ecbae27cdd2fc51cbe5d8344737c7134f655bb3a48b9f639d1c`
- Installed Donkey Kong Jr. regression receipt `24b500bed465b28eea63b41b3ca6f74778d20d3ca0e0d6c6c4e265bb3846fa1e`
- Ring replay Lua SHA-256 `628832f25a2e9ed7975b5523904ad91731be130df35f11c488cb327ddb8f1e37`
