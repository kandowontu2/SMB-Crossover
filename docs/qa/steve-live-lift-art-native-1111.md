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
- One screenshot was reviewed, then removed before the next run to keep the
  shared build file reservation within its cap.
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

The same candidate subsequently passed the full Mesen Laserbot 1-1 replay:
one verified Goomba beam hit (HP2 to1), both lives and HP4, entry into 1-2 at
X40/Y48. Receipt `02e8319a34932c3c38f9068a3f5bc645d4a6bb8c0746a236668b060079535a0a`;
controller `8f3cd1a21b2207452661ce380533230bc48242c05edcd5fcc5d7fe5e64ff31f9`.
Mike, Jay and Steve each matched 80 opening updates against the installed
nightly, including native OAM, CHR latches and VRAM.

Source review then found that the new lift-body early return skipped existing
projectile rendering. Live shots could be invisible while their hit logic
continued. The source fix calls the appropriate projectile-only renderer
after the lift body. These additional edits invalidate the candidate hash
above as a delivery target and require new qualification. A focused check also
verifies the ordinary player pose/CHR owner after releasing the lift.

The fixed in-memory candidate is
`80e6aa3e32574f38b23fa6da6ab3c94bbe7b5ae11b29339b32b11a624fe6f1ed`.
Its worker occupies 499 of 512 bytes. The enhanced CPU route passed all nine
required body/robot poses, 135 first-companion projectile renderer dispatches
following a lift-body draw, and the release transition to native pointer
C141, PRG97 (mapper value E1), four visible OAM cells and published CHR220.
The 21-pixel rise, same-ledge landing, both lives and five brick-headroom
updates also passed. This proves renderer dispatch, not a natural simultaneous
live-shot-and-lift OAM witness; that stronger test remains required.

Still verify the fixed candidate, Downloads launch and replacement IPS before
publishing a nightly. B throw, remaining companion attacks, armor and original
lift/throw audio remain outstanding. No helper platforms changed.
