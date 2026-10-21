"""Append a literal current-N progress snapshot; full roster goal is incomplete."""
from pathlib import Path
import datetime
import hashlib
import json
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'build/verification/root-current49-progress-j.json'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not OUT.exists()
    previous = ROOT / 'build/verification/root-current49-progress-i.json'
    assert sha(previous) == '52461c4bc226776504fdd20f9df87c3e95659cd51d150708d8abe3a1b0f8a750'
    checkpoint = ROOT / 'build/checkpoints/roster-audit-v49-provisional-n'
    manifest = json.loads((checkpoint / 'manifest.json').read_text())
    assert not manifest['goal_complete'] and not manifest['accepted_release']
    assert sha(checkpoint / 'manifest.json') == 'd39a3b6fe501e4b1c1508feb89fbbcd5ec013b125192f3c06cf0760fd2f8cf78'
    with zipfile.ZipFile(checkpoint / 'source-v49.zip') as z:
        source = json.loads(z.read('archived-file-hashes.json'))
    assert len(source) == 408 and all(sha(ROOT / n) == h for n, h in source.items())
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
        report = json.loads((folder / 'report.json').read_text())
        assert len(report[key]) == count
        assert all(sha(folder / 'source' / n) == h for n, h in report[key].items())
        private[name] = dict(report_sha256=sha(folder/'report.json'), source_count=count, source_exact=True)
    paths = {
        'previous_i': previous.relative_to(ROOT).as_posix(),
        'working_N_manifest': (checkpoint/'manifest.json').relative_to(ROOT).as_posix(),
        'N_full761': 'build/verification/root49-combined-private-build-n/qa-suite-a/report.json',
        'audio_K_strict96_MM2_MM3': 'build/verification/mm48-owner-native-paired-review-k/review-a.json',
        'audio_K_frozen_reader': 'build/verification/mm48-owner-native-paired-review-k/frozen.json',
        'audio_J_control_admission': 'build/verification/mm48-owner-native-owners-mm2-j/control-admission-a.json',
        'audio_J_candidate96': 'build/verification/mm48-owner-native-owners-mm2-j/candidate-a/host-receipt.json',
        'Ryu_N_F_Bowser_rear': 'build/roster-through-2-2/root49n-ryu-live-poweron-f-10-v0-mmc3/manifest.json',
        'Ryu_N_G_controller_assertion': 'build/roster-through-2-2/root49n-ryu-live-poweron-g-10-v0-mmc3/manifest.json',
        'Ryu_N_G_actual_receipt': 'build/verification/ryu49n-live-route-preparation-g/actual-attempt-receipt.json',
        'Ryu_N_G_causal_underside': 'build/verification/ryu49n-platform-underside-causal-g/report.json',
        'Samus_N_J_fish_negative': 'build/roster-through-2-2/root49n-samus-blooper-strokes-j-2-v0-mmc3/manifest.json',
        'Samus_N_K_coral_then_bridge_fish': 'build/roster-through-2-2/root49n-samus-coral-cap-k-2-v0-mmc3/manifest.json',
        'Samus_N_L_exit_stall_timer': 'build/roster-through-2-2/root49n-samus-bridge-cheep-l-2-v0-mmc3/manifest.json',
        'Bill_N_observer_lookup_negative': 'build/roster-through-2-2/root49n-bill-gap-support-a-3-v0-mmc3/manifest.json',
        'old_compiler_metadata_compaction': 'build/verification/root-old-canonical-metadata49-compaction-a/receipt.json',
        'old_compiler_metadata_roundtrip': 'build/verification/root-old-canonical-metadata49-compaction-a/verification.json',
        'old_compiler_metadata_real_restore': 'build/verification/root-old-canonical-metadata49-compaction-a/restore-receipt.json',
        'QA': 'docs/qa/roster-provisional-v49.md',
    }
    refs = {}
    for name, n in paths.items():
        p = ROOT / n
        assert p.is_file(), n
        refs[name] = dict(path=n, sha256=sha(p))
    qa = json.loads((ROOT/paths['N_full761']).read_text())
    assert qa['cases'] == 761 and not qa['failures'] and qa['status'] == 'PASS-full-current-fixture-run'
    sys.path.insert(0, str(ROOT/'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(ROOT)
    assert used < 30_000_000_000
    result = dict(status='progress-full-goal-incomplete', goal_complete=False,
                  utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  accepted_checkpoint='roster-audit-v48', working_checkpoint=checkpoint.name,
                  shared_source408_exact=True, private_sources=private, references=refs,
                  workspace_bytes=used, old_metadata_net_saved_bytes=145628596,
                  unfinished=[
                      'Every-character current-runtime ordinary end2-2 clears, complete weapon/upgrade matrix, lag optimization and final recordings.',
                      'Ryu guarded normal-platform underside collision cancels actual qVY through next-update AirSync. Narrow private repair pending; G Bowser controller assertion is separate.',
                      'Samus L passes coral/bridge and stalls at exit2433/Y176 until timer death32038; actual target-removal and exit-controller analysis pending.',
                      'Bill N passive observer failed RgProne lookup; no replay neutrality or collision interpretation accepted. Additive correction pending.',
                      'Audio strict96 MM2/MM3 pass is isolated source48 only. Life/reset/resume/DMC/PCM/crowd/current-N transplant remain pending.',
                      'Native phase/fraction/twip/source anchor qualifications remain explicit. No perfect-physics claim.',
                      'All route/native negatives retained. Older compiler metadata is exact reversible gzip and raw restoration is required for old filename/hash consumers.',
                      'Headroom remains insufficient for all final recordings plus temporary native capture reserve.',
                  ])
    OUT.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(path=OUT.relative_to(ROOT).as_posix(), sha256=sha(OUT), workspace_bytes=used)), flush=True)


if __name__ == '__main__':
    main()
