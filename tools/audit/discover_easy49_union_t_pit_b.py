"""Fresh Pit controller policy, removing only an obsolete S2 debug observer."""
from pathlib import Path
import hashlib, json, subprocess, sys
R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
T = V / 'root49-easy-union-t'
H = V / 'root49-easy-union-t-pit-route-b'
P = R / 'build/roster-through-2-2/agent49s2-pit-fixed-al-6-v0-mmc3/policy.lua'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not H.exists()
    assert sha(P) == '62ba298a9339cd20d5221c033b711729d409515d663ded754d2872f026cd9bd4'
    assert sha(T / 'report.json') == '99b62c608a5fb96c1c121c00cba9edafe0514333d11b939597474a09348278e9'
    H.mkdir()
    lines = P.read_text().splitlines()
    obsolete = [line for line in lines if line.startswith('PIT_LIFT_HOOKS=') or 'dofile(' in line]
    assert len(obsolete) == 2 and 'agent49s2-pit-firebar-p/observer.lua' in obsolete[1]
    policy = H / 'policy.lua'
    policy.write_text('\n'.join(line for line in lines if line not in obsolete) + '\n')
    assert 'emu.' not in policy.read_text() and 'dofile(' not in policy.read_text()
    report = dict(status='RUNNING_FRESH_PIT_CONTROLLER_DISCOVERY_T', script_sha256=sha(__file__),
                  parent_policy_sha256=sha(P), policy_sha256=sha(policy),
                  change='Remove only obsolete hard-coded S2 physical-bank debug observer; controller function body unchanged.',
                  build_sha256=sha(T / 'report.json'), controller_only=True, memory_or_register_writes=False,
                  record=False, goal_complete=False, rows=[])

    def save():
        (H / 'report.json').write_text(json.dumps(report, indent=2) + '\n')

    save()
    for mapper in ['mmc3', 'mmc5']:
        tag = 'root49t-pit-discovery-b'
        rom = T / 'source/build' / ('smb-crossover-' + mapper + '.nes')
        argv = [sys.executable, str(R / 'tools/playthroughs/roster_run.py'), '--character', '6', '--mapper', mapper,
                '--rom', str(rom), '--tag', tag, '--frames', '30000', '--timeout', '300',
                '--workspace-cap-gb', '50', '--policy', str(policy)]
        log = H / (mapper + '-run.log')
        with log.open('wb') as f:
            rc = subprocess.run(argv, cwd=R, stdout=f, stderr=subprocess.STDOUT).returncode
        folder = R / 'build/roster-through-2-2' / (tag + '-6-v0-' + mapper)
        p = folder / 'manifest.json'
        manifest = json.loads(p.read_text()) if p.exists() else None
        report['rows'].append(dict(mapper=mapper, exit=rc, output=folder.relative_to(R).as_posix(),
                                  result=manifest.get('result') if manifest else None,
                                  manifest_sha256=sha(p) if p.exists() else None, log_sha256=sha(log)))
        save()
        print(mapper, rc, report['rows'][-1]['result'], flush=True)
    report['status'] = 'DISCOVERY_RECORDED_REQUIRES_INDEPENDENT_FIXED_REPLAY'
    save()
    print(report['status'], sha(H / 'report.json'), flush=True)


if __name__ == '__main__':
    main()
