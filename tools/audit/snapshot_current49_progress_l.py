"""Pin the provisional O2 promotion and scoped ordinary/native progress."""
from pathlib import Path
import datetime
import hashlib
import json
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'build/verification/root-current49-progress-l.json'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not OUT.exists()
    cp = ROOT/'build/checkpoints/roster-audit-v49-provisional-o2'
    manifest = json.loads((cp/'manifest.json').read_text())
    assert not manifest['accepted_release'] and not manifest['goal_complete']
    assert manifest['status'] == 'provisional-O2-full-component-suite-validated-full-goal-incomplete'
    with zipfile.ZipFile(cp/'source-v49.zip') as z:
        cat = json.loads(z.read('archived-file-hashes.json'))
    assert len(cat) == 409 and cat == manifest['source_hashes']
    assert all(sha(ROOT/n) == h for n,h in cat.items())
    assert sha(cp/'source-v49.zip') == manifest['source_sha256']
    for b in manifest['builds']:
        p = ROOT/f'build/smb-crossover-{b["mapper"]}.nes'
        for e,k in (('.nes','ROM_sha256'),('.dbg','DBG_sha256'),('.lbl','LBL_sha256')):
            assert sha(p.with_suffix(e)) == b[k] == sha(cp/p.with_suffix(e).name)
    stable = ROOT/'build/checkpoints/roster-audit-v48/manifest.json'
    assert sha(stable) == 'fd0770c5058acd0522008f341427878495dadcbb7dd8cbf0e3db1eb934684102'
    paths = {
        'previous_K': 'build/verification/root-current49-progress-k.json',
        'working_O2': 'build/checkpoints/roster-audit-v49-provisional-o2/manifest.json',
        'O2_761_components': 'build/verification/root49n-ryu-overlap-private-build-o2/qa-suite-a/report.json',
        'root_strict_native48_review': 'build/verification/root49o2-platform-actual-review-a/root-receipt.json',
        'O2_Samus_fixed_and_N_adaptive_comparison': 'build/verification/agent49o2-samus-fixed-o-comparison-a/root-comparison-a.json',
        'N_Samus_adaptive_actual_clear_freeze': 'build/verification/agent49n-samus-o-adaptive-clear-review-a/freeze.json',
        'O2_Ryu_actual_castle_clear_review': 'build/verification/ryu49o2-live-a-actual-review/report.json',
        'O2_Ryu_passive2_1_actual_attempt': 'build/verification/ryu49o2-first21-owner-passive-a/actual-attempt-receipt.json',
        'N_Bill_passive_M_root_review': 'build/verification/agent49n-bill-third-platform-observer-m/native-root-review-m.json',
        'N_Scrooge_B_failed_controller_manifest': 'build/roster-through-2-2/root49n-scrooge-live-b-12-v0-mmc3/manifest.json',
        'N_Scrooge_C_failed_controller_manifest': 'build/roster-through-2-2/root49n-scrooge-live-c-12-v0-mmc3/manifest.json',
        'isolated_audio_reset_scope_negative': 'build/verification/mm48-owner-native-reset-paired-scope-q/review-a.json',
        'isolated_audio_R_foreground_supplement_prepared': 'build/verification/mm48-owner-native-reset-foreground-r/frozen.json',
        'storage32_plan': 'build/verification/root-old-candidate-metadata49-compaction-a/plan.json',
        'storage32_verified': 'build/verification/root-old-candidate-metadata49-compaction-a/verification.json',
        'storage32_real_restore': 'build/verification/root-old-candidate-metadata49-compaction-a/restore-receipt.json',
        'promotion_first_budget_negative': 'build/verification/root49o2-promotion-space-negative-a.json',
        'QA_as_of_this_snapshot': 'docs/qa/roster-provisional-v49.md',
    }
    refs = {}
    for key,n in paths.items():
        p = ROOT/n
        assert p.is_file(), n
        refs[key] = dict(path=n, sha256=sha(p), bytes=p.stat().st_size)
    qa = json.loads((ROOT/paths['O2_761_components']).read_text())
    assert qa['status'] == 'PASS-full-current-fixture-run' and qa['cases'] == 761 and not qa['failures']
    sm = json.loads((ROOT/'build/roster-through-2-2/root49o2-samus-fixed-o-2-v0-mmc3/manifest.json').read_text())
    assert sm['verified_through_2_2'] and sm['result']['deaths'] == 0 and sm['result']['all_six_stages']
    sys.path.insert(0, str(ROOT/'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(ROOT)
    assert used < 30_000_000_000
    report = dict(status='progress-full-goal-incomplete', goal_complete=False, accepted_release=False,
                  utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  accepted_checkpoint='roster-audit-v48', working_checkpoint=cp.name,
                  shared_source409_exact=True, root_ROM_DBG_LBL_exact_checkpoint=True,
                  references=refs, workspace_bytes=used,
                  current_O2_ordinary_independent_end2_2_clears=['Samus'],
                  previous_N_independent_clears=['Mario','Luigi'],
                  no_cross_runtime_literal_frame_identity_claim=True,
                  current_active_route='Scrooge D on retained private N; ordinary, bounded, full audit, no capture.',
                  unfinished=[
                      'Whole current-runtime roster through2-2; complete special/alternate weapons/upgrades and lag optimization; final recordings.',
                      'Ryu later2-1 native invisible-block head contact needs source-grounded causal/fix review; surviving Koopa contact is separate.',
                      'Bill M direct pit/platform receipts need causal diagnosis before a bounded controller continuation.',
                      'Scrooge B lower-floor and C left-foot-only admission failures remain literal; D is running.',
                      'Isolated source48 audio reset strict paired proof lacks actual pre/post-clear foreground lineage; R is prepared only and its29.85GB guard currently fails.',
                      'Final video retention preference is pending; no existing native/route evidence deletion is authorized by silence.',
                      'Source phase/fraction/anchor and hardware-mapper-write coverage qualifications remain; no perfect parity claim.',
                  ])
    OUT.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(dict(path=OUT.relative_to(ROOT).as_posix(), sha256=sha(OUT), workspace_bytes=used)), flush=True)


if __name__ == '__main__':
    main()
