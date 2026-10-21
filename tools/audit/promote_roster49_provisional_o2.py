"""Rebuild/expose tested O2 as a provisional working checkpoint, retaining v48."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = ROOT/'build/verification/root49n-ryu-overlap-private-build-o2'
OLD = ROOT/'build/checkpoints/roster-audit-v49-provisional-n'
OUT = ROOT/'build/checkpoints/roster-audit-v49-provisional-o2'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--other-future-reserve', type=int, required=True)
    a = ap.parse_args()
    assert a.other_future_reserve >= 0 and not OUT.exists()
    b = json.loads((PRIVATE/'report.json').read_text())
    assert b['status'] == 'PASS-private-Ryu-overlap-build-only'
    catalog = b['source409_hashes']
    assert len(catalog) == 409 and all(sha(PRIVATE/'source'/n) == h for n,h in catalog.items())
    archive = PRIVATE/'source-overlap-o.zip'
    assert sha(archive) == b['source_archive_sha256']
    with zipfile.ZipFile(archive) as z:
        assert json.loads(z.read('archived-file-hashes.json')) == catalog
    qa_path = PRIVATE/'qa-suite-a/report.json'
    qa = json.loads(qa_path.read_text())
    assert qa['status'] == 'PASS-full-current-fixture-run' and qa['exit'] == 0
    assert qa['cases'] == 761 and not qa['failures']
    assert qa['source409_exact_after'] and qa['fixtures_exact_after']
    summary = PRIVATE/'source/build/verification/summary-build.json'
    assert sha(summary) == qa['summary_sha256']
    checks = json.loads(summary.read_text())
    assert checks['result'] == 'passed' and len(checks['cases']) == 761
    assert all(c['result'] == 'passed' for c in checks['cases'])
    assert all(sha(ROOT/n) == h for n,h in qa['fixture_and_runner_hashes'].items()
               if n.startswith('tests/') or n.startswith('tools/'))
    review_path = ROOT/'build/verification/root49o2-platform-actual-review-a/root-receipt.json'
    review = json.loads(review_path.read_text())
    assert review['status'] == 'PASS_ROOT_EXECUTED_LITERAL_48_CASE_HOST_REVIEW'
    actual = ROOT/'build/verification/ryu49n-platform-source-actual-review-a/report.json'
    assert sha(actual) == review['report_sha256']
    r = json.loads(actual.read_text())
    assert r['cases'] == 48 and r['candidate_source_or_setup_disagreements'] == 0
    samus = ROOT/'build/roster-through-2-2/root49o2-samus-fixed-o-2-v0-mmc3/manifest.json'
    sm = json.loads(samus.read_text())
    assert sm['verified_through_2_2'] and sm['result']['cleared'] and sm['result']['all_six_stages']
    assert sm['result']['deaths'] == 0 and sm['rom_sha256'] == b['cases'][0]['ROM_sha256']
    assert sm['controller_only'] and sm['full_frame_audit'] and not sm['memory_or_register_writes']
    assert sm['config']['prefix'] is None and sm['config']['replay']
    with zipfile.ZipFile(OLD/'source-v49.zip') as z:
        before = json.loads(z.read('archived-file-hashes.json'))
    assert len(before) == 408 and all(sha(ROOT/n) == h for n,h in before.items())
    previous = json.loads((OLD/'manifest.json').read_text())
    for c in previous['builds']:
        rom = ROOT/f'build/smb-crossover-{c["mapper"]}.nes'
        assert sha(rom) == c['ROM_sha256'] and sha(rom.with_suffix('.dbg')) == c['DBG_sha256']
        assert sha(rom.with_suffix('.lbl')) == c['LBL_sha256']
    changed = [n for n,h in catalog.items() if before.get(n) != h]
    assert set(changed) == {'src/object.s', 'src/sprite_render.s', 'src/entrypoint.s',
                            'src/ryu_platform_source_overlap.s'}
    references = dict(private_build=PRIVATE/'report.json', full_current_suite=qa_path,
                      full_suite_summary=summary, strict_root48_native_review=review_path,
                      native_source_review=actual, independent_Samus_fixed=samus,
                      Samus_actual_comparison=ROOT/'build/verification/agent49o2-samus-fixed-o-comparison-a/root-comparison-a.json',
                      Ryu_castle_route_review=ROOT/'build/verification/ryu49o2-live-a-actual-review/report.json',
                      previous_checkpoint=OLD/'manifest.json')
    for mapper in ('mmc3', 'mmc5'):
        p = ROOT/f'build/verification/ryu49n-platform-source-component-a/binding-o2-{mapper}-root-a/native-output/result.json'
        nr = json.loads(p.read_text())
        assert nr['completed'] == nr['cases'] == 24 and nr['failures'] == 0
        references['native_source24_'+mapper] = p
    copies = [PRIVATE/f'source/build/smb-crossover-{m}{e}' for m in ('mmc3','mmc5')
              for e in ('.nes','.lbl','.dbg','.map','.lst')]
    reserve = archive.stat().st_size + sum(p.stat().st_size for p in copies) + 8_000_000
    sys.path.insert(0, str(ROOT/'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(ROOT)
    assert used+reserve+a.other_future_reserve < 30_000_000_000
    OUT.mkdir()
    shutil.copyfile(archive, OUT/'source-v49.zip')
    for n in changed:
        p = ROOT/n
        if n not in before:
            assert not p.exists()
        p.write_bytes((PRIVATE/'source'/n).read_bytes())
    assert all(sha(ROOT/n) == h for n,h in catalog.items())
    report = dict(status='building-provisional-O2', accepted_release=False, goal_complete=False,
                  stable_checkpoint='roster-audit-v48', previous_working_checkpoint=OLD.name,
                  compiler_source_files=409, source_hashes=catalog, source_sha256=sha(OUT/'source-v49.zip'),
                  changed_shared_sources=changed, builds=[], workspace_before_bytes=used,
                  measured_copy_and_transient_reserve=reserve, other_future_reserve=a.other_future_reserve,
                  references={k:dict(path=p.relative_to(ROOT).as_posix(), sha256=sha(p)) for k,p in references.items()},
                  validation=dict(full_current_fixture_run=761, native_source_cases_per_mapper=24,
                                  strict_root_final_RAM_and_write_review=True, Samus_fixed_end2_2_zero_deaths=True),
                  known_limits=[
                      'Full roster ordinary end2-2, every weapon/upgrade, lag optimization and final recordings remain incomplete.',
                      'Ryu castle now clears; later2-1 invisible-block head admission and surviving-enemy contact remain under investigation.',
                      'Platform source forms/phase/fractions/native anchors remain qualified; incoming MMC5 live stack byte differs before calls.',
                      'Ordered hardware mapper writes were not captured by the platform component.',
                      'Samus N adaptive versus O2 fixed rendering/interrupt timing differences remain literal; no N fixed-proof relabel.',
                      'Isolated source48 audio optimization is excluded; current audio is unchanged.',
                      'Stable v48 checkpoint is retained unchanged.'])
    def save():
        (OUT/'manifest.json').write_text(json.dumps(report, indent=2)+'\n')
    save()
    for mapper in ('mmc3', 'mmc5'):
        with (OUT/f'build-{mapper}.log').open('w', encoding='utf-8') as log:
            done = subprocess.run([sys.executable, 'tools/build.py', '--mapper', mapper], cwd=ROOT,
                                  stdout=log, stderr=subprocess.STDOUT)
        assert done.returncode == 0
        rom = ROOT/f'build/smb-crossover-{mapper}.nes'
        private = PRIVATE/f'source/build/{rom.name}'
        assert rom.read_bytes() == private.read_bytes()
        assert rom.with_suffix('.lbl').read_bytes() == private.with_suffix('.lbl').read_bytes()
        for e in ('.nes','.lbl','.dbg','.map','.lst'):
            shutil.copyfile(rom.with_suffix(e), OUT/rom.with_suffix(e).name)
        report['builds'].append(dict(mapper=mapper, ROM_sha256=sha(rom), DBG_sha256=sha(rom.with_suffix('.dbg')),
                                    LBL_sha256=sha(rom.with_suffix('.lbl')), exact_private_ROM_and_LBL=True,
                                    DBG_source_path_difference_expected=True))
        save()
    assert all(sha(ROOT/n) == h for n,h in catalog.items())
    used_after = workspace_bytes(ROOT)
    assert used_after+a.other_future_reserve < 30_000_000_000
    report.update(status='provisional-O2-full-component-suite-validated-full-goal-incomplete',
                  source409_exact_after=True, workspace_after_bytes=used_after)
    save()
    print(json.dumps({k:v for k,v in report.items() if k not in ('source_hashes','references')}, indent=2), flush=True)


if __name__ == '__main__':
    main()
