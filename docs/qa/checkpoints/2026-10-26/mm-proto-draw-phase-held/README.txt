HELD MEGA MAN / PROTO MAN SHOT EXPERIMENT -- 2026-10-26

Status: SOURCE CONTROLS PASS; STRICT REPLAY FAIL; OVERALL VISUAL FAIL.
Not installed. No Proto run, retry, full-ability or matched performance claim.
This checkpoint is a rollback/review artifact, not an accepted game update.

WHAT CAN BE RESTORED
Parent3cee18caa732b2e85e3bdb00faf719223324f9bf24e72dd30c56be355da33b99.
Held b0c152fa0c588a7df28171e1c673a8db31e2769c5e9114768742e328f1134a99.
Copy exactly the three text files in source-overlay onto the frozen parent
source. bindings.json verifies every old/new file hash. All other common
production inputs were compared and are exact. Do not overlay current live
source blindly or include inherited stale candidate.nes/debug files in a build.

src/reset.s and part of cfg are ROOT/B's genuine900 post-DMA mask repair,
not our shot implementation. Their parent canonical proof is externally bound.
The shot-only difference versus900 is exactly144 bytes in PRG66:3-byte hook
plus141-byte helper/table in previouslyFF B9A8..BA34. RAM/CHR/all61,210 old
symbols/other banks are exact versus900. Ordinary MMC3/MMC5 hashes are exact.
Exact public source helper and cfg declaration are retained; no fake aliases.

SOURCE ALGORITHM AND FINITE CHECKS
The existing SsDrawFirst draw clock, advanced by the real NativeDraw producer,
uses physical-start wheel[0,1,2,0,3,1,0,2,1,3]. Pick the first live slot in
descending cyclic order. One live shot is always selected; each persistent
physical slot gets a turn within5 completed source constructions even when
other live flags change. No new RAM, live-slot/age/physics/art changes.
Source timing versus original0/1/2/3/4 live shots:0,+136..137,-193,-523,-853
cycles. Clipped two-live can add40. These positive costs are not waived.
Fresh composed controls:13,376 full shot cases,164 actualIRQ cases,512
genuine-producer cases and152 complete foreign DrawAll cases PASS. Complete
caller/state/original-selected-OAM oracle details are in the bound receipts.
Oracle exclusions are only arranged4 source type bytes, deadstack01C0..01FF
and virtualB flag; no runtime or physical visibility assertion was weakened.

NATIVE OUTCOME -- TWO LAUNCHES ONLY
MegaEasy discovery and independent direct capture each clear1-1 atframe5175,
0deaths. Direct retains4975 actualPPU frames200..5174. Ten otherCSV files are
byte-exact, all3 orderedJSONL and7 summaries semantically exact. Every actual
source/physical256-byte DMA comparison passes3390 times.2851 constructions
and publications;3536 genuineNMI andIRQ checks; minimumSP168; declared5SMC
and bank/CHR guards pass. These are candidate-only finite routes.

The ORIGINAL strict checker still FAILS events.csv. Discovery logs3 extra
pregame sfx-0104 rows at204/205; replay's observer-local selectionDone flag
does not turn true until actualengine8 at371. runner.py70/79/80 and actual
harness.lua120/126..137/140/146 explain the logging boundary. Actual replay
menu queue values were not logged and are not invented. Every event row
from371 onward is exactly equal. There is no passing direct/proof.json and
the overall native strictFAIL is preserved. ROOT has seen this same pregame
logger asymmetry on published3cee; it is not used to waive the strict result.

Earlier failures remain: missing MmSlot config stopped at firstAdmission;
the next attempt exited at the240-second host timeout without a Lua failure.
MmSlot binding/mocks and only host timeout240->1200 were corrected separately.
The unused review_v1 checker is retained and labeled unrun; review_v2 is
superseded byv3's actual geometric lower-body split, not retroactively changed.

ACTUAL VISIBILITY -- STILL BROKEN
2,647 continuous-live five-construction windows pass with no clock break.
That source property does not guarantee physical publication or opaque pixels.
Slots1/2/3 have observed live no-opaque-shot gaps9/12/6 visible frames across
3/4/2 DMA epochs.65 encoded old-image versus latest-DMA type/age mismatches
remain unassigned: held images and reused slots are not unique actor IDs.
The observed episode definition/reset and raw/offscreen limits are explicit.
Among3537 visible observations:1671 exceed8 rectangle candidates per scanline;
803 have lower-half body source-row omissions,775 clean of observed hurt,
invulnerability/death/slide.7,540 clean lower-half opaque part-rows are lost.
Opaque part-row counts can overlap and are not unique finalRGB pixels.
Admitted sprites may still be occluded. EndFrameCHR snapshots do not prove
all mid-scanline mappings. No universal visibility/fairness bound is claimed.
Residual actual frames2689..2691 show hair/face with most body missing.

BASELINE COMPARISON AND SAMPLES
Exact full input/CPU trace prefix with3cee ends438; first trace difference439
is NmiSkipped35vs34. First controller difference is poll652. Only active
frames371..438 (68) are a matched prefix:14RGBexact/54different;8,927changed
pixels. Literal403/404 images show3cee hair-only/3shots andb0 body/1shot,
but baseline physical OAM ownership is not recorded there (starts501).
No later same-numbered-frame paired body recovery/no-harm claim is made.
Sample sheets copy actual complete256x240 RGB captures, at integer2x nearest
neighbor; captions are outside source pixels. SourcePNG/index hashes bound.
Frame372 also exposes a b0 initial-active vertical wrap against normal3cee.
ROOT separately found7 one-frame menu wraps194/206/218/230/242/254/266.
All6 programmed menu guards passing did not establish visual acceptance.
Overall visual acceptance is explicitly FALSE, regardless of shot improvement.

REPRODUCIBLE REVIEW
Native inputs/host/state/settings remain external and immutable; this packet
contains NO ROM, NSF/audio, user settings or lossless capture payloads.
external-bindings.json binds full ready-source ZIP/manifests, exact scripts,
raw guard/ownership streams and original negative catalog. No native rerun
or preparation is authorized by this document. Source/control bundles are
referenced rather than duplicated. Existing source-only public checkpoint:
docs/qa/checkpoints/2026-10-26/mm-proto-shot-mux-v1 (c5 predecessor only).

Final offline commands (P=external mm-proto-postdma-native-ready-v3):
python -B tools/audit/mm_proto_postdma_native_review_v3.py --route
 P/native/megaman-easy --rom external/mm-proto-postdma-composed-v1/candidate.nes
 --output NEW-EMPTY-DIRECTORY
The prefix-pixels and checkpoint freezers use fixed immutable inputs and
create-only output paths; do not rerun into frozen existing directories.
No installation, Git operation, native launch or settings write is performed.
