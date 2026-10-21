"""Freeze N's full component validation and the still-incomplete roster audit."""
from pathlib import Path
import datetime
import hashlib
import json
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'build/verification/root-current49-progress-i.json'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert not OUT.exists()
    checkpoint = ROOT / 'build/checkpoints/roster-audit-v49-provisional-n'
    manifest = json.loads((checkpoint / 'manifest.json').read_text())
    assert manifest['status'] == 'provisional-N-full-component-suite-validated-full-goal-incomplete'
    assert not manifest['goal_complete'] and not manifest['accepted_release']
    with zipfile.ZipFile(checkpoint / 'source-v49.zip') as z:
        catalog = json.loads(z.read('archived-file-hashes.json'))
    assert len(catalog) == 408 and all(sha(ROOT / n) == h for n, h in catalog.items())
    for case in manifest['builds']:
        rom = ROOT / f'build/smb-crossover-{case["mapper"]}.nes'
        assert sha(rom) == case['ROM_sha256'] == sha(checkpoint / rom.name)
        assert sha(rom.with_suffix('.lbl')) == case['LBL_sha256']
        assert sha(rom.with_suffix('.dbg')) == case['DBG_sha256']
    private = {}
    for name, key, count in [
        ('root49-integrated-private-build-k', 'source407_hashes', 407),
        ('root49k-samus-water-private-build-l', 'source407_hashes', 407),
        ('root49k-ryu-platform-private-build-m-d', 'source408_hashes', 408),
        ('root49-combined-private-build-n', 'source408_hashes', 408),
        ('root-mm48-owner-transfer-build-a', 'source404_hashes', 404),
    ]:
        folder = ROOT / 'build/verification' / name
        r = json.loads((folder / 'report.json').read_text())
        assert len(r[key]) == count and all(sha(folder / 'source' / n) == h for n, h in r[key].items())
        private[name] = dict(report_sha256=sha(folder / 'report.json'), source_count=count, source_exact=True, status=r['status'])
    paths = {
        'previous_h': 'build/verification/root-current49-progress-h.json',
        'working_N_manifest': 'build/checkpoints/roster-audit-v49-provisional-n/manifest.json',
        'N_full761_run': 'build/verification/root49-combined-private-build-n/qa-suite-a/report.json',
        'cold_vine_full13568_per_mapper': 'build/verification/ryu49k-vine-abi-component-a/root-cache-full-b/report.json',
        'cache_original_full_M3_literal': 'build/verification/ryu49k-vine-abi-component-a/label-cache-full-m3-receipt-c.json',
        'uncached_redundant_run_stopped_after_M3': 'build/verification/ryu49k-vine-abi-component-a/root-full-a/termination-receipt.json',
        'Ryu_native80_actual': 'build/verification/ryu49k-platform-actual-review-d-b/report.json',
        'Ryu_D_live_five_packets_pending_castle': 'build/roster-through-2-2/root49d-ryu-live-poweron-d-10-v0-mmc3/manifest.json',
        'Ryu_next_E_N_binding': 'build/verification/ryu49d-live-route-preparation-e-n-binding-a/freeze.json',
        'Samus_L_H_five_stages_then_fish': 'build/roster-through-2-2/root49l-samus-high-stair-live-h-2-v0-mmc3/manifest.json',
        'Samus_L_I_coral_success_then_Blooper': 'build/roster-through-2-2/root49l-samus-water-short-hop-i-2-v0-mmc3/manifest.json',
        'Bill_N_unreached_lowerbar': 'build/roster-through-2-2/root49n-bill-lower-bar-k-3-v0-mmc3/manifest.json',
        'Bill_N_controller_bindings': 'build/verification/root49n-bill-lower-bar-k/freeze.json',
        'audio_D_host_setup_negative': 'build/verification/mm48-owner-native-paired-review-d/review-a.json',
        'audio_E_dummy_stack_read_negative': 'build/verification/mm48-owner-native-paired-review-e/review-a.json',
        'audio_F_IRQ_boundary_negative': 'build/verification/mm48-owner-native-paired-review-f/review-a.json',
        'audio_G_exact_boundary_diagnostic': 'build/verification/mm48-owner-native-stack-actions-diagnostic-g/diagnostic-a.json',
        'audio_H_strict88_pass': 'build/verification/mm48-owner-native-paired-review-h/review-a.json',
        'audio_I_MM2_control96_theme_negative': 'build/verification/mm48-owner-native-owners-mm2-i/control-a/host-receipt.json',
        'positive_fixture_DBG14_compaction': 'build/verification/root-old-positive-fixture-debug49-compaction-a/receipt.json',
        'positive_fixture_DBG14_roundtrip': 'build/verification/root-old-positive-fixture-debug49-compaction-a/verification.json',
        'old_prototype_DBG20_compaction': 'build/verification/root-old-provisional-debug49-compaction-a/receipt.json',
        'old_prototype_DBG20_roundtrip': 'build/verification/root-old-provisional-debug49-compaction-a/verification.json',
        'QA_notes': 'docs/qa/roster-provisional-v49.md',
    }
    refs = {}
    for name, n in paths.items():
        p = ROOT / n
        assert p.is_file(), n
        refs[name] = dict(path=n, sha256=sha(p))
    qa = json.loads((ROOT / paths['N_full761_run']).read_text())
    assert qa['status'] == 'PASS-full-current-fixture-run' and qa['cases'] == 761 and not qa['failures']
    sys.path.insert(0, str(ROOT / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(ROOT)
    assert used < 30_000_000_000
    r = dict(status='progress-full-goal-incomplete', goal_complete=False,
             utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
             accepted_checkpoint='roster-audit-v48', working_checkpoint=checkpoint.name,
             shared_source408_exact=True, private_sources=private, references=refs, workspace_bytes=used,
             unfinished=[
                 'All-roster ordinary current-N end2-2 runs, every weapon/upgrade, lag optimization and final recordings.',
                 'Samus L I clears the five prior stages and its short coral hop, then dies on Blooper contact in2-2. Fresh N-bound dynamic defense pending.',
                 'Ryu D controllerD clears1-3 then dies on BowserFlame at13561/X1901; ordinary repaired-platform admission remains unreached. Fresh N E native attempt is separately recorded.',
                 'Bill N falls in1-2 before the lowerbar controller activates; actual fractional/support/clamp analysis pending. No ROM failure inferred yet.',
                 'Audio H strict88 MM3 ownership pass does not cover MM2/life/reset/resume/DMC/PCM/crowd/current-N transplant. I96 MM2 raw capture remains nativeexit1 due a theme-specific writer guard; candidate not admitted under that negative.',
                 'Native source/platform phase, fractional/twip and geometry qualifications remain explicit. No complete perfect-physics claim.',
                 'All route/native negatives retained. Old compiler DBG storage is exact reversible gzip. Current headroom still cannot cover the full remaining final-recording set plus temporary capture reserve.',
             ])
    OUT.write_text(json.dumps(r, indent=2) + '\n')
    print(json.dumps(dict(path=str(OUT.relative_to(ROOT)), sha256=sha(OUT), workspace_bytes=used)), flush=True)

if __name__ == '__main__':
    main()
