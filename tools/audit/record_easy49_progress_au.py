"""Record current identity, completed scoped work and live next actions."""
from pathlib import Path
import datetime
import hashlib
import json
import sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def record(path):
    p = R / path
    return dict(path=p.relative_to(R).as_posix(), bytes=p.stat().st_size, sha256=sha(p))


def main():
    out = V / 'root-current49-progress-au.json'
    assert not out.exists()
    cp = R / 'build/checkpoints/roster-audit-v49-link-ceiling-gq/manifest.json'
    assert sha(cp) == 'b8d20e8cab676894da899801146554f310dc4c339453c7b0897cfe92833c623f'
    old = json.loads(cp.read_text())
    for name, digest in old['source_hashes'].items():
        assert sha(R / name) == digest, name
    for build in old['builds']:
        for item in build['artifacts'].values():
            assert sha(R / item['path']) == item['sha256'], item['path']
    candidate = V / 'root49-sophia-land-fix-a'
    catalog = json.loads((candidate / 'source-catalog-e.json').read_text())
    for name, digest in catalog.items():
        assert sha(candidate / 'source-e' / name) == digest, name
    layout = json.loads((candidate / 'layout-e.json').read_text())
    for build in layout['builds'].values():
        for item in build.values():
            assert sha(R / item['path']) == item['sha256'], item['path']
    paths = [
        'build/verification/root-current49-progress-at-addendum-ix.json',
        'build/verification/root49-combined-adoption-a/preparation.json',
        'build/verification/root49-combined-preparation-negative-a.json',
        'build/verification/root49-combined-mario-a.json',
        'build/verification/root49-samus-gq-route-review-be.json',
        'build/verification/root49-combined-samus-transfer-a.json',
        'build/verification/root49-sophia-feet-packet-review-a.json',
        'build/verification/agent-lsr-sophia-feet-implementation-a/implementation-freeze.json',
        'build/verification/agent-lsr-sophia-feet-implementation-a/final-review.json',
        'build/verification/root49-sophia-land-fix-a/preparation.json',
        'build/verification/root49-sophia-land-fix-a/placement-negative-d.json',
        'build/verification/root49-sophia-land-fix-a/revision-e.json',
        'build/verification/root49-sophia-land-fix-a/source-catalog-e.json',
        'build/verification/root49-sophia-land-fix-a/layout-e.json',
        'build/verification/specialist-samus-gq-route-a/phase-index-be.json',
        'build/verification/specialist-samus-gq-route-a/phase-freeze-be.json',
        'docs/qa/easy-hard-legacy-v49.md',
    ]
    sys.path.insert(0, str(R / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(R)
    report = dict(status='ACTIVE_SCOPED_ROUTES_AND_LANDING_FIX_PROGRESS_MAIN_GQ_UNCHANGED',
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), script_sha256=sha(__file__),
        records=[record(p) for p in paths], main_checkpoint=record(cp),
        main_source_files_verified=442, main_primary_artifacts_verified=8,
        immutable_candidate_source_files_verified=455, candidate_artifacts_verified=16,
        completed=[
            'C collision native source oracles and526 exact caller reexecutions frozen;14 interrupt gaps and +900..931cycle/update cost explicitly retained. Root rehash2791files.',
            'Actual source-c Mario Easy fixed replay through2-2 onbothmappers:16991frames/0deaths,19fields and114dry takeoffs exacthistoricalCC,25nextlevelcontrols. Unrecorded.',
            'Samus GQ EasyMMC3 full ordinary independently fixed replay:28285frames/0deaths,136identifiedsupports,25nextlevelcontrols. Root rehash1534files. Nonfatalinjury preserved; GQ-only.',
            'Root landing wrapper E builds all4 and changes only49ROMbytes/map vsC, withallpriorsegmentsPC/RAM/otherROM/baselines literal. Actual landing probes restore source timer-high frames1/7; full finalaudiofreeze pending.',
        ],
        retained_negatives=[
            'Initial generated-file preparation guard found only11CRLF/LF differences; corrected actual-byte backup and normalized equality, no main mutation.',
            'Source-c landing retriggered everyupdate1..8.',
            'Private D placement moved laterbank7code; rejected before nativeadmission and replaced by new optional-tail E.',
            'Exact GQ Samus input transfer toE fails atM3deathtransition4322/M53528; identity/inputprefix pass. M3firstmotiondifference1973 correlateswithskippedupdate. Notdiagnosedsourcecollisiondefect.',
        ],
        team={
            'link_simon_ryu':'Cfreeze complete. Reusedforone targetedsuccessor fromimmutableaudioE, optimizing newflatfeetwork. Newphaseagent-lsr-sophia-feet-perf-a300MB/50MBreserve; no main edits.',
            'samus_contra_s2':'Audio E old24 actual777calls/map plusstrictIRQreview pass; +35cycles/non25call.20lifecycle/mixercases finishing. Existingphase200MB/25MBreserve; exactfinishedfreeze remains pending.',
            'mario_luigi_scrooge_s2':'SamusGQphasefrozen. ReusedforBill/Lance currentEordinaryroutes; source-e immutableguard455+16. Newphase1GB/100MBreserve. First1-2liftgap and missedsinglepollAarecontrollernegatives; ordinaryadaptationactive.',
        }, root_live_handles=[],
        storage=dict(workspace_bytes=used, global_cap_bytes=70000000000,
            authority='User explicitly chose retainlossless andraise cap;70GB allocates remaining native routes and final lossless recordings. No cleanup/deletion.',
            root_landing_fix_cap_bytes=250000000, root_landing_fix_reserve_bytes=50000000,
            root_samus_transfer_cap_bytes=200000000, root_samus_transfer_reserve_bytes=25000000),
        next_actions=[
            'Finish independent E landing/mixer/pause/old24 nativefreeze; do not treat layout alone as audioadmission.',
            'Reduce measured newSophia collision cost and verify sourceoracles/nativecrowd effect before combined sharedQAadoption.',
            'Continue Bill/Lance ordinaryroute and adapt Samus/controller transfers on finalcandidate, keeping oldGQproof scoped.',
            'Complete allroster/alternates/weaponupgrade coverage, profile/optimize laggyabilities, then finalrecordedplaythroughs withlossless retained.',
        ], main_changed=False, accepted_release=False, goal_complete=False)
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(status=report['status'], sha256=sha(out), workspace_bytes=used, global_cap_bytes=70000000000)))


if __name__ == '__main__':
    main()
