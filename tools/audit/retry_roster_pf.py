"""Retry explicit failed pairs with frozen previously successful controls.

One native worker; no emulated state, equipment, physics or terrain writes.
These are discoveries only, never independent replay claims.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = Path('C:/Users/kando/Videos/SMB Crossover Archive')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT.resolve())
    out.mkdir(parents=True, exist_ok=False)
    parent = ARCHIVE / '2026-10-24-roster-pe/matrix-v1'
    previous = json.loads((parent / 'discover-results.json').read_text())
    digest = sha(a.rom)
    assert digest == previous['ROM_sha256']
    driver = parent / 'bound-runner.py'
    assert sha(driver) == previous['bound_runner_sha256']
    old_policy = ARCHIVE / '2026-10-24-matrix-om/policies-v3/policy.lua'
    assert sha(old_policy) == '550622acf3b3f7ddc3fea34eefb6180e11697578292825ccc152bd936153ea06'
    nav = ROOT / 'tools/playthroughs/mario_luigi_scrooge_nav.lua'
    admitted = json.loads((ARCHIVE / '2026-10-24-matrix-om/strict-guarded-v1/proof.json').read_text())['admitted']
    cases = [r for r in previous['runs'] if not r['passed'] and r['identity'] + '-' + r['mode'] in admitted]
    cases += [r for r in previous['runs'] if r['identity'] == 'mario' and r['mode'] == 'hard']
    assert len(cases) == 6
    policy = out / 'policy.lua'
    text = 'local restored=(function()\n' + old_policy.read_text() + '\nend)()\n'
    text += 'local travel=(function()\n' + nav.read_text() + '\nend)()\n'
    text += "return function(c)if ROSTER_CONFIG.name=='mario' and ROSTER_CONFIG.behavior=='hard' then return travel(c)end;return restored(c)end\n"
    assert 'emu.write(' not in text and 'dofile(' not in text
    policy.write_text(text)
    report = dict(passed=False, complete=False, goal_complete=False, phase='discover',
        ROM_sha256=digest, controller_only=True, memory_writes=False, native_workers=1,
        previous_discovery_index_sha256=sha(parent / 'discover-results.json'),
        bound_runner_sha256=sha(driver), policy_sha256=sha(policy),
        source_policy_sha256=sha(old_policy), source_navigation_sha256=sha(nav),
        wrapper_sha256=sha(Path(__file__)), runs=[],
        scope='Five previously proven per-case OM controls restored after broad PE controller regression; Mario Hard uses ordinary existing navigation. All original negatives retained. Current discoveries still require independent exact replays and visual/item review.')
    for case in cases:
        name, mode = case['identity'], case['mode']
        folder = out / ('discover-' + name + '-' + mode + '-v1')
        command = [sys.executable, str(driver), name, '--rom', str(a.rom.resolve()),
            '--output', str(folder), '--behavior', mode, '--frames', '10000', '--capture', '12',
            '--chr-commit', '--policy', str(policy), '--timeout', '180']
        with (out / (name + '-' + mode + '.log')).open('w') as log:
            code = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT).returncode
        manifest = folder / 'manifest.json'
        m = json.loads(manifest.read_text()) if manifest.exists() else {}
        result = m.get('result', {})
        entry = dict(identity=name, mode=mode, exit=code,
            passed=code == 0 and result.get('cleared') is True and result.get('deaths') == 0 and m.get('chr_commit', {}).get('passed') is True,
            frames=result.get('frames'), deaths=result.get('deaths'), failure=result.get('failure'),
            folder=str(folder), manifest_sha256=sha(manifest) if m else None,
            replaces_no_original_evidence=True)
        report['runs'].append(entry)
        (out / 'progress.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(entry), flush=True)
    report['complete'] = True
    report['passed'] = all(r['passed'] for r in report['runs'])
    (out / 'discover-results.json').write_text(json.dumps(report, indent=2) + '\n')
    (out / 'progress.json').write_text(json.dumps(report, indent=2) + '\n')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
