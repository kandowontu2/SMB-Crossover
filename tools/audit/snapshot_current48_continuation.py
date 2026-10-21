"""Pin accepted48 and the newly observed Ryu wall defect without promoting a fix."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/playthroughs'))
from roster_run import workspace_bytes


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tag', required=True)
    args = parser.parse_args()
    assert args.tag and all(c.isalnum() or c in '-_' for c in args.tag)
    output = ROOT / 'build/verification' / f'root-current48-progress-{args.tag}.json'
    assert not output.exists(), 'Keep each historical continuation receipt'
    checkpoint = ROOT / 'build/checkpoints/roster-audit-v48'
    manifest = json.loads((checkpoint / 'manifest.json').read_text())
    assert sha(checkpoint / 'manifest.json') == 'fd0770c5058acd0522008f341427878495dadcbb7dd8cbf0e3db1eb934684102'
    assert manifest['status'] == 'accepted-bounded-component' and not manifest['goal_complete']
    assert all(sha(checkpoint / f'smb-crossover-{m}.nes') == h for m, h in manifest['roms'].items())
    with zipfile.ZipFile(checkpoint / 'source-v48.zip') as archive:
        sources = json.loads(archive.read('archived-file-hashes.json'))
    changed = [name for name, digest in sources.items() if sha(ROOT / name) != digest]
    assert len(sources) == 403 and set(changed) == {'README.md'}
    refs = {
        'accepted48': 'build/checkpoints/roster-audit-v48/manifest.json',
        'bound761': 'build/checkpoints/roster-audit-v48/validation/bound-summary.json',
        'crowd_review': 'build/verification/goomba47-48-crowd-review-a.json',
        'image_and_pcm': 'build/verification/goomba47-48-ppu-samus-e-a/report.json',
        'existing_final_recordings': 'build/verification/capture45-full-route-review-a/report.json',
        'ryu_fixed': 'build/roster-through-2-2/root48-ryu-fixed-a-10-v0-mmc3/manifest.json',
        'ryu_fixed_review': 'build/verification/ryu48-full-route-review-fixed-a/report.json',
        'ryu_passive_prefix': 'build/verification/root48-ryu-wall-passive-first-a-review.json',
        'ryu_passive_metadata': 'build/verification/ryu48-wall-drift-readonly-a/hooks.json',
        'bill_j': 'build/roster-through-2-2/root48-bill-adaptive-j-3-v0-mmc3/manifest.json',
        'link_batch2': 'build/verification/link47-route-lifts-batch2/handoff.json',
        'samus_f': 'build/verification/agent47-samus-controller-batch-f/freeze-final.json',
        'samus_g_compilation_negative': 'build/verification/agent47-samus-g-native-negative-a/actual-negative.json',
        'rebuild_listings_compaction': 'build/verification/root-completed-rebuild-lst48-compaction-a/receipt.json',
        'accepted_listings_compaction': 'build/verification/mm-owned-accepted-checkpoint-lst-plan-20261018/root-compact-a.json',
    }
    references = {key: dict(path=name, sha256=sha(ROOT / name)) for key, name in refs.items()}
    bound = json.loads((ROOT / refs['bound761']).read_text())
    assert bound['result'] == 'passed' and bound['case_count'] == bound['passed'] == 761
    assert bound['failed'] == 0 and bound['single_full_run']
    fixed = json.loads((ROOT / refs['ryu_fixed']).read_text())
    assert fixed['verified_through_2_2'] and not fixed['result']['deaths']
    assert fixed['result']['frames'] == 23432 and fixed['full_frame_audit']
    probe = json.loads((ROOT / refs['ryu_passive_prefix']).read_text())
    assert probe['result'] == 'read-only-diagnostic-exact-control-prefix'
    assert len(probe['streams']) == 9 and all(r['literal_control_prefix'] for r in probe['streams'].values())
    final_paths = [
        ROOT / 'build/roster-through-2-2/root45-mario-record-a-0-v0-mmc3',
        ROOT / 'build/roster-through-2-2/root45-luigi-record-a-8-v0-mmc3',
    ]
    for folder in final_paths:
        item = json.loads((folder / 'manifest.json').read_text())
        assert item['recording_verified'] and item['verified_through_2_2']
        assert item['rom_sha256'] == manifest['roms']['mmc3']
    report = dict(
        status='progress-full-goal-incomplete', goal_complete=False,
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        script_sha256=sha(Path(__file__)), accepted_checkpoint=checkpoint.name,
        roms=manifest['roms'], references=references,
        runtime_sources_unchanged_since_acceptance=True,
        postacceptance_source_archive_differences=changed,
        full_regression=dict(status='passed', cases=761, single_full_run=True),
        current_hash_final_recordings=2,
        current_hash_additional_fixed_clear=dict(character='Ryu', frames=23432, deaths=0,
            recording=False, clean_movement=False,
            qualification='All nine discovery/replay audit CSVs match. Nine large horizontal steps require review; the first now has a guarded native causal receipt. Do not label traversal success as complete source/AV fidelity.'),
        ryu_defect=dict(first_frame=1231, dx=-9, passive_frames=1320,
            passive_receipts=515, expected_native_exit=1, expected_reason='frame limit',
            emulated_state_writes=False, control_prefix_streams_equal=9,
            observed='Attached movement assigns walking qVX101035; the lower side probe leaves tile18 atY176 for emptyY175, wall contact clears, and right drift later ends in a9px correction.',
            source='Ryu.movePlayer returns in ST_CLIMB before walking VX assignment. Attach and climb bounds also require source body and ground geometry.',
            repair_applied=False, final_ryu_capture_deferred=True,
            next='Review a source-backed complete wall lifecycle repair and new frozen regression before modifying the ROM; a VX-only stop would not maintain valid wall contact.'),
        routes=dict(
            bill='J passes all three ceiling firebars in1-4, then ordinary low-firebar contact atX1298/Y128 on frame16613; no new ROM defect inferred.',
            link='E clears1-4 and reaches2-1. Prepared F remains unrun after prior workspace preflight stopped before launch.',
            samus='F/Z clears five land stages and reaches2-2X2413. One authorized G fails Lua compilation before gameplay; negative preserved. Corrected policy preparation must pass an actual parser before another authorized run.'),
        settings='Outlines defaultOFF; optionrowgold. Samus ordinary stomp follows2.02 false; acquired ScrewAttack supplies eligible contact attacks.',
        lag='48 saves about1343 measured foregroundcycles/update in equal-redraw six-Goomba rows. Dense scenes still skip redraws; all75 negative metrics and the literal PCM timing difference remain retained.',
        storage='34 completed successful rebuild LSTs and16 old accepted canonical LSTs losslessly gzipped with roundtrip SHA checks and all other files protected. No route cleanup, deletion of negatives or retry of rejected cleanup.',
        workspace_bytes=workspace_bytes(ROOT), workspace_cap_bytes=30_000_000_000,
        remaining='Source-backed movement/weapon repairs, every special/alternate/upgrade audit, final current-hash ordinary routes and recordings for all14 characters, audiovisual review and further lag optimization remain open.')
    assert report['workspace_bytes'] < report['workspace_cap_bytes']
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], report['workspace_bytes'], 'bytes; accepted48,2finalrecordings,Ryuwallrepairunapplied')


if __name__ == '__main__':
    main()
