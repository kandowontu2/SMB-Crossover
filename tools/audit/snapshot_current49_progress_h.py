"""Freeze current L progress and unfinished route/platform/audio work."""
from pathlib import Path
import datetime
import hashlib
import json
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'build/verification/root-current49-progress-h.json'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not OUT.exists()
    checkpoint = ROOT / 'build/checkpoints/roster-audit-v49-provisional-l'
    manifest = json.loads((checkpoint / 'manifest.json').read_text())
    assert manifest['status'] == 'provisional-L-focused-validated-full-goal-incomplete'
    with zipfile.ZipFile(checkpoint / 'source-v49.zip') as z:
        catalog = json.loads(z.read('archived-file-hashes.json'))
    assert len(catalog) == 407 and all(sha(ROOT / n) == h for n, h in catalog.items())
    for case in manifest['builds']:
        rom = ROOT / f'build/smb-crossover-{case["mapper"]}.nes'
        assert sha(rom) == case['ROM_sha256'] == sha(checkpoint / rom.name)
        assert sha(rom.with_suffix('.lbl')) == case['LBL_sha256']
        assert sha(rom.with_suffix('.dbg')) == case['DBG_sha256']
    private = {}
    for name, key, count in [
        ('root49-integrated-private-build-k', 'source407_hashes', 407),
        ('root49k-samus-water-private-build-l', 'source407_hashes', 407),
        ('root49k-ryu-platform-private-build-m', 'source408_hashes', 408),
        ('root49k-ryu-platform-private-build-m-c', 'source408_hashes', 408),
        ('root49k-ryu-platform-private-build-m-d', 'source408_hashes', 408),
        ('root-mm48-owner-transfer-build-a', 'source404_hashes', 404),
    ]:
        folder = ROOT / 'build/verification' / name
        r = json.loads((folder / 'report.json').read_text())
        assert len(r[key]) == count and all(sha(folder / 'source' / n) == h for n, h in r[key].items())
        private[name] = dict(report_sha256=sha(folder / 'report.json'), source_count=count, source_exact=True, status=r['status'])
    references = {
        'previous_progress_g': 'build/verification/root-current49-progress-g.json',
        'working_L_manifest': 'build/checkpoints/roster-audit-v49-provisional-l/manifest.json',
        'K_staged_761': 'build/verification/root49-integrated-private-build-k/staged-current-summary.json',
        'L_existing_68_valid': 'build/checkpoints/roster-audit-v49-provisional-l/validation/valid-targeted-68.json',
        'L_original_70_including_two_helper_setup_negatives': 'build/verification/root49k-samus-water-private-build-l/targeted-regression-a/report.json',
        'L_source_native_review': 'build/verification/agent49l-samus-water-order-actual-review-d/freeze.json',
        'L_CPU_M3_1000': 'build/verification/agent49l-samus-water-order-cpu-c/cpu-l-mmc3-root-c.json',
        'L_CPU_M5_1000': 'build/verification/agent49l-samus-water-order-cpu-c/cpu-l-mmc5-root-c.json',
        'Samus_K_early11_real_contact': 'build/verification/agent49k-samus-early11-owner-review-b/freeze.json',
        'Samus_K_early12_actual_contact': 'build/verification/agent49k-samus-early12-owner-review-d/freeze.json',
        'Goomba_source_geometry_conditional_alignment': 'build/verification/root49k-samus-goomba-source-geometry-a.json',
        'Samus_L_live_three_land_stages_then_castle_death': 'build/roster-through-2-2/root49l-samus-third-goomba-live-e-2-v0-mmc3/manifest.json',
        'Ryu_B_overflow': 'build/verification/root49k-ryu-platform-private-build-m/report.json',
        'Ryu_C_wrong_physical_bank': 'build/verification/root49k-ryu-platform-private-build-m-c/bank-placement-negative.json',
        'Ryu_D_build_both_baseline': 'build/verification/root49k-ryu-platform-private-build-m-d/report.json',
        'Ryu_A_fixture_away_request_deadlock': 'build/verification/ryu49k-platform-component-b/A-negative-classification.json',
        'Ryu_D_native_M3_40': 'build/verification/ryu49k-platform-component-b/binding-d-mmc3-positive-b/native-output/result.json',
        'Ryu_D_native_M5_40': 'build/verification/ryu49k-platform-component-b/binding-d-mmc5-positive-b/native-output/result.json',
        'audio_B_partial_timeout': 'build/verification/mm48-owner-native-lifecycle-b/control-b/host-receipt.json',
        'audio_C_88_control_exact_B': 'build/verification/mm48-owner-native-lifecycle-c/control-owners-mm3-c/host-receipt.json',
        'audio_C_dummy_bus_read_guard_negative': 'build/verification/mm48-owner-native-lifecycle-c/candidate-owners-mm3-c/host-receipt.json',
        'audio_D_candidate_88_capture_completed': 'build/verification/mm48-owner-native-shadow-bus-d/native-a/host-receipt.json',
        'old_canonical_DBG_compaction_64': 'build/verification/root-old-checkpoint-debug49-compaction-a/receipt.json',
        'old_canonical_DBG_roundtrip_verification': 'build/verification/root-old-checkpoint-debug49-compaction-a/verification.json',
        'further_old_DBG_inventory_not_applied': 'build/verification/root-old-debug49-storage-inventory-b.json',
        'QA_notes': 'docs/qa/roster-provisional-v49.md',
    }
    refs = {}
    for name, n in references.items():
        path = ROOT / n
        assert path.is_file(), n
        refs[name] = dict(path=n, sha256=sha(path))
    sys.path.insert(0, str(ROOT / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(ROOT)
    assert used < 30_000_000_000
    report = dict(status='progress-full-goal-incomplete', goal_complete=False,
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), accepted_checkpoint='roster-audit-v48',
        working_checkpoint=checkpoint.name, shared_source407_exact=True, private_sources=private,
        references=refs, workspace_bytes=used,
        unfinished=['All-roster ordinary end2-2 runs, every weapon/upgrade, lag optimization and final recordings.',
                    'Samus L clears1-1/1-2/1-3, castle death15291X2189Y101 requires actor/tactic classification.',
                    'Ryu D40native cases/map pass after an explicit test-input deadlock correction; cold-vine ABI proof, broad regression and ordinary continuation pending.',
                    'Audio source48 candidate D completes88 MM3 ownership calls, strict paired review and MM2/life/reset/resume/DMC/PCM/crowd/transplant gates pending.',
                    'K staged761 is historical; L68 valid existing cases plus focused native/CPU do not constitute a full L suite.',
                    'All route/native negatives retained. No final L recordings. Current headroom is insufficient for the final capture reserve plus every remaining recording.'])
    OUT.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(path=str(OUT.relative_to(ROOT)), sha256=sha(OUT), workspace_bytes=used)), flush=True)


if __name__ == '__main__':
    main()
