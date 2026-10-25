# Terrain publication repair and Easy Bill demonstration

The green ground/cloud patch in Bill’s 1-3 movie was caused by a dropped attribute column. A normal update queued seven background attribute writes. Before NMI consumed them, an immediate lag catch-up collected a coin. The native coin/axe erase writes the secondary VRAM queue from its beginning, replacing the column with its own ten-byte packet and terminator.

The original, read-only Bill replay reproduces the overwrite at frame **14406**. Its first 15,000 trace rows and cycle counts are byte-identical to the original recording. `build/verification/bill-green-producer-l/producers.csv` preserves both producers and their exact packet contents; `summary.json` binds the literal replay.

## Installed repair

After an update actually lags, `IdleLoop` now checks whether secondary VRAM work is still published. If so it lets NMI consume that work before starting another catch-up. Otherwise it retains the existing one-catch-up behavior and sprite-skip flag. Normal updates retain the original comparison/branch path and incur no additional instructions.

The helper occupies fourteen bytes of an already unreachable resident bridge tail. Both mappers change only nineteen ROM bytes in banks62/63. All old code-label addresses and RAM addresses, header and CHR remain unchanged. No new RAM or mapper feature is required. Checkpoint: `build/checkpoints/terrain-publication-af/manifest.json`.

The first O candidate called its predicate even on normal frames. AF moves the check behind the existing lag branch to avoid that common cost. O remains frozen because the demonstration below was recorded on that exact candidate. No recording is retagged as AF.

## Verification

- The old-ROM native fixture fails specifically because coin collection overwrites the queued attribute column.
- The new permanent `terrain-coin-publication` test passes on MMC3 and MMC5. It authors a lag/coin arena, then observes the actual coin handler, NMI consumer and all seven physical PPU attributes. This is an explicit diagnostic fixture, not a controller-only clear.
- Eleven existing tests pass on each mapper: character selection, outline option, Mario pipes, Luigi physics, Bill flagpole, Samus head displacement, Sophia weapons, springs, firebar draw admission, roster stomps and Bill inventory. These are24 checks including the new regression on each mapper; they are not a new full757-case suite.
- Build and existing-test receipt: `build/verification/terrain-repair-build-ag/summary.json`. Permanent native logs: `build/verification/terrain-coin-permanent-mmc3-af.log` and `terrain-coin-permanent-mmc5-af.log`.

## New ordinary Easy progression recording

[Bill Easy progression MP4](../../Playthrough%20Videos/Showcases/Ready/Bill-Easy-Progression.mp4) shows the normal rifle, a naturally collected mushroom and machine gun, then the naturally collected 1-1 Fire Flower and spread shot. It includes native game audio and captions above the image. The posted edit is40.916seconds; there are no gameplay cuts after removing the menu/loading prefix.

The fixed power-on replay has3,000 emulator frames and2,999 native captured images, with zero deaths. Its trace and inputs exactly match the independently discovered prefix. The lossless native RGB/PCM verification passes. Every edited gameplay frame also matches the native pixels after reversing the nearest-neighbor scaling, and its PCM audio matches the trimmed native PCM exactly. The H.264 MP4 is the lossy delivery copy.

- Native packet, controller replay and lossless capture: `build/roster-through-2-2/bill-easy-showcase-z-3-v0-mmc3/`.
- Editorial lossless master and delivery manifest: `Playthrough Videos/Showcases/Ready/`.
- Pixel/PCM receipt: `build/verification/showcase-pixels-aj/report.json` —2,459/2,459 frames, zero differing gameplay-pixel frames, identical native PCM.
- General frame review: no motion, split, lag-CHR or vertical-row flags in this bounded capture. Audio queue flags are not interpreted as proof of missing sounds; all source-SFX parity remains part of the larger audit.

This demonstration is a bounded1-1 sequence on O. It is not a through-2-2 clear or a claim that all current bugs are fixed. Earlier editorial attempts are preserved: AC dropped the last frame through shortest-stream truncation; AD kept the frames but used YUV caption composition. The Ready/RGB edit fixes both and is the intended file to use.

## Open work

The terrain repair changes catch-up timing, so original full-route inputs cannot be assumed valid on it. The first old Bill transfer dies in1-1. New controller policies collect both1-1 upgrades and clear1-1, then currently reach a later1-2 failure at x2303. A specific first-gap controller correction clears the low brick ceiling before jumping; this is ordinary gameplay, not a ROM collision change. A fresh ordinary visit and recording of the formerly corrupted1-3 location still remains to be completed.

The score-popup report now has an ordinary replay baseline: five of sixteen observed Bill score anchors use a stale shared enemy-relative X. That repair is not installed. Bullet Bill duplication, missing firebars, underground bounced-brick colors, late HUD splits, Pit’s contact-frame candidate and the tree-color strip remain open. A passing firebar draw-admission test is not proof that the user’s missing-firebar report is fixed.

Hard-mode natural upgrade clips, the Easy/Hard enemy-landing comparison, all-character final recordings, every special/alternate/upgrade lifecycle and remaining lag optimization remain required. The older frozen Land/Arm/Rush/audio/HUD/Ryu/visible-Water candidates have not been merged by this repair. All original videos, native captures and negative evidence are retained under the user-approved100GB cap.

Later follow-up: [score popup repair](score-popup-repair-2026-10-22.md) records the installed successor. Earlier findings and test counts above retain their original build identities.
