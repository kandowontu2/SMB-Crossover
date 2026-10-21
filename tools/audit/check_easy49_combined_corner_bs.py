"""Rebind frozen E corner controls to the actual BQ mapper images."""
from pathlib import Path
import hashlib, json, shutil, subprocess, sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-easy-combined-bq'
F = V / 'agent-lsr-ryu-corner-head-e'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert sha(H / 'report.json') == '2736ac1e4238d237fce859e18ae29f7ef137ed4b2f386e3078c2a2438021e838'
    assert sha(F / 'implementation-freeze.json') == 'ac4095308afe1256e708254a2b68423795e889b916b4d89c24fba41b23402878'
    frozen = json.loads((F / 'implementation-freeze.json').read_text())
    assert all(sha(F / n) == h for n, h in frozen['files'].items())
    build = json.loads((H / 'report.json').read_text())
    assert all(sha(H / 'source' / n) == h for n, h in build['source_hashes'].items())
    out = H / 'native/checks-bs'
    out.mkdir(parents=True, exist_ok=False)
    for name in ['prepare_native.py', 'component.lua', 'cost.lua']:
        shutil.copyfile(F / name, H / name)
    report = dict(status='RUNNING_BQ_FROZEN_RYU_CORNER_CONTROLS', script_sha256=sha(__file__),
                  build_sha256=sha(H / 'report.json'), freeze_sha256=sha(F / 'implementation-freeze.json'),
                  adapter='Verbatim frozen binder and Lua cores at equal folder depth; only mapper image and unique output tag vary.',
                  rows=[], route_proof=False, accepted_release=False, goal_complete=False)
    def save():
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    save()
    for mapper in ['mmc3', 'mmc5']:
        for mode in [0, 1]:
            tag = 'bq-bs-mode' + str(mode)
            binding_log = out / (mapper + '-' + str(mode) + '-binding.log')
            with binding_log.open('wb') as log:
                rc = subprocess.run([sys.executable, str(H / 'prepare_native.py'), mapper, 'b', tag, str(mode)],
                                    cwd=R, stdout=log, stderr=subprocess.STDOUT).returncode
            assert rc == 0, binding_log
            folder = H / ('b-' + mapper + '-native-' + tag)
            binding = json.loads((folder / 'binding.json').read_text())
            parent = json.loads((F / ('b-' + mapper + '-native-nativevel' + str(mode)) / 'binding.json').read_text())
            assert binding['core_sha256'] == parent['core_sha256'] == sha(H / 'component.lua')
            assert binding['cases'] == parent['cases'] and len(binding['cases']) == 42
            assert binding['rom_sha256'] == next(x['ROM_sha256'] for x in build['builds'] if x['mapper'] == mapper)
            log_path = out / (mapper + '-' + str(mode) + '-run.log')
            with log_path.open('wb') as log:
                rc = subprocess.run(binding['argv'], cwd=R, stdout=log, stderr=subprocess.STDOUT).returncode
            result_path = folder / 'native-output/result.json'
            result = json.loads(result_path.read_text()) if result_path.exists() else None
            good = bool(rc == 0 and result and result['cases'] == 42 and result['failures'] == result['setup_failures'] == 0)
            report['rows'].append(dict(mapper=mapper, mode=mode, exit=rc, passed=good, result=result,
                                       binding_sha256=sha(folder / 'binding.json'), parent_binding_sha256=sha(F / ('b-' + mapper + '-native-nativevel' + str(mode)) / 'binding.json'),
                                       result_sha256=sha(result_path) if result_path.exists() else None, log_sha256=sha(log_path)))
            save()
            print(mapper, mode, rc, good, result, flush=True)
    assert all(sha(H / 'source' / n) == h for n, h in build['source_hashes'].items())
    passed = len(report['rows']) == 4 and all(x['passed'] for x in report['rows'])
    report['status'] = 'PASS_BQ_ALL_168_FROZEN_RYU_CORNER_CONTROLS' if passed else 'RETAINED_BQ_RYU_CORNER_NEGATIVES'
    save()
    print(report['status'], sha(out / 'report.json'), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
