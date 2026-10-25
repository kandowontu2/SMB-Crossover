"""Fresh same-hash discovery/replay pairs using each explicitly proven controller.

One QA Mesen worker, including the independent direct replay. Older successful
routes choose controls only; they never count as current-hash route coverage.
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
    p.add_argument('--baseline-status', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT.resolve())
    out.mkdir(parents=True, exist_ok=False)
    baseline_path = out / 'baseline-status.json'
    baseline_path.write_bytes(a.baseline_status.read_bytes())
    baseline = json.loads(baseline_path.read_text())
    parent = json.loads((ROOT / 'build/checkpoints/smb3-shrink-pc/manifest.json').read_text())
    current = json.loads((ROOT / 'build/checkpoints/grant-grip-pm/manifest.json').read_text())
    digest = sha(a.rom)
    assert digest == current['rom_sha256'] and baseline['ROM_sha256'] == parent['rom_sha256']
    assert baseline['strict_independent_direct_pairs'] == 63
    driver = ARCHIVE / '2026-10-24-roster-pe/matrix-v1/bound-runner.py'
    assert sha(driver) == 'd6ab9cc1e938923797525704cf6d0e99e16fda6f007b98da1024cb167f00f167'
    selected = []
    for key, pair in baseline['pairs'].items():
        if not pair['strict_replays']: continue
        assert not key.startswith('grant-')
        candidates = [(Path(path), q) for path, q in pair['discoveries'].items() if q['passed']]
        assert candidates
        path, recorded = candidates[0]
        assert sha(path) == recorded['manifest_sha256']
        manifest = json.loads(path.read_text())
        assert manifest['ROM_sha256'] == baseline['ROM_sha256'] and not manifest['fixed_replay']
        policy = path.parent / 'policy.lua'
        assert sha(policy) == manifest['policy_sha256']
        selected.append((key, path, manifest, policy))
    assert len(selected) == 63
    report = dict(passed=False, complete=False, goal_complete=False, ROM_sha256=digest,
        baseline_ROM_sha256=baseline['ROM_sha256'], baseline_status_sha256=sha(baseline_path),
        bound_runner_sha256=sha(driver), wrapper_sha256=sha(Path(__file__)),
        native_workers=1, selected_cases=len(selected), runs=[],
        scope='Fresh actual candidate cold-menu adaptive discoveries and independent exact same-hash physical-frame replays. Each case uses its explicitly previously proven frozen controller. Old-hash proofs only choose controls and provide an isolation regression comparison. Current Grant two-pair evidence is separate. Remaining nine prior failing pairs, every-item and all other goal gates stay open.')
    (out / 'progress.json').write_text(json.dumps(report, indent=2) + '\n')

    def invoke(log_name, args):
        with (out / log_name).open('w') as log:
            return subprocess.run([sys.executable, *map(str, args)], cwd=ROOT,
                                  stdout=log, stderr=subprocess.STDOUT).returncode

    for key, parent_manifest, before, policy in selected:
        name, mode = before['config']['name'], before['config']['behavior']
        folder = out / ('discover-' + key + '-v1')
        assert sha(a.rom) == digest and sha(policy) == before['policy_sha256']
        code = invoke('discover-' + key + '.log', [driver, name, '--rom', a.rom.resolve(),
            '--output', folder, '--behavior', mode, '--frames', before['config']['limit'],
            '--capture', '12', '--chr-commit', '--policy', policy, '--timeout', '180'])
        path = folder / 'manifest.json'
        m = json.loads(path.read_text()) if path.exists() else {}
        result = m.get('result') or {}
        discovered = code == 0 and result.get('cleared') is True and result.get('deaths') == 0 and m.get('chr_commit', {}).get('passed') is True
        entry = dict(identity=name, mode=mode, passed=False, discovery_passed=discovered,
            discovery_exit=code, frames=result.get('frames'), failure=result.get('failure'),
            folder=str(folder), manifest_sha256=sha(path) if m else None,
            source_policy_sha256=sha(policy), baseline_manifest_sha256=sha(parent_manifest))
        if discovered:
            assert m['ROM_sha256'] == digest and not m['fixed_replay']
            entry['unchanged_nonGrant_inputs_trace'] = {n: (folder / n).read_bytes() == (parent_manifest.parent / n).read_bytes()
                                                      for n in ('inputs.csv', 'trace.csv')}
            case_index = out / ('discover-index-' + key + '.json')
            case_index.write_text(json.dumps(dict(passed=True, phase='discover', ROM_sha256=digest,
                runs=[dict(identity=name, mode=mode, passed=True, folder=str(folder), manifest_sha256=sha(path))]), indent=2) + '\n')
            replay = out / ('replay-' + key + '-v1')
            entry['replay_exit'] = invoke('replay-' + key + '.log', [ROOT / 'tools/audit/replay_roster_pf.py',
                '--rom', a.rom.resolve(), '--discoveries', case_index, '--output', replay])
            entry['replay_batch'] = str(replay)
            if entry['replay_exit'] == 0:
                proof = json.loads((replay / 'proof.json').read_text())
                assert proof['passed'] and proof['complete'] and proof['ROM_sha256'] == digest and len(proof['runs']) == 1
                entry['strict_same_hash_replay_passed'] = True
                entry['replay_proof_sha256'] = sha(replay / 'proof.json')
                entry['passed'] = all(entry['unchanged_nonGrant_inputs_trace'].values())
        report['runs'].append(entry)
        (out / 'progress.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(dict(completed=len(report['runs']), total=len(selected), **entry)), flush=True)
    report['complete'] = True
    report['passed'] = all(row['passed'] for row in report['runs'])
    for name in ('progress.json', 'proof.json'):
        (out / name).write_text(json.dumps(report, indent=2) + '\n')
    return 0 if report['passed'] else 1


if __name__ == '__main__': main()
