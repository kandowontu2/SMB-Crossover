"""Execute frozen O body/platform/terrain components on actual combined AP."""
from pathlib import Path
import hashlib, importlib.util, json, shutil, subprocess, sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-easy-advanced-union-ap'
F = V / 'agent-lsr-ryu-source-body-o'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert sha(H / 'report.json') == 'e1215e073905879a580fea13dfe55dad26d9fe11a0595bbe7fbfdf915a822b6e'
    build = json.loads((H / 'report.json').read_text())
    assert all(sha(H / 'source' / n) == h for n, h in build['source_hashes'].items())
    frozen = json.loads((F / 'implementation-freeze-o.json').read_text())
    review = json.loads((R / frozen['actual_review']['path']).read_text())
    assert sha(R / frozen['actual_review']['path']) == frozen['actual_review']['sha256']
    out = H / 'native/checks-as';out.mkdir(parents=True, exist_ok=False)
    for name in ['prepare_component_c.py', 'component-c.lua', 'bind_platform_c.py', 'prepare_edges_b.py', 'edges-b.lua']:
        shutil.copyfile(F / name, H / name)
    report = dict(status='RUNNING_COMBINED_AP_FROZEN_O_COMPONENTS', script_sha256=sha(__file__),
                  build_sha256=sha(H / 'report.json'), freeze_sha256=sha(F / 'implementation-freeze-o.json'),
                  rows=[], route_proof=False, accepted_release=False, goal_complete=False)
    def save():
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    save()
    for mapper in ['mmc3', 'mmc5']:
        base = {x['tag']: x for x in review['native'][mapper]}
        for kind, binder, args, folder_name, parent_name in [
            ('body', 'prepare_component_c.py', ['o', mapper, 'rebound-body-' + mapper + '-aj'], 'rebound-body-' + mapper + '-aj', 'o-' + mapper + '-positive-h'),
            ('platform', 'bind_platform_c.py', [mapper], 'platform-' + mapper + '-c', 'platform-' + mapper + '-c'),
            ('edges', 'prepare_edges_b.py', [mapper], 'edges-' + mapper + '-b', 'edges-' + mapper + '-b')]:
            parent = base[parent_name]
            assert sha(R / parent['binding']['path']) == parent['binding']['sha256']
            old = json.loads((R / parent['binding']['path']).read_text())
            bound = subprocess.run([sys.executable, str(H / binder)] + args, cwd=R, capture_output=True)
            (out / (kind + '-' + mapper + '-binding.log')).write_bytes(bound.stdout + bound.stderr)
            assert bound.returncode == 0, bound.stderr
            folder = H / folder_name
            actual = json.loads((folder / 'binding.json').read_text())
            if kind == 'body':
                assert actual['core_sha256'] == old['core_sha256'] == sha(H / 'component-c.lua')
                assert actual['cases_sha256'] == old['cases_sha256']
            elif kind == 'edges':
                assert actual['core_sha256'] == old['core_sha256'] == sha(H / 'edges-b.lua')
                assert actual['cases'] == old['cases']
            else:
                assert actual['core']['sha256'] == old['core']['sha256']
                assert actual['setup_extension'] == old['setup_extension']
            log = out / (kind + '-' + mapper + '-run.log')
            with log.open('wb') as f:
                rc = subprocess.run(actual['argv'], cwd=R, stdout=f, stderr=subprocess.STDOUT).returncode
            result_path = folder / 'native-output/result.json'
            result = json.loads(result_path.read_text()) if result_path.exists() else None
            good = bool(rc == 0 and result and result['failures'] == 0)
            if result and 'setup_failures' in result:
                good = good and result['setup_failures'] == 0
            report['rows'].append(dict(mapper=mapper, kind=kind, exit=rc, passed=good, result=result,
                                       binding_sha256=sha(folder / 'binding.json'), parent_binding_sha256=parent['binding']['sha256'],
                                       result_sha256=sha(result_path) if result_path.exists() else None, log_sha256=sha(log)))
            save();print(mapper, kind, rc, good, None if not result else {k: v for k, v in result.items() if k != 'results'}, flush=True)
        test = R / 'tests/ryu-ground-wall-launch.lua'
        wrapper = out / ('terrain-' + mapper + '.lua')
        wrapper.write_text('TEST_DIR=' + json.dumps((R / 'tests').as_posix() + '/') + '\ndofile(' + json.dumps(test.as_posix()) + ')\n')
        rom = H / 'source/build' / ('smb-crossover-' + mapper + '.nes')
        log = out / ('terrain-' + mapper + '-run.log')
        with log.open('wb') as f:
            rc = subprocess.run([sys.executable, str(R / 'tools/run_mesen.py'), str(wrapper), str(rom), '--timeout', '180'], cwd=R, stdout=f, stderr=subprocess.STDOUT).returncode
        native = V / (rom.stem + '-' + wrapper.stem + '.log')
        text = native.read_text() if native.exists() else ''
        good = rc == 0 and '20 actual-input arenas' in text
        report['rows'].append(dict(mapper=mapper, kind='terrain', exit=rc, passed=good, cases=20,
                                   test_sha256=sha(test), wrapper_sha256=sha(wrapper), log_sha256=sha(log),
                                   native_log_sha256=sha(native) if native.exists() else None))
        save();print(mapper, 'terrain', rc, good, flush=True)
    assert all(sha(H / 'source' / n) == h for n, h in build['source_hashes'].items())
    passed = len(report['rows']) == 8 and all(x['passed'] for x in report['rows'])
    report['status'] = 'PASS_COMBINED_AP_ALL_EIGHT_O_BODY_PLATFORM_TERRAIN_GROUPS' if passed else 'RETAINED_COMBINED_AP_O_COMPONENT_FAILURES'
    save();print(report['status'], sha(out / 'report.json'), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
