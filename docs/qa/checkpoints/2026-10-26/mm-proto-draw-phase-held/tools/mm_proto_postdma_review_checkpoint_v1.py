"""Publish a small held-result review packet; never install, stage or launch."""
from pathlib import Path
import difflib, hashlib, json, shutil

R = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
P = D / 'mm-proto-postdma-native-ready-v3'
C = D / 'mm-proto-postdma-composed-v1'
BASE = D / 'root-chip-hud-composed-v1'
POST = D / 'current3cee-postdma-mask-v1/canonical-v2'
OUT = R / 'docs/qa/checkpoints/2026-10-26/mm-proto-draw-phase-held'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(p):
    return json.loads(Path(p).read_text())


def main():
    OUT.mkdir(parents=True, exist_ok=False)
    assert sha(C / 'candidate.nes') == 'b0c152fa0c588a7df28171e1c673a8db31e2769c5e9114768742e328f1134a99'
    assert sha(BASE / 'candidate.nes') == '3cee18caa732b2e85e3bdb00faf719223324f9bf24e72dd30c56be355da33b99'
    source_receipt = C / 'ready-v1/receipt.json'
    assert sha(source_receipt) == '36d1bff5f8b8f74beca4122fd8de70ef609b0fc686728b306a7a3a8b4de9c3d6'
    source = load(source_receipt)
    assert source['source_only'] and source['changed_PRG_bytes'] == {'66': 144}
    review = load(P / 'review-megaman-v3/proof.json')
    negative = load(P / 'replay-negative-v1/proof.json')
    prefix = load(P / 'prefix-pixels-v1/proof.json')
    assert not review['native_route_and_independent_replay_passed']
    assert not negative['passed'] and negative['strict_replay_failure_preserved']
    assert prefix['compared_frames'] == 68 and not prefix['strict_full_replay_passed']
    changed = []
    for old in (BASE / 'source').rglob('*'):
        if old.is_file() and old.suffix.lower() not in ['.nes', '.dbg', '.lbl', '.map']:
            rel = old.relative_to(BASE / 'source')
            new = C / 'source' / rel
            assert new.is_file(), str(rel)
            if sha(old) != sha(new):
                changed.append(rel.as_posix())
    assert sorted(changed) == ['smb1base-mmc5-expanded.cfg', 'src/protoman_legacy_shots.inc', 'src/reset.s']
    overlay = {}
    patch = []
    for rel in sorted(changed):
        old, new, out = BASE / 'source' / rel, C / 'source' / rel, OUT / 'source-overlay' / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(new, out)
        overlay[rel] = dict(parent_sha256=sha(old), candidate_sha256=sha(new), copied_sha256=sha(out))
        assert overlay[rel]['candidate_sha256'] == overlay[rel]['copied_sha256']
        patch.extend(difflib.unified_diff(old.read_text().splitlines(keepends=True), new.read_text().splitlines(keepends=True), fromfile='parent3cee/' + rel, tofile='held-b0/' + rel))
    (OUT / 'source-overlay/review.patch').write_text(''.join(patch))
    (OUT / 'source-overlay/bindings.json').write_text(json.dumps(overlay, indent=2) + '\n')
    # Exact final reports/proofs only; large game data and capture streams stay
    # external. Their immutable manifest/proof hashes remain reviewable here.
    copies = {
        'source-controls/receipt.json': source_receipt,
        'source-controls/composition-proof.json': C / 'proof.json',
        'source-controls/cpu-proof.json': C / 'cpu-v1/proof.json',
        'source-controls/callers-proof.json': C / 'callers-v1/proof.json',
        'native/final-strict-negative.json': P / 'replay-negative-v1/proof.json',
        'native/final-strict-negative.txt': P / 'replay-negative-v1/report.txt',
        'native/opaque-visibility-proof.json': P / 'review-megaman-v3/proof.json',
        'native/frame-summary.json': P / 'review-megaman-v3/frame-summary.json',
        'native/matched-prefix-proof.json': P / 'prefix-pixels-v1/proof.json',
        'native/matched-prefix-frames.json': P / 'prefix-pixels-v1/frames.json',
        'native/failure1-MmSlot.json': D / 'mm-proto-postdma-native-ready-v1/first-failure-v1/proof.json',
        'native/failure2-host-exit.json': D / 'mm-proto-postdma-native-ready-v2/host-exit-negative-v1/proof.json',
        'native/readiness.json': P / 'readiness.json',
        'native/root-grant.json': P / 'ROOT-grant.json',
        'native/host-only-readiness.json': P / 'host-only-proof-v2/readiness.json',
        'samples/matched-prefix-actual-pixels.png': P / 'prefix-pixels-v1/matched-prefix-actual-pixels.png',
        'samples/residual-body-actual-pixels.png': P / 'prefix-pixels-v1/residual-body-actual-pixels.png',
    }
    for name, p in copies.items():
        q = OUT / name
        q.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, q)
        assert sha(q) == sha(p)
    tool_names = [
        'mm_proto_postdma_replay_negative_v1.py',
        'mm_proto_postdma_native_review_v1.py',
        'mm_proto_postdma_native_review_v2.py',
        'mm_proto_postdma_native_review_v3.py',
        'mm_proto_postdma_prefix_pixels_v1.py',
        'mm_proto_postdma_review_checkpoint_v1.py',
    ]
    tools = {}
    for name in tool_names:
        p, q = R / 'tools/audit' / name, OUT / 'tools' / name
        q.parent.mkdir(exist_ok=True)
        shutil.copyfile(p, q)
        tools[name] = dict(owned_workspace_path=str(p), sha256=sha(p), exact_checkpoint_copy_sha256=sha(q),
                           classification='unused draft; requires passing direct proof and was never run' if name.endswith('native_review_v1.py') else 'superseded v2 geometric split; retained, never relabeled' if name.endswith('native_review_v2.py') else 'actual final checker/freezer')
    (OUT / 'tools/bindings.json').write_text(json.dumps(tools, indent=2) + '\n')
    external_paths = [
        BASE / 'candidate.nes', BASE / 'source-manifest.json',
        POST / 'candidate.nes', POST / 'proof.json', POST / 'source-manifest.json',
        C / 'candidate.nes', C / 'source-manifest.json', C / 'candidate.lbl', C / 'candidate.map',
        C / 'ready-v1/catalog.json', C / 'ready-v1/source-bindings.json', C / 'ready-v1/dependencies.json', C / 'ready-v1/source.zip',
        P / 'bindings.json', P / 'environment.json', P / 'ROOT-grant.json', P / 'launch.json', P / 'exit.json',
        P / 'runner.py', P / 'capture.py', P / 'coordinator.py',
        P / 'mm_proto_postdma_native_observer_v1.lua', P / 'tmnt_static_exec_dispatcher_v1.lua',
        P / 'observer-name-reconciliation.json', P / 'replay-negative-v1/catalog.json',
        P / 'review-megaman-v3/opaque-row-witnesses.jsonl', P / 'review-megaman-v3/visible-shot-ages.jsonl',
        P / 'review-megaman-v3/observed-slot-episodes.jsonl', P / 'review-megaman-v3/encoded-owner-mismatches.json',
        P / 'prefix-pixels-v1/dependencies.json',
        D / 'root-megaman-lowbody-probe-v1/attribution.json',
    ]
    for p in copies.values():
        external_paths.append(p)
    # Bind the exact actual source/capture programs, not a current mutable copy.
    for name in ['inputs.csv', 'trace.csv', 'events.csv', 'render.csv', 'shot-events.jsonl', 'shot-epochs.jsonl', 'shot-guards.jsonl', 'shot-observer.json', 'result.json', 'harness.lua']:
        for run in ['megaman-easy', 'megaman-easy-direct']:
            external_paths.append(P / 'native' / run / name)
    refs = {str(p): dict(sha256=sha(p), bytes=p.stat().st_size) for p in sorted(set(external_paths))}
    (OUT / 'external-bindings.json').write_text(json.dumps(refs, indent=2) + '\n')
    readme = '''HELD MEGA MAN / PROTO MAN SHOT EXPERIMENT -- 2026-10-26

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
'''
    (OUT / 'README.txt').write_text(readme)
    paths = [OUT.relative_to(R).as_posix()]
    (OUT / 'review-files.json').write_text(json.dumps(dict(owned_review_paths=paths,
        do_not_stage_production=True, do_not_stage_external_payloads=True,
        source_overlay_scope='exact three changed text inputs versus frozen3cee; reset belongs to independently bound900',
        additional_owned_workspace_tools=[str(R / 'tools/audit' / n) for n in tool_names],
        optional_global_tools_stage=False), indent=2) + '\n')
    # Public catalog is acyclic: it catalogs every payload except itself and
    # its final proof, which separately binds the catalog hash.
    catalog = {p.relative_to(OUT).as_posix(): dict(sha256=sha(p), bytes=p.stat().st_size)
               for p in sorted(OUT.rglob('*')) if p.is_file()}
    assert all(Path(n).suffix.lower() not in ['.nes', '.nsf', '.nsfe', '.dmc', '.wav', '.mp4', '.zip', '.gz'] for n in catalog)
    (OUT / 'catalog.json').write_text(json.dumps(catalog, indent=2) + '\n')
    for n, v in catalog.items():
        assert sha(OUT / n) == v['sha256']
    result = dict(checkpoint_integrity_passed=True, source_controls_passed=True,
        strict_full_native_replay_passed=False, overall_visual_acceptance=False,
        installed=False, native_retry=False, worker_released=True,
        parent_ROM_sha256=sha(BASE / 'candidate.nes'), held_ROM_sha256=sha(C / 'candidate.nes'),
        source_overlay=overlay, source_packet_sha256=sha(source_receipt),
        exact_final_negative_sha256=sha(P / 'replay-negative-v1/proof.json'),
        actual_visibility_proof_sha256=sha(P / 'review-megaman-v3/proof.json'),
        bounded_prefix_pixels_sha256=sha(P / 'prefix-pixels-v1/proof.json'),
        public_payload_files=len(catalog), public_payload_bytes=sum(x['bytes'] for x in catalog.values()),
        catalog_sha256=sha(OUT / 'catalog.json'), external_bindings=len(refs),
        external_bindings_sha256=sha(OUT / 'external-bindings.json'),
        builder_sha256=sha(__file__), no_ROM_audio_settings_lossless_payload=True,
        staging_or_Git_actions_performed=False)
    (OUT / 'proof.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(checkpoint=str(OUT), checkpoint_integrity_passed=True,
                         strict_full_native_replay_passed=False, overall_visual_acceptance=False,
                         payload_files=len(catalog), payload_bytes=result['public_payload_bytes'],
                         proof_sha256=sha(OUT / 'proof.json')), indent=2))


if __name__ == '__main__':
    main()
