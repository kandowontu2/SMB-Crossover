"""Preserve current-N ordinary clears and unaccepted O/O2 build evidence."""
from pathlib import Path
import datetime
import hashlib
import json
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'build/verification/root-current49-progress-k.json'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not OUT.exists()
    previous = ROOT/'build/verification/root-current49-progress-j.json'
    assert sha(previous) == '8f237062e25ca2455b2554a2525b0ed8e386534364b77e543a3b08f99a0336e4'
    checkpoint = ROOT/'build/checkpoints/roster-audit-v49-provisional-n'
    m = json.loads((checkpoint/'manifest.json').read_text())
    assert not m['accepted_release'] and not m['goal_complete']
    with zipfile.ZipFile(checkpoint/'source-v49.zip') as z:
        cat = json.loads(z.read('archived-file-hashes.json'))
    assert len(cat) == 408 and all(sha(ROOT/n) == h for n,h in cat.items())
    for c in m['builds']:
        rom = ROOT/f'build/smb-crossover-{c["mapper"]}.nes'
        assert sha(rom) == c['ROM_sha256']
        assert sha(rom.with_suffix('.lbl')) == c['LBL_sha256']
        assert sha(rom.with_suffix('.dbg')) == c['DBG_sha256']
    private = {}
    for suffix in ('o','o2'):
        folder = ROOT/f'build/verification/root49n-ryu-overlap-private-build-{suffix}'
        r = json.loads((folder/'report.json').read_text())
        assert r['status'] == 'PASS-private-Ryu-overlap-build-only'
        assert len(r['source409_hashes']) == 409
        assert all(sha(folder/'source'/n) == h for n,h in r['source409_hashes'].items())
        assert sha(folder/'source-overlap-o.zip') == r['source_archive_sha256']
        private[suffix] = dict(report_sha256=sha(folder/'report.json'), source409_exact=True,
                               status=r['status'], acceptance=False)
    paths = {
        'previous_j': previous.relative_to(ROOT).as_posix(),
        'working_N': (checkpoint/'manifest.json').relative_to(ROOT).as_posix(),
        'N_761_component_checks': 'build/verification/root49-combined-private-build-n/qa-suite-a/report.json',
        'N_Mario_Luigi_current_clear_review': 'build/verification/root49n-mario-luigi-fixed-review-a.json',
        'N_Samus_M_legacy_target_assertion': 'build/roster-through-2-2/root49n-samus-floor-handoff-m-2-v0-mmc3/manifest.json',
        'N_Bill_B_original_checker_negative': 'build/verification/root49n-bill-observer-b-check-negative-a/report.json',
        'N_Bill_C_root_admission': 'build/verification/agent49n-bill-gap-support-admission-c/native-n-root-c.json',
        'isolated_audio72_strict_root_pass': 'build/verification/mm48-owner-native-life-l-paired-a/review-a.json',
        'isolated_audio72_actual_frozen': 'build/verification/mm48-owner-native-life-l-paired-a/frozen.json',
        'H2_corrected_source_packet': 'build/verification/ryu49n-platform-source-admission-h2/implementation-freeze.json',
        'O2_private_build': 'build/verification/root49n-ryu-overlap-private-build-o2/report.json',
        'O_private_pre_hardening_build': 'build/verification/root49n-ryu-overlap-private-build-o/report.json',
        'QA': 'docs/qa/roster-provisional-v49.md',
    }
    refs = {}
    for name,n in paths.items():
        p = ROOT/n
        assert p.is_file(), n
        refs[name] = dict(path=n,sha256=sha(p))
    clears = json.loads((ROOT/paths['N_Mario_Luigi_current_clear_review']).read_text())
    assert all(c['result']['cleared'] and c['result']['deaths']==0 for c in clears['cases'])
    sys.path.insert(0,str(ROOT/'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(ROOT)
    assert used < 30_000_000_000
    report = dict(status='progress-full-goal-incomplete', goal_complete=False,
                  utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  accepted_checkpoint='roster-audit-v48', working_checkpoint=checkpoint.name,
                  shared_source408_exact=True, private409_builds=private, references=refs,
                  current_N_ordinary_clears=['Mario','Luigi'], workspace_bytes=used,
                  unfinished=[
                      'Full current-runtime roster ordinary end2-2 clears, complete specials/weapons/upgrades verification, lag optimization and final recordings.',
                      'Samus M reaches2592/Y48 grounded then stops on inherited legacy target assumption; additive current-N continuation pending.',
                      'Bill C admits actual neutral edge/pit receipts; later genuinely supported ordinary takeoff not executed.',
                      'Ryu H2/O2 compiled only. Targeted source/native underside/fallback tests, full regression, ordinary route and integration pending.',
                      'O/H missing-prior-overflow-guard build is retained and unaccepted. Shared/root N unchanged.',
                      'Mario/Luigi completion frames match old references; per-frame NMI/PPU/DMA differences remain literal and current-runtime final videos are pending.',
                      'Isolated source48 audio72 death-transition strict pass does not prove reset/resume/DMC/crowd/PCM or current-N integration.',
                      'Old source phase/fraction/anchor qualifications remain; no perfect-physics or full-goal claim.',
                      'Workspace remains below30GB but cannot yet cover all final recordings and their temporary capture reserve. All native/route negatives are retained.',
                  ])
    OUT.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(path=OUT.relative_to(ROOT).as_posix(),sha256=sha(OUT),workspace_bytes=used)),flush=True)


if __name__=='__main__':
    main()
