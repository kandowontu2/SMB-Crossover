"""Retain the Scrooge route negative and isolate BE from its AP parent."""
from pathlib import Path
import csv, hashlib, json, shutil, subprocess, sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
P = V / 'root49-easy-advanced-union-ap'
H = V / 'root49-easy-pit-empty-be'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = H / 'ordinary-scrooge-control-bk'
    out.mkdir(exist_ok=False)
    before = H / 'ordinary-scrooge-bj/report.json'
    assert sha(before) == '8352fead73931c5db0465f85ff9a21890910f8542d85e75a6e40a779644755f2'
    assert sha(P / 'report.json') == 'e1215e073905879a580fea13dfe55dad26d9fe11a0595bbe7fbfdf915a822b6e'
    parent = json.loads((P / 'report.json').read_text())
    assert all(sha(P / 'source' / n) == h for n, h in parent['source_hashes'].items())
    control = json.loads(before.read_text())
    policy = H / 'ordinary-scrooge-bj/policy.lua'
    assert sha(policy) == control['policy_sha256']
    report = dict(status='RUNNING_AP_BE_FOREIGN_SCROOGE_CONTROL', script_sha256=sha(__file__),
                  BE_negative_sha256=sha(before), AP_build_sha256=sha(P / 'report.json'), rows=[],
                  controller_only=True, emulated_changes=False, recorded=False,
                  qualification='This comparison diagnoses a failed old route transfer. A matching failure does not certify a complete route or every Scrooge ability.',
                  accepted_release=False, goal_complete=False)
    def save():
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    save()
    keys = ['frame', 'poll', 'world', 'level', 'area', 'areaType', 'x', 'y', 'yHigh', 'state',
            'vx', 'vy', 'power', 'engine', 'mode', 'task', 'lives', 'camera', 'buttons']
    for candidate in control['rows']:
        mapper = candidate['mapper']
        evidence = R / candidate['output']
        manifest = json.loads((evidence / 'manifest.json').read_text())
        replay = Path(manifest['config']['replay'])
        assert sha(replay) == candidate['inputs_sha256']
        rom = P / 'source/build' / ('smb-crossover-' + mapper + '.nes')
        tag = 'root49bk-scrooge-ap-control'
        argv = [sys.executable, str(R / 'tools/playthroughs/roster_run.py'), '--character', '12',
                '--mapper', mapper, '--rom', str(rom), '--tag', tag, '--replay', str(replay),
                '--policy', str(policy), '--frames', '36000', '--timeout', '360', '--workspace-cap-gb', '50']
        with (out / (mapper + '-host.log')).open('wb') as stream:
            rc = subprocess.run(argv, cwd=R, stdout=stream, stderr=subprocess.STDOUT).returncode
        folder = R / 'build/roster-through-2-2' / (tag + '-12-v0-' + mapper)
        native_source = V / (rom.stem + '-run-' + tag + '-12-v0-' + mapper + '.log')
        native = out / (mapper + '-native.log')
        if native_source.exists():
            shutil.copyfile(native_source, native)
        path = folder / 'manifest.json'
        actual = json.loads(path.read_text()) if path.exists() else None
        a = list(csv.DictReader((folder / 'trace.csv').open())) if (folder / 'trace.csv').exists() else []
        b = list(csv.DictReader((evidence / 'trace.csv').open()))
        diff = [i + 1 for i, (x, y) in enumerate(zip(a, b)) if any(x[k] != y[k] for k in keys)]
        identity = bool(native.exists() and 'ORDINARY SCROOGE title verified: mode=0 selected=12 shadows=0' in native.read_text())
        good = bool(actual and actual['result'] == candidate['result'] and len(a) == len(b) and not diff and identity
                    and rc == candidate['exit'] and actual['replay_sha256'] == candidate['inputs_sha256'])
        receipts = {}
        for name in ['inputs.csv', 'events.csv', 'audio-events.csv', 'chr.csv', 'oam.csv',
                     'render.csv', 'scroll-writes.csv', 'stomp-events.csv']:
            x, y = folder / name, evidence / name
            receipts[name] = dict(AP_sha256=sha(x), BE_sha256=sha(y), byte_exact=sha(x) == sha(y)) if x.exists() and y.exists() else None
        row = dict(mapper=mapper, exit=rc, passed=good, output=folder.relative_to(R).as_posix(),
                   result=actual['result'] if actual else None, fields=keys,
                   AP_frames=len(a), BE_frames=len(b), differing_frames=diff,
                   identity_guard_observed=identity, manifest_sha256=sha(path) if path.exists() else None,
                   native_log_sha256=sha(native) if native.exists() else None, receipts=receipts)
        report['rows'].append(row)
        save()
        print(mapper, good, row['result'], 'differing_frames', len(diff), flush=True)
    assert all(sha(P / 'source' / n) == h for n, h in parent['source_hashes'].items())
    good = len(report['rows']) == 2 and all(row['passed'] for row in report['rows'])
    report['status'] = 'PASS_AP_BE_SCROOGE_NEGATIVE_TRANSFER_ISOLATION' if good else 'RETAINED_AP_BE_SCROOGE_DIFFERENCE'
    save()
    print(report['status'], sha(out / 'report.json'), flush=True)
    return 0 if good else 1


if __name__ == '__main__':
    raise SystemExit(main())
