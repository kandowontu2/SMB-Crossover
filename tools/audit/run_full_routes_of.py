"""Bind the existing controller-only 1-1 runner to all 37 named identities.

Only its profile/name tables are extended. The emulated-game audit, clear/death
criteria and controller replay logic remain the pinned ND implementation.
Discovery failures stay recorded; a route is verified only by a fresh replay.
"""
from pathlib import Path
import argparse
import concurrent.futures
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_SHA = '327233bd42a2abb8c8daaee823065da7851121c00392cb957664f88ff9cc0631'
ADDED = {
    'mario': (0, 0, 'MarioVariant', 0),
    'luigi': (0, 8, 'MarioVariant', 1),
    'megaman': (1, 1, 'ProtoVariant', 0),
    'samus': (2, 2, None, 0),
    'bill': (3, 3, 'BillVariant', 0),
    'lance': (3, 3, 'BillVariant', 1),
    'link': (4, 4, 'Z2Variant', 0),
    'simon': (5, 5, 'Cv3Variant', 0),
    'pit': (6, 6, None, 0),
    'rygar': (7, 7, None, 0),
    'scrooge': (8, 12, 'DarkwingVariant', 0),
    'bass': (9, 9, 'RlVariant', 0),
    'ryu': (10, 10, None, 0),
    'sophia': (11, 11, None, 0),
}
NAMES = dict(megaman='MEGA MAN', samus='SAMUS ARAN', bill='BILL RIZER',
             lance='LANCE BEAN', simon='SIMON BELMONT', scrooge='SCROOGE MCDUCK',
             ryu='RYU HAYABUSA', sophia='SOPHIA III')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--phase', choices=('discover', 'replay'), required=True)
    p.add_argument('--names', nargs='+', required=True)
    p.add_argument('--modes', nargs='+', choices=('easy', 'hard'), default=['easy', 'hard'])
    p.add_argument('--policy', type=Path, default=ROOT / 'tools/playthroughs/new_roster_policy_nd.lua')
    p.add_argument('--frames', type=int, default=10000)
    p.add_argument('--timeout', type=int, default=120)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=True)
    result_path = a.output / f'{a.phase}-results.json'
    assert not result_path.exists()
    template = ROOT / 'tools/playthroughs/new_roster_run_nd.py'
    assert sha(template) == TEMPLATE_SHA
    source = template.read_text()
    anchor = 'ROOT=Path(__file__).resolve().parents[2]'
    assert source.count(anchor) == 1
    source = source.replace(anchor, 'ROOT=Path(' + repr(ROOT.as_posix()) + ')')
    anchor = '\ndef main():\n'
    assert source.count(anchor) == 1
    source = source.replace(anchor, '\nPROFILES.update(' + repr(ADDED) + ')\n' + anchor)
    anchor = ' names=dict(proto='
    assert source.count(anchor) == 1
    additions = ''.join(k + '=' + repr(v) + ',' for k, v in NAMES.items())
    source = source.replace(anchor, ' names=dict(' + additions + 'proto=')
    # ND's original observer is correct for its explicit expanded pages. The
    # fourteen legacy identities additionally require the logical CHR map.
    anchor = "  observer=(ROOT/'tools/audit/chr_commit_observer.lua').read_text()"
    assert source.count(anchor) == 1
    source = source.replace(anchor,
        "  observer=(ROOT/('tools/audit/legacy_chr_observer_of.lua' if a.name in "
        + repr(tuple(ADDED)) + " else 'tools/audit/chr_commit_observer.lua')).read_text()")
    driver = a.output / 'bound-runner.py'
    if driver.exists():
        assert driver.read_text() == source
    else:
        driver.write_text(source)
    # Load only declarations to validate every selected profile before any run.
    namespace = {'__name__': 'bound_profiles', '__file__': str(driver)}
    exec(compile(source, str(driver), 'exec'), namespace)
    assert len(namespace['PROFILES']) == 37
    assert len(set(a.names)) == len(a.names) and all(n in namespace['PROFILES'] for n in a.names)

    def run(case):
        name, mode = case
        folder = a.output / f'{a.phase}-{name}-{mode}-v1'
        policy = (ROOT / 'tools/playthroughs/mac_easy_policy_nv.lua') if name == 'mac' else a.policy
        command = [sys.executable, str(driver), name, '--rom', str(a.rom.resolve()),
                   '--output', str(folder), '--behavior', mode, '--frames', str(a.frames),
                   '--capture', '1' if a.phase == 'replay' else '12', '--chr-commit',
                   '--policy', str(policy.resolve()), '--timeout', str(a.timeout)]
        discovery = a.output / f'discover-{name}-{mode}-v1'
        if a.phase == 'replay':
            m = json.loads((discovery / 'manifest.json').read_text())
            if m['exit'] != 0 or not m.get('result', {}).get('cleared'):
                return dict(identity=name, mode=mode, passed=False, skipped=True,
                            reason='Discovery did not clear; retained failure requires investigation.')
            command += ['--replay', str(discovery / 'inputs.csv')]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        (a.output / f'{a.phase}-{name}-{mode}-host.log').write_text(result.stdout + result.stderr)
        m = json.loads((folder / 'manifest.json').read_text()) if (folder / 'manifest.json').exists() else {}
        state = m.get('result', {})
        comparisons = {}
        if a.phase == 'replay' and result.returncode == 0:
            comparisons = {n: (folder / n).read_bytes() == (discovery / n).read_bytes()
                           for n in ['inputs.csv', 'trace.csv']}
        passed = result.returncode == 0 and state.get('cleared') and state.get('deaths') == 0
        passed = passed and m.get('chr_commit', {}).get('passed') is True
        if a.phase == 'replay':
            passed = passed and all(comparisons.values()) and len(comparisons) == 2
        return dict(identity=name, mode=mode, passed=bool(passed), exit=result.returncode,
                    frames=state.get('frames'), deaths=state.get('deaths'), failure=state.get('failure'),
                    exact_discovery_bytes=comparisons, folder=str(folder),
                    manifest_sha256=sha(folder / 'manifest.json') if m else None)

    cases = [(name, mode) for name in a.names for mode in a.modes]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(run, cases))
    report = dict(passed=all(q['passed'] for q in results), ROM_sha256=sha(a.rom),
                  phase=a.phase, template_sha256=sha(template), bound_runner_sha256=sha(driver),
                  policy_sha256=sha(a.policy), wrapper_sha256=sha(Path(__file__)),
                  legacy_chr_observer_sha256=sha(ROOT / 'tools/audit/legacy_chr_observer_of.lua'),
                  controller_only=True, memory_writes=False, runs=results,
                  scope='Explicit named subset of all37. Cold actual menus, existing clear/death/CHR criteria. Discovery is not a replay or all-items claim.')
    result_path.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
