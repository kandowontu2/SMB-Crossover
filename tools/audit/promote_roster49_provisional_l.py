"""Expose verified private L as a provisional working build, retaining G/48."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
L = ROOT / 'build/verification/root49k-samus-water-private-build-l'
G = ROOT / 'build/checkpoints/roster-audit-v49-provisional-g'
OUT = ROOT / 'build/checkpoints/roster-audit-v49-provisional-l'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not OUT.exists()
    built = json.loads((L / 'report.json').read_text())
    assert built['status'] == 'PASS-build-and-scoped-layout-only-not-accepted'
    current = built['source407_hashes']
    assert len(current) == 407 and all(sha(L / 'source' / n) == h for n, h in current.items())
    targeted_path = L / 'targeted-regression-a/report.json'
    targeted = json.loads(targeted_path.read_text())
    assert targeted['status'] == 'FAIL-retained' and targeted['source407_and_fixtures_exact_after']
    assert sorted(targeted['failures']) == [['mmc3', 'expanded-environment'], ['mmc5', 'expanded-environment']]
    valid = [c for c in targeted['cases'] if c['test'] != 'expanded-environment']
    assert len(valid) == 68 and all(c['passed'] and c['exit'] == 0 for c in valid)
    staged_path = ROOT / 'build/verification/root49-integrated-private-build-k/staged-current-summary.json'
    staged = json.loads(staged_path.read_text())
    known = {(c['test'], c['rom']) for c in staged['unchanged_cases'] + staged['separately_executed']}
    assert all((c['test'], 'smb-crossover-' + c['mapper']) in known for c in valid)
    assert not any(test == 'expanded-environment' for test, _ in known)
    helper = ROOT / 'tests/expanded-environment.lua'
    assert 'local c=assert(EXPANDED_CHARACTER)' in helper.read_text()
    refs = {'private_build': L / 'report.json', 'K_staged_regression': staged_path,
            'targeted_original_with_two_helper_setup_negatives': targeted_path,
            'source_backed_crouch_geometry': ROOT / 'build/verification/agent49f-samus-crouch-source-audit-a/report.json',
            'water_actual_review': ROOT / 'build/verification/agent49l-samus-water-order-actual-review-d/freeze.json'}
    for mapper in ('mmc3', 'mmc5'):
        cpu_path = ROOT / f'build/verification/agent49l-samus-water-order-cpu-c/cpu-l-{mapper}-root-c.json'
        cpu = json.loads(cpu_path.read_text())
        assert cpu['status'] == 'PASS_FOCUSED_SOURCE_ORACLE_FULL_ABI_RAM_STACK'
        assert cpu['planned_cases'] == cpu['completed_cases'] == 1000 and not cpu['failures']
        native_path = ROOT / f'build/verification/agent49l-samus-water-order-component-b/native-l-m{3 if mapper == "mmc3" else 5}-root-a.json'
        native = json.loads(native_path.read_text())
        assert native['status'] == 'PASS_ACTUAL_SOURCE_ORDER_REVISION' and native['cases'] == 53
        assert not native['source_actual_coordinate_velocity_differences'] and not native['unexpected_control_differences']
        assert len(native['source_velocity_differences']) == 4 and len(native['initial_vs_current_coordinate_water_differences']) == 5
        refs['CPU_' + mapper] = cpu_path
        refs['native_' + mapper] = native_path
    with zipfile.ZipFile(G / 'source-v49.zip') as z:
        before = json.loads(z.read('archived-file-hashes.json'))
    assert len(before) == 404 and all(sha(ROOT / n) == h for n, h in before.items())
    assert sha(ROOT / 'build/smb-crossover-mmc3.nes') == '547fc4ef8803db040f8eed3fb1b4a309aac2257b35842a81b84f4bea54295931'
    assert sha(ROOT / 'build/smb-crossover-mmc5.nes') == 'e8a85e48f68bc0e2a3bf6f78227b58b5d9e49126b1a485fba870a865bc957652'
    sys.path.insert(0, str(ROOT / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(ROOT)
    assert used + 150_000_000 < 30_000_000_000
    OUT.mkdir()
    validation = OUT / 'validation'
    validation.mkdir()
    (validation / 'valid-targeted-68.json').write_text(json.dumps(dict(status='PASS-68-valid-established-cases',
        cases=valid, original_report_sha256=sha(targeted_path), excluded_helper_setup_failures=targeted['failures'],
        qualification='expanded-environment.lua is a non-standalone helper requiring EXPANDED_CHARACTER; both nil-setup negatives are retained, never relabelled PASS. Not a full L suite.'), indent=2) + '\n')
    archive = L / 'source-water-l.zip'
    assert sha(archive) == built['source_archive_sha256']
    shutil.copyfile(archive, OUT / 'source-v49.zip')
    changed = [n for n, h in current.items() if before.get(n) != h]
    assert len(changed) == 9
    for n in changed:
        target = ROOT / n
        if n not in before:
            assert not target.exists()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((L / 'source' / n).read_bytes())
    assert all(sha(ROOT / n) == h for n, h in current.items())
    report = dict(status='building-provisional-L', accepted_release=False, stable_checkpoint='roster-audit-v48',
                  goal_complete=False, previous_working_checkpoint=G.name, compiler_source_files=407,
                  source_sha256=sha(OUT / 'source-v49.zip'), source_hashes=current, changed_shared_sources=changed,
                  executed_validation=dict(existing_targeted_cases=68, source_native_arenas_per_mapper=53,
                                           focused_source_oracle_CPU_calls_per_mapper=1000),
                  K_staged_761_is_historical_not_a_full_L_run=True,
                  validation_references={n: dict(path=str(p.relative_to(ROOT)), sha256=sha(p)) for n, p in refs.items()},
                  known_limits=['Full roster ordinary runs, all weapons, lag optimization and final recordings remain incomplete.',
                                'Ryu moving-platform lifecycle is separate and unshipped.',
                                'Audio owner-transfer optimization is separate and unshipped.',
                                'Four seed-coordinate water velocity differences and five ground fraction qualifications remain; current-coordinate mismatches zero in the focused native component.'],
                  workspace_before_bytes=used, builds=[])
    manifest = OUT / 'manifest.json'
    def save():
        manifest.write_text(json.dumps(report, indent=2) + '\n')
    save()
    for mapper in ('mmc3', 'mmc5'):
        with (OUT / f'build-{mapper}.log').open('w', encoding='utf-8') as log:
            done = subprocess.run([sys.executable, 'tools/build.py', '--mapper', mapper], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        assert done.returncode == 0
        rom = ROOT / f'build/smb-crossover-{mapper}.nes'
        private = L / f'source/build/{rom.name}'
        assert rom.read_bytes() == private.read_bytes()
        assert rom.with_suffix('.lbl').read_bytes() == private.with_suffix('.lbl').read_bytes()
        for extension in ('.nes', '.lbl', '.dbg', '.map', '.lst'):
            shutil.copyfile(rom.with_suffix(extension), OUT / rom.with_suffix(extension).name)
        report['builds'].append(dict(mapper=mapper, ROM_sha256=sha(rom), LBL_sha256=sha(rom.with_suffix('.lbl')),
                                    DBG_sha256=sha(rom.with_suffix('.dbg')), exact_private_ROM_and_LBL=True))
        save()
    assert all(sha(ROOT / n) == h for n, h in current.items())
    report.update(status='provisional-L-focused-validated-full-goal-incomplete', source407_exact_after=True,
                  workspace_after_bytes=workspace_bytes(ROOT))
    save()
    print(json.dumps({k: v for k, v in report.items() if k not in ('source_hashes', 'validation_references')}, indent=2), flush=True)


if __name__ == '__main__':
    main()
