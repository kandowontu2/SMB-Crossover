# World 1-1 audit: six added characters

Twelve fixed-controller recordings cover Pit, Rygar, Luigi, Bass, Ryu and Sophia, with both routes for each. All runs survive and verify movement in 1-2. Each surface run defeats all 17 enemies and collects five power-ups; each shortcut run defeats all six encountered enemies and collects its mushroom. Review decoded **57,084 video frames** with native recorded audio.

These recordings pin the checkpoint below, before the later Contra optimization. They expose the unresolved defects listed below and do not establish complete reference-game parity. The original-six audit is preserved in [world-1-1.md](world-1-1.md).

[Video gallery and issue clips](../../build/playthroughs/expanded-review.html) · [Machine-readable audit](../../build/playthroughs/expanded-summary.json)

| Character | Video | Frames | Enemies | Pickups | Lag frames | Overloaded sprite frames |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Pit | [surface](../../build/playthroughs/expanded-qa-6-surface/playthrough.mp4) | 6,164 | 17 | 5 | 22 | 346 |
| Pit | [pipe](../../build/playthroughs/expanded-qa-6-pipe/playthrough.mp4) | 3,862 | 6 | 1 | 16 | 78 |
| Rygar | [surface](../../build/playthroughs/expanded-qa-7-surface/playthrough.mp4) | 5,365 | 17 | 5 | 18 | 266 |
| Rygar | [pipe](../../build/playthroughs/expanded-qa-7-pipe/playthrough.mp4) | 3,715 | 6 | 1 | 17 | 82 |
| Luigi | [surface](../../build/playthroughs/expanded-qa-8-surface/playthrough.mp4) | 5,721 | 17 | 5 | 11 | 120 |
| Luigi | [pipe](../../build/playthroughs/expanded-qa-8-pipe/playthrough.mp4) | 4,239 | 6 | 1 | 12 | 52 |
| Bass | [surface](../../build/playthroughs/expanded-qa-9-surface/playthrough.mp4) | 5,707 | 17 | 5 | 165 | 1776 |
| Bass | [pipe](../../build/playthroughs/expanded-qa-9-pipe/playthrough.mp4) | 3,968 | 6 | 1 | 54 | 1136 |
| Ryu | [surface](../../build/playthroughs/expanded-qa-ryu-10-surface/playthrough.mp4) | 5,290 | 17 | 5 | 100 | 534 |
| Ryu | [pipe](../../build/playthroughs/expanded-qa-10-pipe/playthrough.mp4) | 4,094 | 6 | 1 | 12 | 48 |
| Sophia | [surface](../../build/playthroughs/expanded-qa-11-surface/playthrough.mp4) | 5,260 | 17 | 5 | 83 | 258 |
| Sophia | [pipe](../../build/playthroughs/expanded-qa-11-pipe/playthrough.mp4) | 3,699 | 6 | 1 | 80 | 108 |

## Findings

Five findings are confirmed; the brief wall-contact clip is a follow-up. Frame numbers refer to end-frame telemetry; rendered OAM changes can appear one captured frame later.

