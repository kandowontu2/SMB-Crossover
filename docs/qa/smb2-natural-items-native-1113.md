# Eight SMB2/Doki natural Mushroom pickups: native PASS

All eight were independently run in actual Mesen against the unchanged
Downloads launch context:
`C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes`, SHA256
`7ef2de351d3a4ae60b3ada2eb1aa56b330873dc106ad43428ec6803bf420d4fc`.
The pre/post automatic-patch guard was clear. The private flag candidate
remained unchanged in its separate file. No ROM was installed by these tests.

`run_smb2_natural_items_native_1113.py` uses the frozen factory and real
native menu in source commit379f3332. Root ran Imajin first, then the other
seven serially through the sole Mesen queue. Each run retains the real first
Goomba injury, actual authored C1 head collision, native preparation and rise,
mature physical pickup, original grant, erase, sound and score popup, followed
by 60 resumed ordinary updates. No gameplay state or ROM byte is written.

| Identity | Physical frames | Returned Main | Collector Main | Result |
| --- | ---: | ---: | ---: | --- |
| SMB2 Mario | 874 | 534 | 474 | PASS |
| SMB2 Luigi | 904 | 541 | 481 | PASS |
| SMB2 Toad | 899 | 537 | 477 | PASS |
| SMB2 Peach | 920 | 537 | 477 | PASS |
| Imajin | 906 | 503 | 443 | PASS |
| Lina | 916 | 508 | 448 | PASS |
| Papa | 951 | 522 | 462 | PASS |
| Mama | 954 | 526 | 466 | PASS |

Every run starts with health31/max0 and both lives. The actual Goomba contact
reduces health to15; the native item kind is0, and it reaches mature state128
before collection. The real collector erases the actor, writes sound32 and
popup6, increases max-health0 to1 and heals to47. All eight finish alive on
ordinary ground at X395 or396/Y176 with both lives. Mesen positions differ
slightly from the CPU model; no positions or controller timestamps are repaired
to match it.

Imajin's actual C1 head occurs at Main257/X329/Y150, birth at Main258/item
336/135 and mature collection at Main443/item406/184/player396/176. The
documented healthy large/two-heart Flower policy is unchanged. This proof
qualifies the injured Mushroom and recovery, not Flower reserves/attacks,
Star, 1UP, every health tier or a completed 1-1 exit.

| Identity | Frozen Lua SHA256 | Full native receipt SHA256 |
| --- | --- | --- |
| SMB2 Mario | `18ffdb276851310ca47b3cf81b4c6296553c51880973fe821bda4ba5ac604637` | `bba0072b061cdfefc5342ace8ad91b99ba9c235e8e8dbda11d172935bfe6e8cc` |
| SMB2 Luigi | `c5ca127d154a93208b05b3a46df4e7d4ca6154dac2d841e63c66225815ffc10b` | `2e70af5ade43fb6ee837e4bbf1ee2edd671fe9b5c86a8daa763b35dde35c4766` |
| SMB2 Toad | `f11ece155400e8a0759df2b677fb28cf89dd27876880835f4bfd00a74f1d61ea` | `5dd21d1df768db4dc568e535217c5c7287def2cb6a0d2b10b25ded8c9b039977` |
| SMB2 Peach | `87afd36136998d186ea2abe0d5eafab3a75e85d86e3c8b90b9fa7654941346e8` | `0555d604803a92cb868fc390f7e52da2b4d11aace4f3a0dd0f1c753f07e39822` |
| Imajin | `36e52aae4abee6a26a42dd396239137d41195e4fe72ab85dfd0dfcb75b3bb81d` | `afc423ce870ec83de92b5ab94dedbd2fc5980f45a09219f46fc157e28e27bc1f` |
| Lina | `f989e99c0fb1ac05d4f9b837748dbb4f6a8443038fdb2ac0eafa43732c6ad149` | `f4ca8f959af80f9b2765d45bbaf9a53e80b57bc4b7c891e88fad75f1bb4fc5d1` |
| Papa | `679f8817ca936011fe2cbde247106cbe07b4e89bd83f6caabb59e1cbd8df4047` | `e3df7fc4df984175f208733d07a74a73ebda4709e154c65c68af4bd31fa9232e` |
| Mama | `714d8373089d38b9f58f6781d399df174f5515315874acebcad41cc44eb9e100` | `f657748e9f1043880d9200f06d6b2e43bb2fff0163540a23cf5cbeb55f4b661c` |

All outputs stay in stdout. No capture files, screenshots, videos, states or
per-case receipt files were created. Root reused the existing bounded SMB2
two-file component and overwrote only its controller Lua; no backup copies.
GitHub releases remain empty by user instruction. The entrance halt remains
separately open in `smb2-flag-native-1113.md`.
