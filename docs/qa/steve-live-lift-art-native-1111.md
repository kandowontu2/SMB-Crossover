# Steve original lift poses: physical replay

Private candidate: `c36c9f76e462a214405a6431a7810934c6b2de45ca8620071cbf5f967d2b8ebf`.
Installed nightly remains `235de3ed2487cd3f93c695e1eb2ceec55c172cede3cb6d98c5309afbc7cfbe38`.

The native pose integration builds original player and companion records in
raw WRAM bank 2, with a fixed-ROM guard before entering the loaded worker.
The player renderer maps that WRAM owner for the dynamic record. Original
non-lift rendering remains the fallback. The companion uses its matching
original lift poses rather than its ordinary attack pose.

Controller-only Mesen replay passed: earned Alpha companion through the
three-token route, approached, latched, gripped, rose from native Y48 to Y27
over 21 updates, and returned to Y48 with both lives. The replay finished at
X1743 after 3817 physical frames. It checked complete lift OAM DMA and the
actual MMC5 sprite bank register writes (1 KB mode, slot zero page 339).

- Receipt SHA256: `646ed89b77a8c4dbd5ddb193e3c395ab8b99196f9c50869658c3f52e90d0ee4e`
- Controller SHA256: `80bb8bf4a304bf4c2ee797ea7c8d1baecb064663d38778f4443e20d45c31aece`
- Candidate and replay: `build/steve-pose-native-1111/`
- One reviewed screenshot: `build/steve-pose-native-1111/lift.png`
- Reproduce with the bounded runner, `--resume --max-files 3`, invoking
  `replay_steve_companion_native_1111.py --lift-art --reuse-route --output build/steve-pose-native-1111`.
  Storage preflight must still pass; discard the superseded task screenshot
  before regenerating it when the shared file reservation has no room.

## Test correction

The first physical check incorrectly compared frame-end `nesPpuMemory` with
the sprite CHR page. MMC5 switches its generic PPU view between background
and sprite banks. A correct sprite register write can therefore coexist with
a background page returned by that read. The failed assertion was reproduced
at Y40, while independently observed sprite registers already selected page
339. The corrected check observes actual writes to $5101, $5120–$5127 and
$5130; no game-state writes or weakened movement assertions were introduced.
See [Mesen's UpdateChrBanks implementation](https://github.com/SourMesen/Mesen2/blob/master/Core/NES/Mappers/Nintendo/MMC5.h).
Failures now expose the emulator receipt instead of being masked by a missing
screenshot assertion; diagnostic screenshots are retained even on failure.

## Remaining before delivery

Run the full Laserbot 1-1 regression on this exact candidate, complete the
family rendering regression, then verify the Downloads launch and replacement
IPS before publishing a nightly. This replay proves the lift sequence only,
not all of Steve's gameplay. B throw, remaining companion attacks, armor and
original lift/throw audio remain outstanding. No helper platforms changed.
