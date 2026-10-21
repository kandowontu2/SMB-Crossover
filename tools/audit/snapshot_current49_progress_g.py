"""Record current evidence and unfinished work without accepting a ROM."""
from pathlib import Path
import datetime
import hashlib
import json
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'build/verification/root-current49-progress-g.json'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not OUT.exists()
    g = ROOT / 'build/checkpoints/roster-audit-v49-provisional-g'
    with zipfile.ZipFile(g / 'source-v49.zip') as z:
        catalog = json.loads(z.read('archived-file-hashes.json'))
    assert len(catalog) == 404 and all(sha(ROOT / n) == h for n, h in catalog.items())
    private = {}
    for name, key, count in [
        ('root49g-grapple-private-build-a', 'source405_hashes', 405),
        ('root49h-coin-private-build-a', 'source406_hashes', 406),
        ('root49g-samus-crouch-private-build-b', 'source405_hashes', 405),
        ('root49-integrated-private-build-k', 'source407_hashes', 407),
        ('root-mm48-owner-transfer-build-a', 'source404_hashes', 404),
    ]:
        folder = ROOT / 'build/verification' / name
        r = json.loads((folder / 'report.json').read_text())
        # The audio builder uses its original field spelling.
        if key not in r and name == 'root-mm48-owner-transfer-build-a':
            key = 'source_hashes'
        assert len(r[key]) == count and all(sha(folder / 'source' / n) == h for n, h in r[key].items())
        private[name] = dict(report_sha256=sha(folder / 'report.json'), source_count=count, source_exact=True)
    references = {
        'previous_progress_f': 'build/verification/root-current49-progress-f.json',
        'old_debug_compaction_plan': 'build/verification/root-completed-debug49-compaction-a/plan.json',
        'old_debug_compaction_restore': 'build/verification/root-completed-debug49-compaction-a/restore-proof.json',
        'Samus_source_crouch': 'build/verification/agent49f-samus-crouch-source-audit-a/report.json',
        'Samus_bad_placement_rejected': 'build/verification/root49g-samus-crouch-private-build-a/layout-negative.json',
        'Samus_good_placement': 'build/verification/agent49g-samus-crouch-fix-proposal-b/freeze.json',
        'Samus_cpu_m3': 'build/verification/agent49g-samus-crouch-fix-proposal-b/cpu-m3-root-b.json',
        'Samus_cpu_m5': 'build/verification/agent49g-samus-crouch-fix-proposal-b/cpu-m5-root-b.json',
        'Samus_native_m3': 'build/verification/agent49g-samus-crouch-fix-proposal-b/native-new-m3-root-b.json',
        'Samus_native_m5': 'build/verification/agent49g-samus-crouch-fix-proposal-b/native-new-m5-root-b.json',
        'Samus_actual_review_and_water_correction': 'build/verification/agent49g-samus-crouch-b-actual-review-a/report.json',
        'Samus_fresh_Up_source_order': 'build/verification/agent49k-samus-water-button-order-a/report.json',
        'Samus_crouch_fixture_revision': 'build/verification/root49k-crouch-fixture-migration-a/report.json',
        'Samus_head_fixture_revision': 'build/verification/root49k-head-fixture-migration-a/report.json',
        'Samus_K_early_ordinary_negative': 'build/roster-through-2-2/root49k-samus-floorwait-live-a-2-v0-mmc3/manifest.json',
        'Samus_K_early_passive_preparation': 'build/verification/agent49k-samus-early11-contact-observer-a/freeze.json',
        'Ryu_H_ordinary_grapple': 'build/verification/ryu49h-ordinary-contact-classification-a/report.json',
        'Ryu_J_coin_CPU': 'build/verification/ryu49j-map-cpu-full-root-a.json',
        'Ryu_J_native_data': 'build/verification/ryu49j-native-coin-differential-a/report.json',
        'Ryu_K_ordinary_1_3_clear': 'build/verification/ryu49k-ordinary-coin-classification-a/report.json',
        'Ryu_K_castle_owner': 'build/verification/ryu49k-castle-classification-b/report.json',
        'Ryu_native_callbackPC_qualification': 'build/verification/ryu49k-castle-classification-b/native-callback-pc-qualification.json',
        'Ryu_platform_binding_preparation': 'build/verification/ryu49k-platform-source-binding-a/freeze.json',
        'K_compiled_composition': 'build/verification/root49-integrated-private-build-k/component-applicability.json',
        'K_full_suite_in_progress': 'build/verification/root49-integrated-private-build-k/qa-suite-b/report.json',
        'MM_audio_C_normal_native': 'build/verification/mm48-owner-c-normal-native-a/native-a/host-receipt.json',
        'MM_audio_first_timing_negative': 'build/verification/mm48-owner-c-normal-native-a/native-review-negative.json',
        'MM_audio_timing_v2': 'build/verification/mm48-owner-c-normal-review-v2/completion-receipt.json',
        'MM_audio_lifecycle_control_negative': 'build/verification/mm48-owner-native-lifecycle-a/control-a/host-receipt.json',
        'provisional_QA_notes': 'docs/qa/roster-provisional-v49.md',
    }
    refs = {}
    for name, relative in references.items():
        p = ROOT / relative
        assert p.is_file(), relative
        refs[name] = dict(path=relative, sha256=sha(p))
    sys.path.insert(0, str(ROOT / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(ROOT)
    assert used < 30_000_000_000
    data = dict(status='progress-full-goal-incomplete', goal_complete=False,
                utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                accepted_checkpoint='roster-audit-v48', shared_runtime='roster-audit-v49-provisional-g',
                shared_source404_exact=True, private_sources=private, references=refs, workspace_bytes=used,
                CPU_cases=dict(Ryu_map=359424, Samus_per_mapper=13154),
                native_Samus_active_form=dict(arenas_per_mapper=177, unexpected_source_disagreements=0),
                audio_normal=dict(source_NMIs=4641, steady_audio_cycles_saved=725, PCM_identity_proven=False),
                known_qualifications=[
                    'Two same-update water checks precede the body selector; no final-water/gravity delay demonstrated. Up+direction speed remains untested.',
                    'Native memory callback PC is callback-visible/post-decode, not direct writer opcode; original raw data retained.',
                    'Ryu ordinary clears1-3 then dies at Bowser13778; exact platform-grapple fractional diagnostic is running.',
                    'Samus K old fixed prefix dies in1-1 at2533; water route has not been exercised on K. Early passive is running.',
                    'K full suite remains running with preserved old Samus head-offset expectation failure; current revised32-pose tests pass both mappers.',
                    'Audio lifecycle control did not complete; candidate was not launched. Instrumentation diagnosis is pending.',
                    'No final K recordings; all-character/end2-2/all-weapons/lag objective remains incomplete.',
                    'Retain all route/native negatives; no recursive cleanup or relocation. Final capture needs additional reserve.',
                ])
    OUT.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(path=str(OUT.relative_to(ROOT)), sha256=sha(OUT), workspace_bytes=used)), flush=True)


if __name__ == '__main__':
    main()
