"""Fresh controller-only Chip/Dale routes with unchanged movement guards."""
from pathlib import Path
import argparse
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


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidates', type=Path, required=True)
    p.add_argument('--archive', type=Path, required=True)
    p.add_argument('--mapper', choices=['mmc3', 'mmc5'], required=True)
    p.add_argument('--name', default='native-routes-v1')
    p.add_argument('--bind-policy-symbols', action='store_true',
                   help='Replace frozen numeric L aliases with actual linked symbols; record each binding')
    p.add_argument('--chip-hard-dale-policy', action='store_true',
                   help='Use the existing Dale Hard controller for the same Chip gameplay family')
    args = p.parse_args()
    d, mapper = args.archive.resolve(), args.mapper
    v = d / 'mmc3-static-call-v37'
    rom = args.candidates.resolve() / mapper / 'candidate.nes'
    folder = rom.parent / args.name
    folder.mkdir(exist_ok=False)
    driver = d / 'mmc3-ship-lives-v25/native-routes-v1/bound-mmc3-runner.py'
    original_guard = (v / 'full-roster-v1/native-guard.lua').read_text()
    b = load(rom)
    if mapper == 'mmc3':
        guard = original_guard
    else:
        names = ['OperMode', 'OperMode_Task', 'GameEngineSubroutine', 'WorldNumber',
                 'LevelNumber', 'Player_X_Position', 'Player_PageLoc',
                 'Player_Y_Position', 'ScreenLeft_X_Pos', 'ScreenLeft_PageLoc']
        size = int(b['syms']['GameLoop']['size'], 0)
        pc = address(b, 'GameLoop') + size - 1
        pos = location(b, 'GameLoop') + size - 1
        assert b['raw'][pos] == 0x60
        hook = dict(address=pc, physical_bank=(pos-16)//8192,
                    bytes=list(b['raw'][pos:pos+8]))
        guard = ('MOTION_RAM=' + lua({n: address(b, n) for n in names}) + '\n'
                 + 'MOTION_HOOK=' + lua(hook) + '\n'
                 + original_guard[original_guard.index('local checks,maxWorld,maxCamera='):])
    guard_path = folder / 'native-guard.lua'
    guard_path.write_text('OUTPUT=ROSTER_CONFIG.out\n' + guard)
    report = dict(passed=False, complete=False, goal_complete=False, ROM_sha256=sha(rom),
                  driver_sha256=sha(driver), native_guard_sha256=sha(guard_path), runs=[],
                  scope='Fresh ordinary-controller1-1 routes for Chip and Dale in Easy/Hard. Original failed routes retained. Unchanged world<=8/camera0..4 completed-loop bounds; MMC3 additionally retains full tiny-code/stack/NMI/bank/cache guards. MMC5 additionally observes committed CHR. Native screenshots sampled separately; independent PPU replays and other powerup/passive cases are separate.')
    for name, source_mode in [('chip', 'easy'), ('dale', 'hard')]:
        original = v / 'full-roster-v1' / (name + '-' + source_mode) / 'policy.lua'
        text = original.read_text()
        first, body = text.split('\n', 1)
        assert first.startswith('dofile(') and first.endswith(')')
        for mode in ['easy', 'hard']:
            used_original = original
            used_body = body
            if name == 'chip' and mode == 'hard' and args.chip_hard_dale_policy:
                used_original = v / 'full-roster-v1/dale-hard/policy.lua'
                used_body = used_original.read_text().split('\n', 1)[1]
            bindings = []
            if args.bind_policy_symbols:
                def bind(match):
                    symbol, old = match.group(1), int(match.group(2))
                    if symbol not in b['syms']:
                        assert not symbol.startswith('Cd'), symbol
                        return match.group(0)
                    linked = address(b, symbol)
                    bindings.append(dict(symbol=symbol, old=old, actual=linked))
                    return 'L.' + symbol + '=' + str(linked)
                used_body = re.sub(r'^L\.(\w+)=(\d+)\s*$', bind, used_body, flags=re.M)
            policy = folder / (name + '-' + mode + '-policy.lua')
            policy.write_text('dofile(' + lua(guard_path.as_posix()) + ')\n' + used_body)
            out = folder / (name + '-' + mode)
            command = [sys.executable, str(driver), name, '--rom', str(rom),
                       '--output', str(out), '--mapper', mapper, '--behavior', mode,
                       '--frames', '16000', '--capture', '12', '--policy', str(policy),
                       '--timeout', '240']
            if mapper == 'mmc5':
                command.append('--chr-commit')
            with (folder / (name + '-' + mode + '-host.log')).open('w') as log:
                result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
            manifest = json.loads((out / 'manifest.json').read_text())
            motion = json.loads((out / 'completed-loop-motion.json').read_text()) if (out / 'completed-loop-motion.json').exists() else {}
            native = manifest.get('result') or {}
            guards = {}
            for n in ['full-smc-guard', 'mmc3-cache-guard'] if mapper == 'mmc3' else ['chr-commit']:
                q = out / (n + '.json')
                guards[n] = json.loads(q.read_text()) if q.exists() else dict(passed=False)
            row = dict(identity=name, mode=mode, folder=str(out), exit=result.returncode,
                       passed=bool(result.returncode == 0 and native.get('cleared')
                                   and native.get('deaths') == 0 and motion.get('passed')
                                   and all(q.get('passed') for q in guards.values())),
                       result=native, motion=motion, guards=guards,
                       manifest_sha256=sha(out / 'manifest.json'),
                       original_policy_sha256=sha(used_original), policy_sha256=sha(policy),
                       actual_symbol_bindings=bindings)
            report['runs'].append(row)
            (folder / 'progress.json').write_text(json.dumps(report, indent=2))
            print(json.dumps(row), flush=True)
    report.update(complete=True, passed=all(row['passed'] for row in report['runs']))
    (folder / 'proof.json').write_text(json.dumps(report, indent=2))
    raise SystemExit(0 if report['passed'] else 1)


if __name__ == '__main__':
    main()
