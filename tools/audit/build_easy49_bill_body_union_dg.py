"""Privately combine frozen Bill body source with CG's disjoint baseline guards."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
F = V / 'agent49-bill-source-body-f'
H = V / 'root49-bill-body-union-dg'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    freeze_path = F / 'source-freeze-j.json'
    assert sha(freeze_path) == '5d5ab8ab8852c16630cec3e0c619868bae1e89d43776dd839a8dbd101ab36f96'
    freeze = json.loads(freeze_path.read_text())
    catalog = F / 'source-final-f-catalog.json'
    assert sha(catalog) == freeze['final_catalog_sha256'] == 'abf622639ea0e2e878076c10da00577e058ba6c809b1cad861796d71414140ae'
    expected = json.loads(catalog.read_text())
    original = Path(freeze['source'])
    assert len(expected) == 441 and all(sha(original / n) == h for n, h in expected.items())
    cg_path = V / 'root49-easy-combined-cg/report.json'
    assert sha(cg_path) == '519570a4a54bd9f588dec8ec621120bb223b7b4df0cd5c6738a34d3719165989'
    cg = json.loads(cg_path.read_text())
    assert set(cg['source_changes']) == {'src/collision.s'}
    change = cg['source_changes']['src/collision.s']
    assert expected['src/collision.s'] == change['before']
    assert sha(R / 'src/collision.s') == cg['source_hashes']['src/collision.s'] == change['after']
    published = R / 'build/checkpoints/roster-audit-v49-easy-hard-by/manifest.json'
    assert sha(published) == 'fe005475a409894834268bdd203efde78df0275a124a5d13def3bb6816f098c7'
    installed = json.loads(published.read_text())
    assert all(sha(R / n) == h for n, h in installed['source_hashes'].items())
    H.mkdir(exist_ok=False)
    source = H / 'source'
    for name in expected:
        target = source / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original / name, target)
    shutil.copyfile(R / 'src/collision.s', source / 'src/collision.s')
    expected['src/collision.s'] = change['after']
    generated_path = F / 'generated-build-inputs-a.json'
    generated = json.loads(generated_path.read_text())
    assert len(generated) == 11
    for name, digest in generated.items():
        old = original / 'build/generated' / name
        assert sha(old) == digest
        target = source / 'build/generated' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(old, target)
    driver_source = F / 'build-driver-a.py'
    driver = H / 'build-driver.py'
    text = driver_source.read_text()
    needle = 'ROOT = Path(' + repr(str(original)) + ')'
    assert text.count(needle) == 1
    driver.write_text(text.replace(needle, 'ROOT = Path(' + repr(str(source)) + ')'))
    report = dict(status='PRIVATE_DG_BODY_F_PLUS_CG_BASELINE_GUARDS_BUILDING',
        script_sha256=sha(__file__), source_freeze_sha256=sha(freeze_path),
        parent_source_catalog_sha256=sha(catalog), CG_report_sha256=sha(cg_path),
        generated_inputs_sha256=sha(generated_path), generated_inputs=generated,
        driver_source_sha256=sha(driver_source), driver_sha256=sha(driver),
        source_hashes=expected, source_files=441,
        merge=dict(path='src/collision.s', method='DISJOINT_CG_BASELINE_ONLY_DELTA',
                   body_F_equals_BQ_before=change['before'], CG_after=change['after']),
        builds=[], main_changed=False, source_body_admission_pending=True,
        accepted_release=False, goal_complete=False,
        qualification='Private source union only. Both crossover ROMs must be byte-exact frozen body F and both disabled-crossover baselines exact CG. Final source-body native/head/cost/reset admission remains pending; no new public ROM is installed.')
    def save():
        (H / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    save()
    baseline_shas = dict(mmc3='0511c6844d0e9fa61f4b4fbc34e6f9c67d8247d3ca964ebbb0c9c2718cdc5146',
                         mmc5='34858561f4825dcc96cdd5fd46872f9230890c93af95351720c8536155f5cbbd')
    for baseline in [False, True]:
        for mapper in ['mmc3', 'mmc5']:
            tag = mapper + ('-baseline' if baseline else '')
            log = H / (tag + '-build.log')
            command = [sys.executable, str(driver), '--mapper', mapper] + (['--baseline'] if baseline else [])
            with log.open('wb') as stream:
                rc = subprocess.run(command, cwd=R, stdout=stream, stderr=subprocess.STDOUT).returncode
            row = dict(mapper=mapper, baseline=baseline, exit=rc, log_sha256=sha(log))
            report['builds'].append(row)
            save()
            assert rc == 0, log
            name = 'smb-crossover-' + tag
            rom = source / 'build' / (name + '.nes')
            row['rom_sha256'] = sha(rom)
            expected_rom = baseline_shas[mapper] if baseline else freeze['ROMs'][mapper]
            row['expected_rom_sha256'] = expected_rom
            row['exact_expected_rom'] = sha(rom) == expected_rom
            row['artifacts'] = {ext: sha(source / 'build' / (name + '.' + ext)) for ext in ['nes', 'lbl', 'map', 'dbg']}
            save()
            assert row['exact_expected_rom'], row
    assert all(sha(source / n) == h for n, h in expected.items())
    assert all(sha(original / n) == h for n, h in json.loads(catalog.read_text()).items())
    assert all(sha(R / n) == h for n, h in installed['source_hashes'].items())
    report['status'] = 'PASS_PRIVATE_DG_CROSSOVER_EXACT_BODY_F_BASELINES_EXACT_CG_ADMISSION_PENDING'
    save()
    print(report['status'], sha(H / 'report.json'), flush=True)


if __name__ == '__main__':
    main()
