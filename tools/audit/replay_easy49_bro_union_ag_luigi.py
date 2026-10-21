"""Ordinary Luigi timing control on AB, with exact fixed power-on inputs."""
from pathlib import Path
import csv, hashlib, json, subprocess, sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-easy-bro-union-ab'
Y = R / 'build/roster-through-2-2'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert sha(H / 'report.json') == '68567961c9ec02603c055aff83ff89185427361d5f84f313d9c755aabcb3b4ee'
    build = json.loads((H / 'report.json').read_text())
    assert all(sha(H / 'source' / n) == h for n, h in build['source_hashes'].items())
    out = H / 'ordinary-luigi-ag';out.mkdir(parents=True, exist_ok=False)
    fixed = Y / 'root49s2-luigi-final-a-8-v0-mmc3/inputs.csv'
    assert sha(fixed) == 'df3ba1b6996c9ccde0d355328a47793f353ea87e9d30ce154f6f077a0c94ec1b'
    keys = ['frame', 'poll', 'world', 'level', 'area', 'areaType', 'x', 'y', 'yHigh', 'state', 'vx', 'vy',
            'power', 'engine', 'mode', 'task', 'lives', 'camera', 'buttons']
    report = dict(status='RUNNING_ORDINARY_AB_LUIGI_FIXED_BOTH_MAPPERS', rows=[], script_sha256=sha(__file__),
                  build_sha256=sha(H / 'report.json'), inputs_sha256=sha(fixed), recorded=False,
                  final_integrated_recordings_required=True, accepted_release=False, goal_complete=False)
    def save():
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    save()
    for mapper in ['mmc3', 'mmc5']:
        parent = Y / ('specialist-y-luigi-easy-fixed-a-8-v0-' + mapper)
        policy = parent / 'policy.lua'
        log = out / (mapper + '-native.log')
        argv = [sys.executable, str(R / 'tools/playthroughs/roster_run.py'), '--character', '8', '--mapper', mapper,
                '--rom', str(H / 'source/build' / ('smb-crossover-' + mapper + '.nes')), '--tag', 'root49ab-luigi-fixed-ag',
                '--policy', str(policy), '--replay', str(fixed), '--frames', '18000', '--timeout', '300', '--workspace-cap-gb', '50']
        with log.open('wb') as f:
            rc = subprocess.run(argv, cwd=R, stdout=f, stderr=subprocess.STDOUT).returncode
        folder = Y / ('root49ab-luigi-fixed-ag-8-v0-' + mapper)
        manifest = json.loads((folder / 'manifest.json').read_text())
        before = list(csv.DictReader((parent / 'trace.csv').open()))
        after = list(csv.DictReader((folder / 'trace.csv').open()))
        diffs = [dict(frame=b['frame'], fields=[k for k in keys if a[k] != b[k]])
                 for a, b in zip(before, after) if any(a[k] != b[k] for k in keys)]
        guard = 'ORDINARY LUIGI title verified: mode=0 selected=8' in log.read_text()
        stages, lag = {}, 0
        for x in csv.DictReader((folder / 'render.csv').open()):
            assert int(x['behaviorVersion']) == 0
            stage = x['world'] + '-' + x['level']
            p = stages.setdefault(stage, dict(frames=0, flagged_lag_frames=0, max_oam_sprites=0))
            p['frames'] += 1
            p['flagged_lag_frames'] += int(int(x['lagNmi']) != 0)
            p['max_oam_sprites'] = max(p['max_oam_sprites'], int(x['maxSprites']))
            lag += int(int(x['lagNmi']) != 0)
        passed = bool(rc == 0 and manifest.get('verified_through_2_2') and manifest.get('full_frame_audit')
                      and manifest.get('controller_only') and not manifest.get('memory_or_register_writes')
                      and manifest.get('inputs_sha256') == sha(fixed) and guard
                      and len(before) == len(after) == 17412 and not diffs
                      and manifest['result']['deaths'] == 0 and manifest['result']['all_six_stages'])
        report['rows'].append(dict(mapper=mapper, exit=rc, passed=passed, result=manifest.get('result'),
                                   title_mode_and_character_guard=guard, compared_fields=keys, first_differences=diffs[:10],
                                   parent_trace_rows=len(before), actual_trace_rows=len(after), profiles=stages,
                                   flagged_lag_frames=lag, manifest_sha256=sha(folder / 'manifest.json'),
                                   log_sha256=sha(log), route_path=folder.relative_to(R).as_posix()))
        save();print(mapper, rc, passed, manifest.get('result'), flush=True)
    assert all(sha(H / 'source' / n) == h for n, h in build['source_hashes'].items())
    report['status'] = 'PASS_AB_ORDINARY_LUIGI_BOTH_MAPPERS_EXACT_Y_TRAJECTORY' if all(x['passed'] for x in report['rows']) else 'RETAINED_AB_LUIGI_DIFFERENCES'
    save();print(report['status'], sha(out / 'report.json'), flush=True)
    return 0 if all(x['passed'] for x in report['rows']) else 1


if __name__ == '__main__':
    raise SystemExit(main())
