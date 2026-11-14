# Common world-sprite fix: verified Downloads delivery

The installed nightly is now
`82ec0446873b28af458e7686fec87938feaf798a0a893b44e4dccfd071ccfd63`
(2,097,168 bytes), at
`C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes`.
It equals the tested `build/smb2-flag-native-1113/candidate.nes` byte for byte.

This fixes stale character-preview CHR modes surviving into gameplay. The
allocation, exact 29-byte macro, portable inverse, source contracts and
interrupt checks are recorded in `shared-world-chr-reset-1114.md` and
`allocations/shared-world-chr-reset-1114.json`. Only 28 bytes change within
that 29-byte allocation. All earlier 421 fixes remain present.

Root's private native checks cover all six WWF wrestlers: Hogan, DiBiase,
Bigelow, Honky Tonk Man, Savage and Andre. Their Goomba and mushroom OAM
select native pages 17 and 16 with matching tile bytes and palettes. The
normal-pose Goomba checks for Prince and Donkey Kong also improve. Their
private powerup-window conflicts **remain open**, as do Prince's pipe
collisions. This delivery does not claim those issues are fixed.

## Verification in the actual Downloads launch context

The first install job, root6590, finished, but its terminal output was lost
during compaction. Recovery independently found the installed 82ec hash and
no remaining owned Mesen process. No success was inferred from that absence.
Root38527 deliberately repeated the idempotent installer once; its reported
previous hash was already 82ec. This repeat completed with exit 0 and all
assertions below passing.

| Controller | Actual Downloads result | Receipt SHA256 |
| --- | --- | --- |
| Hogan `829f3f25...` | 1,490 physical frames / 908 completed Main updates; both correct Goomba/mushroom images match the private run exactly | `b1388d1a1d4f5f38ddb34a82a11a56b013df0bc62cae94fb63896a9005057e05` |
| Toad `a42266b5...` | 3,221 physical frames / 3,204 completed Main updates; full nonshortcut 1-1, flag, castle and entrance, then 25 living grounded updates in 1-2 | `cd0e705ddb11054cd9bdc92d4170616b42437fe550c7338edbb6a4e5abc701f1` |

Toad ends at world X40/Y176/high1, native grounded state 0, two lives,
power 0, Star 0, alternate 5. Hogan's PNGs remain in memory only:
2,701 bytes, SHA `07affc626261432af5b003c6a03e1b1dc4396b0f6b2bb4facfccf5f2ff55f3a1`;
3,131 bytes, SHA `a177ef68d0ed895ba76727c8e88bea39fe0fbd5e5f3f4941145139b20fe91722`.
Both receipts and both PNG hashes equal their private-candidate results.

The installer authenticates its composer/replay source hashes, the candidate,
the complete inverse back to 421 and the allowed installed parent/current
hashes. Pre-copy and post-copy sidecar patch guards pass with no matching
IPS/BPS/UPS files. Installed bytes are checked against the candidate before
and after each Downloads replay. No backup, patch asset, release, video,
capture file, state dump or receipt file is generated. Existing user and
other-project emulator processes are untouched.

The bounded runner resumes the existing two-file flag slot with max-files 2.
The controller is replaced in that slot; no extra build directory or file is
created. Root's single Mesen queue is free after terminal job38527.
GitHub releases must remain empty. Overall roster work remains active and
incomplete; helper-platform locations are unchanged by this patch.

Post-delivery source checkpoint `41a171a8` was pushed to `origin/master`.
The verified repository's releases API reports zero releases. A read-only
storage inventory reports workspace 6,410,185,119 bytes / 56,995 files and
build 2,873,631,813 bytes / 19,996 files. No build growth or additional capture
files are needed for this delivery; the 20,000-file build cap remains in force.
The unrelated user progress JSON retains SHA256
`bd99b4ee9143380aabf12da8ee1e56beda5a1491abe26c92e6c789afecaaa0a7`.
