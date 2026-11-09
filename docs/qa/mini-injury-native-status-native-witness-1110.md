# Native Mini Mario powered injury witness

The private `68f91167` cartridge reproduced the [CPU powered injury status observation](mini-injury-native-status-1110.md) under controller-only Mesen playback. Mini collected a natural mushroom and reached `PlayerStatus=1`. At frame 1650, the physically qualified `ForceInjury` ingress recorded the powered side contact with a live Goomba at world X718, while the camera right edge was X844. At frame 1666, the first native injury movement update recorded engine 10, timer `$EF`, and `PlayerStatus=41`. The status remained 41 for all 39 recorded native injury movement updates. Mini retained both lives.

The replay stopped with the camera edge at X852. The pipe prevented that controller route from reaching the third lift admission window at X856–863 during injury. This run establishes the native status write. A separate controller replay must establish the lift crossing during injury.

Evidence is `build/mini-injury-helper-native-1110/capture/result.json`, SHA-256 `d0467b76fe110f36d34474b21544a63af026440e43ae8c45477f35e294aedbe7`. Its `binding.json` records terminal exit 1 and the exact ROM SHA-256 `68f9116724fcb02e0ce457b8487b29a570328566c5cd7b50a1cab531b33bbc45`.