- **Luigi, 46.01s / frame 2765 (confirmed):** After the airborne flower upgrade, releasing A clamps Luigi to the minimum jump height. In one frame he moves 39 pixels down and eight left. The jump-release code rewinds his position instead of ending the rise. [Sequential frames](../../build/playthroughs/expanded-issue-evidence/luigi-powerup-snap.png) · [Clip](../../build/playthroughs/expanded-issue-evidence/luigi-powerup-snap.mp4)
- **Bass, 9.15s / frame 550 (confirmed):** Bass can exceed eight sprites on a scanline even without enemies. The two routes have 2,912 overloaded frames (30.1%); priority rotation cannot make every part visible on each frame. [Sequential frames](../../build/playthroughs/expanded-issue-evidence/bass-sprite-overload.png) · [Clip](../../build/playthroughs/expanded-issue-evidence/bass-sprite-overload.mp4)
- **Bass, 20.25s / frame 1217 (confirmed):** Airborne shooting selects the standing attack pose, including its grounded leg position, instead of a separate airborne shooting pose. [Sequential frames](../../build/playthroughs/expanded-issue-evidence/bass-air-shot.png) · [Clip](../../build/playthroughs/expanded-issue-evidence/bass-air-shot.mp4)
- **Ryu, 47.34s / frame 2845 (confirmed):** Airborne melee selects the ground slash sequence. The pinned reference has a separate falling attack sequence. [Sequential frames](../../build/playthroughs/expanded-issue-evidence/ryu-air-slash.png) · [Clip](../../build/playthroughs/expanded-issue-evidence/ryu-air-slash.mp4)
- **Sophia, 47.22s / frame 2838 (confirmed):** Hover movement works, but the wheel exhaust/flame animation and sustained hover sound from the pinned reference are absent. The sound is never queued, so common-SFX queue checks cannot detect its absence. [Sequential frames](../../build/playthroughs/expanded-issue-evidence/sophia-hover.png) · [Clip](../../build/playthroughs/expanded-issue-evidence/sophia-hover.mp4)
- **Sophia, 57.72s / frame 3469 (follow-up):** The generated wall art is unrotated. This route contains only one wall-contact frame, so a sustained wall-climb replay is needed to judge the visible transition against the reference. [Sequential frames](../../build/playthroughs/expanded-issue-evidence/sophia-wall.png) · [Clip](../../build/playthroughs/expanded-issue-evidence/sophia-wall.mp4)

These are audit findings; the Contra optimization does not fix these character-specific defects.

Later checkpoint: the [Bass/Rygar audit](bass-rygar-audit.md) corrects Bass's body-only sprite overload and airborne aiming poses, together with his default-buster and movement mismatches. The recordings and counts above remain evidence for their original ROM hash.

## Checks and limits

Every captured frame was decoded. Automated checks found no stage-row vertical shifts, bad HUD split timing, missing **queued common SFX**, mushroom palette errors, or abnormal mushroom-emergence motion. Pit and Rygar raised no crouch/air-attack pose flags. PCM audio is present in all twelve captures. Common-SFX voice checks do not verify every source-specific sound or waveform identity.

Manual inspection covered animation-context contact sheets, route milestones, item-emergence sequences and consecutive frames around findings. Bass has 22 pose/CHR timing candidates across the two routes; the inspected bank-transition sequence looks normal, so those candidates are not reported as confirmed corrupted graphics.

Lag counts measure overloaded update frames; sprite counts measure hardware eight-sprites-per-scanline overload, not full-body disappearance. Native sprite limits remain enabled. The final stop callback is one frame beyond AVI capture; the trace and endpoint screenshot preserve that control check.

The initial Ryu surface replay did not clear and was rejected. The accepted retry uses a fixed controller tail to traverse the flagpole approach. No level-clear recording writes game RAM or registers. Mesen starts with randomized RAM, so these are pinned successful recordings rather than a claim that uninitialized power-on state is identical on every replay.

Each directory includes native AVI/PCM, a viewing MP4, manifest, hashes, actual controller inputs, read-only state/animation/PPU/APU traces, coverage events, and review sheets. Explicit injected stress fixtures used later for Contra are separate.

## Checkpoint and reproduction

MMC3 SHA-256: `4a59408c586865334312872b2727f272c93a3339409c6b2cf2fd59d25f6aad70`

```powershell
python tools/playthroughs/review.py build/playthroughs/expanded-qa-6-surface
python tools/playthroughs/summarize_expanded.py
```

Reference comparison uses the pinned extracted Crossover 2 scripts under `reference/crossover2/extracted/scripts/com/smbc/characters/` and the generated pose mappings in `tools/reference/build_expanded_assets.py`.
