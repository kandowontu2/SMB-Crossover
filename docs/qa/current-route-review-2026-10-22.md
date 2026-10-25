# Current Mario/Bass route and footage review

Both new Easy/MMC3 routes clear all six stages through 2-2 on the unchanged HR
ROM and demonstrate 25 controllable frames of rightward movement in 2-3. Their
independent fixed replays retain byte-identical controller, position/cycle and
event logs from the discovery runs. Every native RGB frame and PCM sample in
each lossless master was verified against its retained capture parts.

| Character | Emulator / video frames | Deaths | Active-play lag frames | QA delivery |
|---|---:|---:|---:|---|
| Mario |16,997 /16,996 |0 |14 of10,631 |`Playthrough Videos/QA/Mario-Easy-through-2-2-2026-10-22-HR-QA.mp4` |
| Bass |28,424 /28,423 |0 |7,055 of21,825 |`Playthrough Videos/QA/Bass-Easy-through-2-2-2026-10-22-HR-QA.mp4` |

Mario stays small throughout this complete route. Bass uses the buster and
natural mushrooms. These recordings do not certify every weapon or upgrade,
Hard behavior, every enemy/item, or the two requested 1-1 route variants.

Every recorded frame was decoded. Mario has no motion, CHR-on-lag, visible
scroll-timing, background-shift or background-flash candidates in this bounded
recording. Its 28-frame contact sheet was visually inspected. Bass has no late
scroll/CHR/background-shift candidates, but has 19 player-position candidates.
All 33 native frames surrounding the underground and water candidates were
extracted into two sheets and visually inspected. A clean background scan does
not exclude a player-geometry defect.

## Confirmed Bass sideways snap — unfixed

The late 2-2 coral sequence visibly moves Bass left and right by about 14 pixels.
The native footage, exact inputs and a passive collision capture are retained.
Thirty-four complete terrain calls have entry/return flat 10,240-byte RAM
snapshots, registers and position writes. The entire diagnostic trace is a
literal prefix of the independently verified full movie; the diagnostic stops
at its intentional frame limit and is not offered as another full clear.

A second passive capture adds all 3,806 ordered CPU writes from those same
34 calls. Reexecuting the unchanged compiled ROM reproduces every final RAM
byte, physical register, bank, mapper selector, ordered write and instruction
cycle exactly. No interrupt or external hardware read occurs inside this
bounded window. The initial negative verifier is retained; Mesen reports an
already-fetched PC at write callbacks, now bound to each actual producer's
decoded instruction length (including JSR's earlier stack pushes).

The actual writes come from `SamusStopAtWallBanked` in bank10: eight +14,
seven -14 and two +16 pixel corrections. They alternate zero-speed side
admission while the native deep-foot probes use offsets30/33 against tile105.
The source hitbox/axis/previous-contact admission needs correction. No
velocity-only bypass, terrain change or gameplay fix has been admitted.
The two underground motion candidates at8190/8191 remain separately unresolved.

Bass also retains the known face/world palette conflict and dense-scene lag
and sprite overload. This is a QA recording, not a finished promotional movie.

## Audio review correction

`BassAudioBegin` writes `$ff` as an idle marker each update, and
`BassSourceAudioTick` explicitly skips request handling for it. The reviewer
now reports those markers separately. The original report is retained:
22,547 idle markers were excluded, removing11,377 false unconfirmed-request
flags. The remaining1,680 flags still require cue/priority review; they are
not automatically missing sounds. Native PCM provenance does not by itself
prove source waveform or cue parity.

## Additional controller progress

A separate native Mario route collects the first mushroom, then the flower
at poll1812. A cold-boot verified branch crosses the late 1-1 pipe with Fire
Mario retained; continued play clears the flag and enters1-2 at frame3972.
That powered route currently stalls at1-2 X610. The failed controller attempts
are preserved; no terrain defect is inferred from the policy failure.

The MMC3 Mario tape transferred to MMC5 clears1-1 but dies in1-2 at4747.
That is a tape-transfer failure, not a crash or proof the stage cannot clear.

The current HR full-route set is Mario, Bass and Rygar. Other current identities,
Hard routes, full arsenals, source-fidelity repairs and final films remain open.
The new level audit and player's guide are separate deliverables; no level
change was bundled into these checks.

Evidence: `build/verification/current-route-review-ir/summary.json`; native
packets `root-mario-av-if-0-v0-mmc3`, `root-bass-av-im-9-v0-mmc3` and
`root-bass-collision-is-9-v0-mmc3`. The second capture is
`root-bass-collision-ix-9-v0-mmc3`; complete unchanged-call CPU evidence is
`build/verification/bass-collision-cpu-iz/summary.json`. Both mapper ROMs and the full HR gameplay
source/asset hashes remain unchanged. The workspace remains below30 GB.
