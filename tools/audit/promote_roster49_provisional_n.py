"""Expose exact combined N only after its complete current-fixture run passes."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
N = ROOT / 'build/verification/root49-combined-private-build-n'
OLD = ROOT / 'build/checkpoints/roster-audit-v49-provisional-l'
OUT = ROOT / 'build/checkpoints/roster-audit-v49-provisional-n'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert not OUT.exists()
    built = json.loads((N / 'report.json').read_text())
    assert built['status'] == 'PASS-private-exact-disjoint-combination-build-only'
    catalog = built['source408_hashes']
    assert len(catalog) == 408 and all(sha(N / 'source' / n) == h for n, h in catalog.items())
    qa_path = N / 'qa-suite-a/report.json'
    qa = json.loads(qa_path.read_text())
    assert qa['status'] == 'PASS-full-current-fixture-run' and qa['exit'] == 0
    assert qa['cases'] == 761 and not qa['failures'] and qa['source408_exact_after'] and qa['fixtures_exact_after']
    summary = N / 'source/build/verification/summary-build.json'
    assert sha(summary) == qa['summary_sha256']
    tests = json.loads(summary.read_text())
    assert tests['result'] == 'passed' and len(tests['cases']) == 761
    assert all(c['result'] == 'passed' for c in tests['cases'])
    assert all(sha(ROOT / n) == h for n, h in qa['fixture_and_runner_hashes'].items()
               if n.startswith('tests/') or n.startswith('tools/'))
    vine_path = ROOT / 'build/verification/ryu49k-vine-abi-component-a/root-cache-full-b/report.json'
    vine = json.loads(vine_path.read_text())
    assert vine['status'] == 'PASS_EXPLICIT_COMPILED_VINE_ABI_OAM_SMC_STACK_COMPONENT'
    assert all(x['passed'] == 13568 for x in vine['cases'].values())
    references = {'private_exact_combination': N / 'report.json', 'full_current_suite': qa_path,
                  'full_suite_summary': summary, 'cold_vine_full_CPU': vine_path,
                  'native_platform_actual_review': ROOT / 'build/verification/ryu49k-platform-actual-review-d-b/report.json',
                  'Samus_L_manifest': OLD / 'manifest.json'}
    for mapper in ('mmc3', 'mmc5'):
        p = ROOT / f'build/verification/ryu49k-platform-component-b/binding-d-{mapper}-positive-b/native-output/result.json'
        value = json.loads(p.read_text())
        assert value['cases'] == value['completed'] == 40 and value['failures'] == 0
        references['native_platform_' + mapper] = p
    with zipfile.ZipFile(OLD / 'source-v49.zip') as z:
        before = json.loads(z.read('archived-file-hashes.json'))
    assert len(before) == 407 and all(sha(ROOT / n) == h for n, h in before.items())
    previous = json.loads((OLD / 'manifest.json').read_text())
    for c in previous['builds']:
        rom = ROOT / f'build/smb-crossover-{c["mapper"]}.nes'
        assert sha(rom) == c['ROM_sha256'] and sha(rom.with_suffix('.dbg')) == c['DBG_sha256']
        assert sha(rom.with_suffix('.lbl')) == c['LBL_sha256']
    changed = [n for n, h in catalog.items() if before.get(n) != h]
    assert len(changed) == 10 and 'src/samus.s' not in changed
    sys.path.insert(0, str(ROOT / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(ROOT)
    assert used + 150_000_000 < 30_000_000_000
    OUT.mkdir()
    archive = N / 'source-combined-n.zip'
    assert sha(archive) == built['source_archive_sha256']
    shutil.copyfile(archive, OUT / 'source-v49.zip')
    for n in changed:
        p = ROOT / n
        if n not in before:
            assert not p.exists()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes((N / 'source' / n).read_bytes())
    assert all(sha(ROOT / n) == h for n, h in catalog.items())
    report = dict(status='building-provisional-N', accepted_release=False, goal_complete=False,
                  stable_checkpoint='roster-audit-v48', previous_working_checkpoint=OLD.name,
                  compiler_source_files=408, source_hashes=catalog, source_sha256=sha(OUT / 'source-v49.zip'),
                  changed_shared_sources=changed, builds=[], workspace_before_bytes=used,
                  validation=dict(single_full_current_run=True, cases=761, native_platform_cases_per_mapper=40,
                                  cold_vine_CPU_cases_per_mapper=13568, compiled_disjoint_union=True),
                  references={k: dict(path=str(p.relative_to(ROOT)), sha256=sha(p)) for k, p in references.items()},
                  known_limits=['All-roster ordinary end2-2 runs, every weapon/upgrade, lag optimization and final recordings remain incomplete.',
                                'Platform source/native motion phase, fractional/twip differences, actual fallback RAM and fixture-input corrections remain qualified in the actual review.',
                                'Cold vine draw adds106 MMC3 or86 MMC5 cycles per active call; no walking speedup is claimed.',
                                'Source48 audio owner-transfer optimization remains separate and is not included.'])
    def save():
        (OUT / 'manifest.json').write_text(json.dumps(report, indent=2) + '\n')
    save()
    for mapper in ('mmc3', 'mmc5'):
        with (OUT / f'build-{mapper}.log').open('w', encoding='utf-8') as log:
            done = subprocess.run([sys.executable, 'tools/build.py', '--mapper', mapper], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        assert done.returncode == 0
        rom = ROOT / f'build/smb-crossover-{mapper}.nes'
        private = N / f'source/build/{rom.name}'
        assert rom.read_bytes() == private.read_bytes()
        assert rom.with_suffix('.lbl').read_bytes() == private.with_suffix('.lbl').read_bytes()
        for extension in ('.nes', '.lbl', '.dbg', '.map', '.lst'):
            shutil.copyfile(rom.with_suffix(extension), OUT / rom.with_suffix(extension).name)
        report['builds'].append(dict(mapper=mapper, ROM_sha256=sha(rom), DBG_sha256=sha(rom.with_suffix('.dbg')),
                                    LBL_sha256=sha(rom.with_suffix('.lbl')), exact_private_ROM_and_LBL=True))
        save()
    assert all(sha(ROOT / n) == h for n, h in catalog.items())
    report.update(status='provisional-N-full-component-suite-validated-full-goal-incomplete',
                  source408_exact_after=True, workspace_after_bytes=workspace_bytes(ROOT))
    save()
    print(json.dumps({k: v for k, v in report.items() if k not in ('source_hashes', 'references')}, indent=2), flush=True)

if __name__ == '__main__':
    main()
