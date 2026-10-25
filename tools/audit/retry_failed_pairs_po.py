"""Bounded controller-only retries, sharing at most two native emulator slots."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = Path('C:/Users/kando/Videos/SMB Crossover Archive')
SLOTS = r'''$m=@(Get-CimInstance Win32_Process -Filter "Name = 'Mesen.exe'");
$g=@($m | Where-Object {$_.CommandLine -notmatch '--testRunner'});
$k=@(Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" | Where-Object {$_.CommandLine -like '*run_known_roster_pn.py*'});
[pscustomobject]@{mesen=$m.Count;gui=$g.Count;knownWorker=$k.Count}|ConvertTo-Json -Compress'''


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--policy', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--keys', nargs='+', required=True)
    a = p.parse_args()
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT.resolve())
    out.mkdir(parents=True, exist_ok=False)
    digest = sha(a.rom)
    driver = ARCHIVE / '2026-10-24-roster-pe/matrix-v1/bound-runner.py'
    assert sha(driver) == 'd6ab9cc1e938923797525704cf6d0e99e16fda6f007b98da1024cb167f00f167'
    assert set(a.keys) <= {'mario-hard', 'chip-easy', 'chip-hard', 'dale-hard'} and len(set(a.keys)) == len(a.keys)
    report = dict(passed=False, complete=False, goal_complete=False, phase='discover',
        ROM_sha256=digest, policy_sha256=sha(a.policy), bound_runner_sha256=sha(driver),
        wrapper_sha256=sha(Path(__file__)), controller_only=True, memory_writes=False,
        selected_cases=len(a.keys), runs=[], native_workers=1,
        scope='Explicit failed-pair controller retries. Actual menus, current ROM, original clear/death/CHR assertions and independent strict direct replay for a passing discovery. Source game/physics/equipment/terrain unchanged. Prior failures retained. Native-slot polling never closes or modifies the user emulator.')

    def save():
        (out / 'progress.json').write_text(json.dumps(report, indent=2) + '\n')

    def slot():
        while True:
            q = subprocess.run(['powershell', '-NoProfile', '-Command', SLOTS], capture_output=True, text=True)
            assert q.returncode == 0, q.stderr
            state = json.loads(q.stdout)
            if state['mesen'] < 2 and not (state['gui'] and state['knownWorker']):
                report.pop('waiting_for_native_slot', None)
                save()
                return
            report['waiting_for_native_slot'] = state
            save()
            time.sleep(2)

    def invoke(log_name, args):
        with (out / log_name).open('w') as log:
            return subprocess.run([sys.executable, *map(str, args)], cwd=ROOT,
                                  stdout=log, stderr=subprocess.STDOUT).returncode

    save()
    for key in a.keys:
        slot()
        assert sha(a.rom) == digest and sha(a.policy) == report['policy_sha256']
        name, mode = key.rsplit('-', 1)
        folder = out / ('discover-' + key + '-v1')
        code = invoke(key + '-discover.log', [driver, name, '--rom', a.rom.resolve(), '--output', folder,
            '--behavior', mode, '--frames', '10000', '--capture', '12', '--chr-commit',
            '--policy', a.policy.resolve(), '--timeout', '180'])
        path = folder / 'manifest.json'
        m = json.loads(path.read_text()) if path.exists() else {}
        result = m.get('result') or {}
        passed = code == 0 and result.get('cleared') is True and result.get('deaths') == 0 and m.get('chr_commit', {}).get('passed') is True
        entry = dict(identity=name, mode=mode, passed=False, discovery_passed=passed,
            exit=code, frames=result.get('frames'), failure=result.get('failure'),
            folder=str(folder), manifest_sha256=sha(path) if m else None)
        if passed:
            assert m['ROM_sha256'] == digest and not m['fixed_replay']
            index = out / ('discover-index-' + key + '.json')
            index.write_text(json.dumps(dict(passed=True, phase='discover', ROM_sha256=digest,
                runs=[dict(identity=name, mode=mode, passed=True, folder=str(folder), manifest_sha256=sha(path))]), indent=2) + '\n')
            slot()
            replay = out / ('replay-' + key + '-v1')
            entry['replay_exit'] = invoke(key + '-replay.log', [ROOT / 'tools/audit/replay_roster_pf.py',
                '--rom', a.rom.resolve(), '--discoveries', index, '--output', replay])
            entry['replay_batch'] = str(replay)
            if entry['replay_exit'] == 0:
                proof = json.loads((replay / 'proof.json').read_text())
                assert proof['passed'] and proof['complete'] and proof['ROM_sha256'] == digest
                entry['passed'] = True
                entry['replay_proof_sha256'] = sha(replay / 'proof.json')
        report['runs'].append(entry)
        save()
        print(json.dumps(entry), flush=True)
    report['complete'] = True
    report['passed'] = all(r['passed'] for r in report['runs'])
    save()
    (out / 'discover-results.json').write_text(json.dumps(report, indent=2) + '\n')
    return 0 if report['passed'] else 1


if __name__ == '__main__': main()
