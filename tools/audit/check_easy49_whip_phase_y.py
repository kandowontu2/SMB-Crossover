"""Verify active source rectangles/phase plus foreign weapon regressions on Y."""
from pathlib import Path
import hashlib, json, shutil, subprocess, sys
R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-easy-whip-phase-y'
F = V / 'agent-lsr-easy-link-freeze-phase-n'
L = V / 'agent-lsr-easy-link-rect-animation-k'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    build = json.loads((H / 'report.json').read_text())
    assert build['status'] == 'PASS_PRIVATE_WHIP_AND_PHASE_Y_BUILD_ONLY'
    assert all(sha(H / 'source' / n) == h for n, h in build['source_hashes'].items())
    out = H / 'native/checks-a';out.mkdir(parents=True, exist_ok=False)
    for parent, name, target in [(F, 'bind.py', 'bind-phase.py'), (F, 'component.lua', 'component.lua'),
                                 (L, 'bind_rect.py', 'bind_rect.py'), (L, 'rect_component.lua', 'rect_component.lua')]:
        shutil.copyfile(parent / name, H / target)
        assert sha(parent / name) == sha(H / target)
    report = dict(status='RUNNING_PRIVATE_WHIP_PHASE_Y_CHECKS', script_sha256=sha(__file__),
                  build_sha256=sha(H / 'report.json'), rows=[], route_proof=False)

    def save():
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')

    save()
    for mapper in ['mmc3', 'mmc5']:
        rom = H / 'source/build' / ('smb-crossover-' + mapper + '.nes')
        for kind, binder, extra in [('phase', 'bind-phase.py', ['n']), ('rectangles', 'bind_rect.py', [])]:
            tag = 'source-' + kind + '-' + mapper + '-a'
            bound = subprocess.run([sys.executable, str(H / binder)] + extra + [mapper, tag], cwd=R, capture_output=True)
            (out / (tag + '-binding.log')).write_bytes(bound.stdout + bound.stderr)
            assert bound.returncode == 0
            argv = json.loads(bound.stdout.decode().splitlines()[-1])
            log = out / (tag + '-run.log')
            with log.open('wb') as f:
                rc = subprocess.run(argv, cwd=R, stdout=f, stderr=subprocess.STDOUT).returncode
            result_path = H / tag / 'native-output/result.json'
            result = json.loads(result_path.read_text()) if result_path.exists() else None
            report['rows'].append(dict(mapper=mapper, kind=kind, exit=rc, result=result,
                                       result_sha256=sha(result_path) if result_path.exists() else None,
                                       binding_sha256=sha(H / tag / 'binding.json'), log_sha256=sha(log)))
            save();print(mapper, kind, rc, flush=True)
        for name in ['megaman-buster', 'samus-weapon-families', 'pit-attacks', 'rygar-attacks',
                     'ryu-source-weapons', 'bass-weapons', 'sophia-independent-weapons',
                     'link-weapon-profile-202', 'simon-weapon-profile-202']:
            wrapper = out / (mapper + '-' + name + '.lua')
            bootstrap = (R / 'tests/menu-bootstrap.lua').as_posix()
            test = R / 'tests' / (name + '.lua')
            wrapper.write_text('dofile(' + json.dumps(bootstrap) + ')\ndofile(' + json.dumps(test.as_posix()) + ')\n')
            log = out / (mapper + '-' + name + '.log')
            with log.open('wb') as f:
                rc = subprocess.run([sys.executable, str(R / 'tools/run_mesen.py'), str(wrapper), str(rom),
                                     '--timeout', '120'], cwd=R, stdout=f, stderr=subprocess.STDOUT).returncode
            report['rows'].append(dict(mapper=mapper, kind=name, exit=rc, log_sha256=sha(log),
                                       original_test_sha256=sha(test), wrapper_sha256=sha(wrapper)))
            save();print(mapper, name, rc, flush=True)
    passed = all(row['exit'] == 0 for row in report['rows'])
    report['status'] = 'PASS_ALL_TWENTY_TWO_WHIP_PHASE_Y_CHECK_GROUPS' if passed else 'RETAINED_WHIP_PHASE_Y_CHECK_FAILURES'
    save();print(report['status'], sha(out / 'report.json'), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
