"""Rebind exact frozen Link test cores using their unchanged symbol binders."""
from pathlib import Path
import hashlib, json, shutil, subprocess, sys
R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-easy-union-t'
P = V / 'agent-lsr-easy-link-rect-animation-k'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert sha(H / 'report.json') == '99b62c608a5fb96c1c121c00cba9edafe0514333d11b939597474a09348278e9'
    report = dict(status='RUNNING_COMBINED_T_LINK_COMPONENTS', script_sha256=sha(__file__),
                  build_sha256=sha(H / 'report.json'), files={}, rows=[], route_proof=False)
    path = H / 'link-native-report.json'

    def save():
        path.write_text(json.dumps(report, indent=2) + '\n')

    kinds = [('rectangles', 'bind_rect.py', 'rect_component.lua'),
             ('animation', 'bind_animation_l.py', 'animation_component_l.lua'),
             ('art', 'bind_art_l.py', 'art_component_l.lua'),
             ('death', 'bind_death_l.py', 'death_component_l.lua')]
    for _, binder, core in kinds:
        for name in [binder, core]:
            assert not (H / name).exists()
            shutil.copyfile(P / name, H / name)
            report['files'][name] = sha(H / name)
            assert sha(H / name) == sha(P / name)
    save()
    for mapper in ['mmc3', 'mmc5']:
        for kind, binder, core in kinds:
            tag = 'link-' + kind + '-' + mapper + '-a'
            bound = subprocess.run([sys.executable, str(H / binder), mapper, tag], cwd=R, capture_output=True)
            (H / (tag + '-binding.log')).write_bytes(bound.stdout + bound.stderr)
            assert bound.returncode == 0, (mapper, kind, bound.stderr.decode(errors='replace'))
            argv = json.loads(bound.stdout.decode().splitlines()[-1])
            log = H / (tag + '-run.log')
            with log.open('wb') as f:
                rc = subprocess.run(argv, cwd=R, stdout=f, stderr=subprocess.STDOUT).returncode
            result_path = H / tag / 'native-output/result.json'
            result = json.loads(result_path.read_text()) if result_path.exists() else None
            report['rows'].append(dict(mapper=mapper, kind=kind, exit=rc, result=result,
                                       result_sha256=sha(result_path) if result_path.exists() else None,
                                       binding_sha256=sha(H / tag / 'binding.json'), log_sha256=sha(log)))
            save()
            print(mapper, kind, rc, flush=True)
            assert rc == 0 and result is not None
    report['status'] = 'PASS_COMBINED_T_ALL_EIGHT_LINK_NATIVE_GROUPS'
    save()
    print(report['status'], sha(path), flush=True)


if __name__ == '__main__':
    main()
