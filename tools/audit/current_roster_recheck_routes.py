"""Sequential fresh current-candidate controller-only roster qualification.

Private proposal evidence only. This does not qualify every item/source mechanic.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys

from check_tmnt_render_oa import load, address, location
from observe_chip_committed_write import lua

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text()) if path.exists() else {}


def stair_controller(body):
    return 'local base=(function()\n' + body + '''
end)()
local phase,held='approach',0
return function(c)
 local b=base(c)
 if c.world~=0 or c.level~=0 or c.x<2390 or c.x>=2512 then return b end
 if phase=='approach'and c.grounded then phase='hop';held=0 end
 if phase=='hop'then
  held=held+1
  b={right=c.x<2406,left=c.x>2420,a=held<=10}
  if held>10 and c.grounded and c.y<=112 then phase='runup';held=0 end
  return b
 elseif phase=='runup'then
  if c.grounded and c.x>=2424 and c.vx>0 and c.vx<128 then phase='cross';held=1;return{right=true,a=true}end
  return{right=true}
 elseif phase=='cross'then
  held=held+1;return{right=true,a=held<=40}
 end
 return b
end
'''


def trace_summary(folder):
    path = folder / 'trace.csv'
    if not path.exists():
        return {}
    rows = list(csv.DictReader(path.open()))
    active = [r for r in rows if r['world'] == r['level'] == '0'
              and r['engine'] == '8' and r['mode'] == '1' and r['task'] == '3']
    return dict(last_trace=rows[-12:], active_video_frames=len(active),
                active_nmiSkipped_values=sorted({int(r['nmiSkipped']) for r in active}),
                raw_video_bound_note='Completed-loop guard is authoritative; video rows may span interrupted game updates.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for n in ['rom', 'archive', 'output']:
        p.add_argument('--' + n, type=Path, required=True)
    p.add_argument('--cases', nargs='+', help='identity:mode; default all aggregate recorded cases')
    p.add_argument('--replay', action='store_true', help='Immediately independently replay each passing discovery')
    p.add_argument('--frames', type=int, default=18000)
    a = p.parse_args()
    rom, d, out = a.rom.resolve(), a.archive.resolve(), a.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(exist_ok=False)
    bundle = load(rom)
    digest = sha(rom)
    aggregate_path = d / 'native-probes-qa-v2/full-roster-aggregate-v1/proof.json'
    aggregate = read_json(aggregate_path)
    driver = d / 'mmc3-ship-lives-v25/native-routes-v1/bound-mmc3-runner.py'
    original_guard = d / 'mmc3-static-call-v37/full-roster-v1/native-guard.lua'
    names = ['OperMode', 'OperMode_Task', 'GameEngineSubroutine', 'WorldNumber',
             'LevelNumber', 'Player_X_Position', 'Player_PageLoc', 'Player_Y_Position',
             'ScreenLeft_X_Pos', 'ScreenLeft_PageLoc']
    delta = int(bundle['syms']['GameLoop']['size'], 0) - 1
    offset = location(bundle, 'GameLoop') + delta
    assert bundle['raw'][offset] == 0x60
    hook = dict(address=address(bundle, 'GameLoop') + delta,
                physical_bank=(offset - 16) // 8192,
                bytes=list(bundle['raw'][offset:offset + 8]))
    guard = out / 'native-guard.lua'
    guard.write_text('OUTPUT=ROSTER_CONFIG.out\nMOTION_RAM=' + lua({n: address(bundle, n) for n in names})
                     + '\nMOTION_HOOK=' + lua(hook) + '\nlocal checks,maxWorld,maxCamera='
                     + original_guard.read_text().split('local checks,maxWorld,maxCamera=', 1)[1])
    cases = [tuple(x.split(':')) for x in a.cases] if a.cases else [(r['identity'], r['mode']) for r in aggregate['runs']]
    report = dict(passed=False, complete=False, goal_complete=False,
                  private_proposal=True, ROM_sha256=digest, rom=str(rom),
                  driver_sha256=sha(driver), runner_sha256=sha(Path(__file__)),
                  aggregate_sha256=sha(aggregate_path), guard_sha256=sha(guard), runs=[],
                  scope='Fresh controller-only native1-1; one Mesen worker. Frozen qualified controllers, actual symbol rebinding recorded, native completed-loop world<=8/camera0..4 and actual body CHR. ZeldaII uses retained top-step controller. Failed attempts retained. Discovery requires separate PPU replay; not every item, source fidelity, lag or final release certification.')
    for name, mode in cases:
        assert mode in ['easy', 'hard']
        matches = [r for r in aggregate['runs'] if r['identity'] == name]
        row = next((r for r in matches if r['mode'] == mode), matches[0])
        source = Path(row['discovery']).parent / 'policy.lua'
        body = source.read_text()
        if body.startswith('dofile('):
            body = body.split('\n', 1)[1]
        bindings = []
        def bind(match):
            symbol, old = match[1], int(match[2])
            if symbol not in bundle['syms']:
                return match[0]
            actual = address(bundle, symbol)
            bindings.append(dict(symbol=symbol, old=old, actual=actual))
            return 'L.' + symbol + '=' + str(actual)
        body = re.sub(r'^L\.(\w+)=(\d+)\s*$', bind, body, flags=re.M)
        if name == 'zelda2':
            body = stair_controller(body)
        policy = out / (name + '-' + mode + '-policy.lua')
        policy.write_text('dofile(' + lua(guard.as_posix()) + ')\n' + body)
        folder = out / (name + '-' + mode)
        command = [sys.executable, str(driver), name, '--rom', str(rom), '--output', str(folder),
                   '--mapper', 'mmc5', '--behavior', mode, '--frames', str(a.frames),
                   '--capture', '12', '--policy', str(policy), '--chr-commit', '--timeout', '240']
        with (out / (name + '-' + mode + '-host.log')).open('w') as log:
            result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        manifest = read_json(folder / 'manifest.json')
        motion = read_json(folder / 'completed-loop-motion.json')
        native = manifest.get('result') or {}
        passed = bool(result.returncode == 0 and native.get('cleared') and native.get('deaths') == 0
                      and motion.get('passed') and manifest.get('chr_commit', {}).get('passed'))
        entry = dict(identity=name, mode=mode, source_mode=row['mode'], passed=passed,
                     source_policy=str(source), source_policy_sha256=sha(source),
                     actual_symbol_bindings=bindings, policy_sha256=sha(policy),
                     folder=str(folder), exit=result.returncode, result=native, motion=motion,
                     chr_commit=manifest.get('chr_commit'), trace_summary=trace_summary(folder), replay=None)
        report['runs'].append(entry)
        (out / 'progress.json').write_text(json.dumps(report, indent=2))
        print(json.dumps({k: v for k, v in entry.items() if k != 'trace_summary'}), flush=True)
        if a.replay and passed:
            replay = out / (name + '-' + mode + '-direct')
            with (out / (name + '-' + mode + '-replay-host.log')).open('w') as log:
                result = subprocess.run([sys.executable, str(d / 'streaming-replay-v1/capture.py'),
                                         '--rom', str(rom), '--route', str(folder), '--output', str(replay)],
                                        cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
            proof = read_json(replay / 'proof.json')
            entry['replay'] = dict(folder=str(replay), exit=result.returncode, passed=proof.get('passed', False),
                                   physical_frames=proof.get('direct_frames'), proof_sha256=sha(replay / 'proof.json') if proof else None)
            (out / 'progress.json').write_text(json.dumps(report, indent=2))
            print(json.dumps(dict(identity=name, mode=mode, replay=entry['replay'])), flush=True)
    report.update(complete=True, passed=all(r['passed'] and (not a.replay or r['replay']['passed']) for r in report['runs']))
    (out / 'proof.json').write_text(json.dumps(report, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
