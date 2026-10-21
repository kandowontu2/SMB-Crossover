"""Add the closed native diagnostics to the immutable earlier continuation."""
from pathlib import Path
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
    output = ROOT / 'build/verification/root-current48-progress-c.json'
    assert not output.exists()
    previous = ROOT / 'build/verification/root-current48-progress-b.json'
    parent = json.loads(previous.read_text())
    cp = ROOT / 'build/checkpoints/roster-audit-v48'
    manifest = json.loads((cp / 'manifest.json').read_text())
    assert sha(cp / 'manifest.json') == 'fd0770c5058acd0522008f341427878495dadcbb7dd8cbf0e3db1eb934684102'
    assert all(sha(cp / f'smb-crossover-{m}.nes') == h for m, h in manifest['roms'].items())
    with zipfile.ZipFile(cp / 'source-v48.zip') as archive:
        sources = json.loads(archive.read('archived-file-hashes.json'))
    assert {n for n, h in sources.items() if sha(ROOT / n) != h} == {'README.md'}
    names = {
        'ryu_all_nine_native_origins': 'build/verification/root48-ryu-wall-passive-all-a-review.json',
        'ryu_source_proposal': 'build/verification/ryu48-wall-drift-readonly-a/freeze.json',
        'ryu_new44_fixture': 'build/verification/ryu-wall49-component-preparation-a/fixture-freeze.json',
        'ryu_old48_mmc3_negative': 'build/verification/ryu-wall49-component-preparation-a/binding48-mmc3/native-output/result.json',
        'ryu_old48_mmc3_negative_log': 'build/verification/ryu-wall49-component48-mmc3-negative-a.log',
        'samus_h': 'build/verification/agent47-samus-h-native-a/actual-receipt.json',
        'samus_i': 'build/verification/agent47-samus-i-native-a/actual-receipt.json',
        'samus_j': 'build/verification/agent47-samus-j-continuation-a/actual-receipt.json',
        'mm_samus_additional_profile': 'build/verification/mm-bass-v48-expanded-profile-a/final-receipt.json',
        'bass_profile_continuation': 'build/verification/mm-bass-v48-expanded-profile-c9-continuation-a/final-receipt.json',
        'bass_profile_all3_report': 'build/verification/mm-bass-v48-expanded-profile-c9-continuation-a/report.json',
        'old_accepted_debug_compaction': 'build/verification/root-accepted-dbg48-compaction-preparation-a/root-compact-a.json',
    }
    references = {key: dict(path=name, sha256=sha(ROOT / name)) for key, name in names.items()}
    compaction = json.loads((ROOT / names['old_accepted_debug_compaction']).read_text())
    assert compaction['result'] == 'passed-lossless-compaction'
    assert compaction['net_savings_bytes'] == 185575262
    assert sum(s['step'] == 'raw-compacted' for s in compaction['steps']) == 16
    unit = json.loads((ROOT / names['ryu_old48_mmc3_negative']).read_text())
    assert unit['cases'] == unit['completed'] == 44 and unit['failures'] == 47
    observed = json.loads((ROOT / names['ryu_all_nine_native_origins']).read_text())
    assert observed['result'] == 'all-nine-native-foot-clamp-origins-confirmed'
    assert len(observed['cases']) == 9 and observed['native_receipts'] == 4751
    report = dict(status='progress-full-goal-incomplete', goal_complete=False,
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), script_sha256=sha(Path(__file__)),
        previous=dict(path=previous.relative_to(ROOT).as_posix(), sha256=sha(previous)),
        accepted_checkpoint=cp.name, roms=manifest['roms'], references=references,
        runtime_source_unchanged=True, full_regression_cases=761,
        final_current_hash_recordings=parent['current_hash_final_recordings'],
        ryu='All9 actual native foot-clamp origins confirmed with4751 guarded receipts and9 literal-equal full audit streams. Source phase geometry independently classified for first grab. Runtime repair/third final recording remain unapplied/deferred.',
        new_component_negative='Frozen44 seeded arenas complete with47 accumulated errors on old48MMC3. This is NOT47 independent game bugs: setup/coverage and possible short-lived-projectile observer gaps require classification. M5 baseline and candidate positive not run. Any proven fixture repair must retainV1 and use a new frozenV2 without weakening source expectations.',
        samus='H reaches2481 and loses a life. I passes that encounter, stays alive through28000 atX2546, then same-policy extendedJ dies28090 atX2658/Y79 to actual slot2ID11Cheep2669/Y83. J first27999 inputs and28000 trace rows exactly matchI. All five land stages retain clears;2-2 remains incomplete. K host-only next-controller preparation requested; no further native authorization.',
        additional_lag_profile=dict(native_calls=3, matched_updates=3600, gameplay_fields=204,
            original_timing_and_render_receipts_equal=True,
            six_goomba_off_walking_redraws='30/60 for MegaMan,Samus,Bass',
            worst_work_deficit_cycles=dict(megaman=4939, samus=3352, bass=5431),
            qualified_preceding_NMIs=3600, duplicate_or_reused_NMI_serials=0,
            scope='Seeded arenas only. Inclusive parent/child costs must not be summed. Current audio and enemy work exceed deadline; tiny terrain90-132cycle proposal remains unimplemented and cannot promise60fps.'),
        storage='16 additional OLD accepted35/36/37/39/40/41/42/43 canonical DBG files losslessly gzipped,185575262B saved,11635 other checkpoint files pinned unchanged. No route/negative cleanup. Exact restoration remains available.',
        native_jobs='Root5588 and31147 closedexit0; new44arena oldMMC3negative closedexpectedexit1; SamusH/I/J and three additional profiles closed. No final capture launched.',
        active_host_work='Ryu agent prepares proven fixture corrections and coherent unapplied wall helper/caller/reset accounting; MegaMan/Bass agent evaluates larger MMC5 audio memory/CPU trade; Samus agent prepares one grounded final-coral fish-wait policyK. No shared runtime edits authorized to agents.',
        workspace_bytes=workspace_bytes(ROOT), workspace_cap_bytes=30_000_000_000,
        remaining=parent['remaining'])
    assert report['workspace_bytes'] < report['workspace_cap_bytes']
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], report['workspace_bytes'], 'bytes; accepted48unchanged,all9Ryuoriginsconfirmed')


if __name__ == '__main__':
    main()
