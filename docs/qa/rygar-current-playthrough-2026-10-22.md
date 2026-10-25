# Current Rygar Easy playthrough and review

The current HUD FL MMC3 ROM now has an independently verified ordinary-controller clear of1-1,1-2,1-3,1-4,2-1 and2-2, followed by25 controllable frames in2-3 and actual rightward movement. The20681-emulator-frame replay has zero deaths. Inputs never grant a character, power, ammo, position or terrain. Search checkpoints were unedited; final proof replays start from power-on without state loads. Power forms0 and1 occur, so this does not establish every upgrade or alternate attack.

The20680-image recording lasts344.100 seconds. Native ZMBV parts, continuous48kHz PCM, the verified lossless RGB/PCM master and MP4 delivery are all retained. The master assembly verifies every RGB frame and PCM sample against its native inputs. The MP4 has real NES audio with peak-12.2dBFS. This is a QA recording; remaining palette and character-fidelity work prevents calling it final.

A logging weakness was found during review: the old scroll observer retained only scanlines30..38, which could miss the very late writes under investigation. The observer now records every visible scanline, the actual rendering-enable state and physical writer identity. A separate complete replay has byte-identical inputs, CPU/position trace, committed OAM/CHR, render and audio-event logs to the recorded replay. Its78028 visible-write records include73392 writes during active rendered gameplay, all on scanline31. This bounded complete log supports the absence of late writes in this replay; older HUD-window logs do not prove that.

Every20680 recorded frame was decoded and correlated. The automated review found zero split-timing, lag-CHR, motion, vertical-stage-shift or background-flash candidates. All10350 logged source SFX events have voice ownership and physical audio writes; this is not waveform parity or a claim of human listening. The active run still has847 sprite-overload frames and2265 lag-NMI frames, so flicker and lag remain optimization work.

Both bounded contact sheets and twelve consecutive native frames around1:14.9 were inspected. The underground brick debris is brown/orange against cyan world bricks. This confirms the already diagnosed shared sprite-palette3 conflict on current Rygar as well as retained Bass footage. It remains unrepaired. The exact sequence is in build/verification/rygar-final-review-ft/underground-brick-sequence.png.

Above-water excursions were also checked against both pinned Character sources: their shared update changes gravity above the water surface rather than imposing a generic top clamp. No artificial ceiling was added. Rygar's custom movement/animation and complete disk/upgrade fidelity still need their separate original-game checks.

The delivered QA copy is Playthrough Videos/QA/Rygar-Easy-through-2-2-2026-10-22-FL-QA.mp4, with its fixed input stream and scope receipt beside it. Original recordings were not replaced. The source packet is build/roster-through-2-2/root-rygar-current-fl-av-fq-7-v0-mmc3; the full visible-write replay is root-rygar-full-visible-fr-7-v0-mmc3. Evidence aggregate: build/verification/rygar-final-review-ft/summary.json.

The overall goal remains active: other current-ROM character clears, both behavior modes, every special/alternate weapon and upgrade, private component composition, remaining palette/fidelity repairs, lag work and the final roster recordings are unfinished. All captures and negative attempts remain under the user-approved100GB cap.

Successor: Rygar's shared world palette defect is repaired in the GA checkpoint. The original FL recording and this historical finding are retained; see rygar-world-palette-2026-10-22.md and build/verification/world-palette-progress-gd/summary.json for the corrected current recording.
