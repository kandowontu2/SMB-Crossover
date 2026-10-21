"""Discover ordinary controller retiming from independently observed logic ticks.

New output is a discovery candidate until a separate complete fixed-input replay.
Missed logic edges and multiple-update poll gaps are logged, never RAM-patched.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('observation', type=Path)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--character', type=int, required=True, choices=range(13))
    p.add_argument('--variant', type=int, default=0, choices=(0, 1))
    p.add_argument('--mapper', choices=('mmc3', 'mmc5'), default='mmc3')
    p.add_argument('--tag', required=True)
    p.add_argument('--tail-policy', type=Path)
    p.add_argument('--completed-loop-clock', action='store_true',
                   help='Hold each tick input until foreground GameLoop finishes; discovery only')
    p.add_argument('--frames', type=int, default=30000)
    p.add_argument('--timeout', type=int, default=480)
    a = p.parse_args()
    source = a.observation.resolve()
    report = json.loads((source / 'observation.json').read_text())
    assert report['verified_coldboot'] and report['ram_bytes_identical'] == 10240
    assert report['emulated_writes'] is False and report['savestate_loads'] is False
    ticks = source / 'game-tick-actions.csv'
    assert sha(ticks) == report['ticks_sha256']
    config = ROOT / 'build/roster-through-2-2/tick-policies' / a.tag
    if config.exists() and any(config.iterdir()):
        raise FileExistsError('Choose a fresh retiming tag')
    config.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ticks, config / ticks.name)
    shutil.copyfile(ROOT / 'tools/playthroughs/scrooge_retime_updates.lua', config / 'core.lua')
    lines = ['ROSTER_TICK_REFERENCE=' + json.dumps((config / ticks.name).as_posix()),
             'ROSTER_TICK_MIN_POLL=' + str(report['last_tick_poll'])]
    if a.completed_loop_clock:
        lines.append('ROSTER_TICK_COMPLETE_CLOCK=true')
    if a.tail_policy:
        lines.append('ROSTER_TICK_TAIL_POLICY=' + json.dumps(a.tail_policy.resolve().as_posix()))
    lines.append('return dofile(' + json.dumps((config / 'core.lua').as_posix()) + ')')
    policy = config / 'policy.lua'
    policy.write_text('\n'.join(lines) + '\n')
    (config / 'reference.json').write_text(json.dumps(report, indent=2) + '\n')
    return subprocess.call([sys.executable, str(ROOT / 'tools/playthroughs/roster_run.py'),
                            '--rom', str(a.rom.resolve()), '--character', str(a.character),
                            '--variant', str(a.variant), '--mapper', a.mapper, '--tag', a.tag,
                            '--policy', str(policy), '--frames', str(a.frames),
                            '--timeout', str(a.timeout), '--discovery-fast'], cwd=ROOT)


if __name__ == '__main__':
    raise SystemExit(main())
