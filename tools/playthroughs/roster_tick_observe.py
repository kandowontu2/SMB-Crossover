"""Read-only logical input extraction from a verified genuine branch prefix.

Fresh power-on replay must still match the endpoint and all10,240 RAM bytes.
No state is loaded or emulated memory/register/ROM written by this observer.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import run_mesen


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('proof', type=Path)
    p.add_argument('--basename', choices=('winning', 'best'), default='winning')
    p.add_argument('--tag', required=True)
    p.add_argument('--timeout', type=int, default=480)
    a = p.parse_args()
    proof = a.proof.resolve()
    manifest = json.loads((proof / 'manifest.json').read_text())
    verified = 'branch_coldboot_verified' if a.basename == 'winning' else 'best_coldboot_verified'
    assert manifest[verified] is True
    assert manifest['emulated_memory_or_register_patches'] is False
    rom = next(proof.glob('*.nes'))
    assert sha(rom) == manifest['rom_sha256']
    prefix = proof / (a.basename + '-inputs.csv')
    assert sha(prefix) == manifest[a.basename + '_inputs_sha256']
    out = ROOT / 'build/roster-through-2-2/tick-observations' / a.tag
    if out.exists() and any(out.iterdir()):
        raise FileExistsError('Choose a fresh observation tag')
    out.mkdir(parents=True, exist_ok=True)
    for suffix in ('-inputs.csv', '-target.lua', '-ram.bin'):
        shutil.copyfile(proof / (a.basename + suffix), out / (a.basename + suffix))
    observer = ROOT / 'tools/playthroughs/scrooge_observe_updates.lua'
    verifier = ROOT / 'tools/playthroughs/roster_branch_verify.lua'
    script = out / ('observe-' + a.tag + '.lua')
    script.write_text(
        'ROSTER_CONFIG={out=' + json.dumps(out.as_posix() + '/') + ',replay='
        + json.dumps((out / (a.basename + '-inputs.csv')).as_posix()) + '}\n'
        + 'dofile(' + json.dumps(observer.as_posix()) + ')\n'
        + 'BRANCH_VERIFY={out=' + json.dumps(out.as_posix() + '/') + ',basename='
        + json.dumps(a.basename) + '}\n'
        + 'dofile(' + json.dumps(verifier.as_posix()) + ')\n')
    code = run_mesen.run(script, rom, timeout=a.timeout, emulator_options=[
        '--nes.ramPowerOnState=AllZeros', '--nes.randomizeCpuPpuAlignment=false',
        '--nes.randomizeMapperPowerOnState=false'])
    check = out / ('coldboot-verified.json' if a.basename == 'winning' else 'best-coldboot-verified.json')
    assert code == 0 and json.loads(check.read_text())['ram_bytes_identical'] == 10240
    with (out / 'game-tick-actions.csv').open() as f:
        ticks = list(csv.DictReader(f))
    report = dict(verified_coldboot=True, emulated_writes=False, savestate_loads=False,
                  ram_bytes_identical=10240, proof=str(proof), basename=a.basename,
                  rom_sha256=sha(rom), inputs_sha256=sha(prefix),
                  observer_sha256=sha(observer), verifier_sha256=sha(verifier),
                  ticks_sha256=sha(out / 'game-tick-actions.csv'),
                  logical_ticks=len(ticks), last_tick_poll=int(ticks[-1]['poll']))
    (out / 'observation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(output=str(out), **report)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
