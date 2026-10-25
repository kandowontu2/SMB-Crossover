# Review of the 14 current recordings

The outdoor green corruption is in **Bill.mp4, 1-3, approximately 4:01–4:05**. The excerpt starts at 3:59 and ends at 4:08. Ground blocks and part of a cloud turn green. The other 13 recordings do not produce this same green-background candidate in the cross-character scan.

[Green-tile clip](../../Playthrough%20Videos/Review%20Clips/Bill-green-tiles-1-3.mp4) · [Clear frame](../../Playthrough%20Videos/Review%20Clips/Bill-green-tiles-frame-14599.png)

## Coverage

All **369,711 frames** of all 14 retained lossless masters were decoded. Their delivery MP4 identities match their original recording manifests. The general scan checks motion, physical HUD split timing, CHR changes during lag, screen-row displacement and large background flashes. A second pass checks all **139,244 active outdoor frames**, masks committed sprite rectangles and compares aligned background cells across characters. This caught the small green patches that the older whole-row checks missed.

Manual inspection covers the green candidates, Bass’s reported 1:38 sequence, and the consecutive-frame evidence for every motion/screen-shift candidate. This is automated full-frame coverage plus targeted visual inspection; it is not a claim that a person watched every frame or listened to every sound.

| Recording | Decoded frames | Outdoor frames | Green background candidates | General motion / screen-row flags |
| --- | ---: | ---: | --- | --- |
| Bass | 29,542 | 11,865 | None detected | 2 / 0 |
| Bill | 34,400 | 14,786 | 8 cells, two scene regions | 6 / 0 |
| Mario | 16,990 | 4,905 | None detected | 0 / 0 |
| Mega Man | 32,517 | 11,274 | None detected | 0 / 0 |
| Samus | 32,223 | 13,092 | None detected | 2 / 0 |
| Link | 27,057 | 11,902 | None detected | 0 / 0 |
| Simon | 28,792 | 9,842 | None detected | 2 / 0 |
| Pit | 25,749 | 9,098 | None detected | 1 / 0 |
| Rygar | 21,536 | 7,627 | None detected | 3 / 2 |
| Luigi | 17,411 | 5,126 | None detected | 0 / 0 |
| Ryu | 23,097 | 7,946 | None detected | 8 / 0 |
| Sophia | 25,403 | 8,607 | None detected | 3 / 0 |
| Scrooge | 21,741 | 8,238 | None detected | 0 / 0 |
| Lance | 33,253 | 14,936 | None detected | 2 / 2 |

Raw flags are not all visible bugs. Several motion flags sample temporarily relocated projectile-collision coordinates during an interrupted update, while the player image remains stable. Rygar’s 2-1 Y-high wrap at the top of the screen is also not a 65,000-pixel on-screen teleport.

## Findings

| Recording / original time | Finding | Status / evidence |
| --- | --- | --- |
| Bill, 1-3, 4:01.62–4:04.60 | Ground-block patterns become bright green; a cloud in the same region also becomes green. The brown block pattern remains recognizable, so local background palette/attribute corruption is the leading explanation, not a proven replacement of terrain collision data. | confirmed-visible; [clip](../../Playthrough%20Videos/Review%20Clips/Bill-green-tiles-1-3.mp4) |
| Bass, 1-2, 1:37.40–1:40.30 | Brown/orange bouncing brick art against the blue underground ceiling, including the user-reported 1:38. Similar brown brick art is visible in other guest recordings. Root cause and final palette repair remain open. | confirmed-visible-color-inconsistency; [clip](../../Playthrough%20Videos/Review%20Clips/Bass-underground-block-colors.mp4) |
| Rygar, 1-2, 1:22.25 | One-frame displaced HUD/background. The physical split writes occur a scanline late; surrounding frames restore the screen. | confirmed-visible; [clip](../../Playthrough%20Videos/Review%20Clips/Rygar-screen-jump.mp4) |
| Lance, 1-2, 1:49.05 | One-frame displaced HUD/background with a matching late physical split. | confirmed-visible; [clip](../../Playthrough%20Videos/Review%20Clips/Lance-screen-jump.mp4) |
| Pit, 1-4, 3:51.95 | Suspicious block/player appearance at block contact; retained sequential frames and clip. Not promoted to a confirmed sprite bug without actual committed-OAM/CHR comparison. | follow-up-candidate; [clip](../../Playthrough%20Videos/Review%20Clips/Pit-block-contact-review.mp4) |
| Ryu, 1-2, 1:27.10–1:29.70 | Abrupt wall-contact adjustments in the footage. Source behavior and the private uninstalled Ryu repair need separate review. | follow-up-candidate; [clip](../../Playthrough%20Videos/Review%20Clips/Ryu-wall-contact-review.mp4) |
| Bill, 1-3, 3:36.49 | A narrow green strip on a tree trunk is the other cross-character background candidate; inspect its publication separately from the clear late-stage ground/cloud fault. | follow-up-candidate; [frames](../../build/verification/outdoor-green-review-e/Bill-candidates-1.png) |

## Reproduction and retained evidence

The green-background scene also has a fresh read-only replay of the original Bill inputs on the original movie ROM. All **15,000 trace rows, including cycle counts, are byte-identical** to the movie’s prefix. The bounded replay deliberately stops at frame 15,000 and is not claimed as a full clear. PPU writes and background attribute/palette changes are retained for diagnosis.

The first trace assertion incorrectly compared CRLF output against an LF-normalized expression; the corrected comparison uses the untouched original byte prefix. The original assertion failure is retained. No gameplay or trace data was changed.

ROM MMC3: `35a6543694774aa78d9e9e5af6fc77f5dc3bdea931b71d2d211a5852c472d40e`. All six review excerpts retain native game audio, a lossless excerpt master, a 768×720 MP4 with nearest-neighbor scaling, and source/input hashes in `Playthrough Videos/Review Clips/manifest.json`. These are extracts of existing footage, not newly recorded showcase runs.

Evidence: [general full-frame index](../../build/verification/postable-footage-audit-b/index.json), [outdoor full-frame index](../../build/verification/outdoor-green-review-e/index.json), [green candidates](../../build/verification/outdoor-green-review-e/candidates.json), [sequential flagged frames](../../build/verification/footage-flag-inspection-g/index.json), [Bill replay proof](../../build/verification/bill-green-native-i/summary-j.json).

## Remaining work

No runtime fix is installed by this review. The green corruption, underground block colors and late HUD splits need repair and fresh recordings. Pit’s contact frame and the narrow tree strip remain candidates. Bullet Bill duplication, missing firebars and misplaced score popups still need actor/renderer evidence; this review does not certify those reports fixed. Audio presence/voice-write checks do not certify every required sound effect or source waveform.

The previous request for new natural Contra Easy/Hard progression, each Hard upgrade, and an enemy-landing comparison remains open. These old Easy route recordings do not provide that showcase. The broader all-character abilities, optimization and final-recording goal remains active. Original captures and lossless data are retained under the user-authorized 100 GB workspace cap.

Follow-up: [terrain repair and new Easy Bill recording](terrain-publication-repair-2026-10-22.md) documents the later installed repair. Findings above retain their original movie/build identities.

Later follow-up: [score popup repair](score-popup-repair-2026-10-22.md) records the installed successor. Earlier findings and test counts above retain their original build identities.
