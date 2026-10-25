"""Bounded TAS discovery from genuine controller-attained, unedited save states.

The winning ordinary inputs still require a fresh power-on replay. This runner
does not patch emulated RAM, ROM, registers or serialized state contents.
"""
from pathlib import Path
import argparse
import hashlib
import gzip
import json
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import run_mesen
from workspace_storage import CAP_BYTES, locate
from roster_run import workspace_bytes
from roster_branch_root import bind_root, validate_root


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--prefix', type=Path, required=True)
    p.add_argument('--root-poll', type=int, required=True)
    p.add_argument('--root-proof', type=Path,
                   help='Optional independently verified opaque discovery root directory')
    p.add_argument('--root-proof-basename', choices=('winning', 'best'), default='winning')
    p.add_argument('--goal-x', type=int, required=True)
    p.add_argument('--goal-y-min', type=int, default=0,
                   help='Minimum canonical player Y at goal, excluding roof routes when needed')
    p.add_argument('--goal-y-max', type=int, default=208)
    p.add_argument('--goal-power-min', type=int, choices=(0, 1, 2), default=0,
                   help='Require an ordinary collected power-up at the physical landing goal')
    p.add_argument('--tag', required=True)
    p.add_argument('--width', type=int, default=4)
    p.add_argument('--depth', type=int, default=18)
    p.add_argument('--chunk', type=int, default=32)
    p.add_argument('--timeout', type=int, default=180)
    p.add_argument('--air-goal', action='store_true')
    p.add_argument('--actions', help='Comma-separated subset of controller actions; default retains all actions')
    p.add_argument('--spatial-limit', type=int, default=0,
                   help='Optional max alternatives per 24-pixel X/Y/movement cell, retaining wider timing choices')
    p.add_argument('--score-mode', choices=('forward','landing'), default='forward',
                   help='Prefer the physical landing height when the obstacle requires gaining height before moving right')
    a = p.parse_args()
    if workspace_bytes(ROOT) + 150_000_000 > CAP_BYTES:
        raise RuntimeError('Archive older evidence before another branch search under the 30 GB cap')
    a.rom = locate(a.rom)
    a.prefix = locate(a.prefix)
    if a.root_proof:
        a.root_proof = locate(a.root_proof)
    assert a.root_poll > 500 and 1 <= a.width <= 12 and 1 <= a.depth <= 80
    assert 8 <= a.chunk <= 64
    assert 0 <= a.goal_y_min <= a.goal_y_max <= 255
    assert 0 <= a.spatial_limit <= 4
    if a.actions:
        selected_actions = a.actions.split(',')
        allowed_actions = {'R', 'RA', 'R-A8', 'R-AOFF8', 'RB', 'RAB', 'L', 'A', 'LA', 'AB', 'B', 'WAIT',
                           'DB', 'RDB', 'ADB', 'DA', 'RDA', 'LDA', 'U', 'RU', 'RUA', 'UA',
                           'UB', 'RUB', 'UAB', 'RUAB', 'LB', 'LAB',
                           'S', 'RS', 'US', 'RUS', 'AS'}
        assert len(selected_actions) == len(set(selected_actions)), 'Actions must be unique'
        assert all(v in allowed_actions for v in selected_actions), 'Unknown controller action'
    root_metadata = None
    if a.root_proof:
        root_metadata = validate_root(a.root_proof, a.root_proof_basename,
                                      a.rom, a.prefix, a.root_poll)
    out = ROOT / 'build/roster-through-2-2/search' / a.tag
    if out.exists() and any(out.iterdir()):
        raise FileExistsError(f'Output tag already has evidence; choose a fresh tag: {out}')
    out.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(Path(__file__),out/'driver.py')
    rom = out / a.rom.name
    for extension in ('.nes', '.lbl'):
        shutil.copyfile(a.rom.with_suffix(extension), rom.with_suffix(extension))
    debug = a.rom.with_suffix('.dbg')
    raw_debug = debug.read_bytes() if debug.exists() else gzip.decompress(a.rom.with_suffix('.dbg.gz').read_bytes())
    rom.with_suffix('.dbg.gz').write_bytes(gzip.compress(raw_debug, mtime=0))
    prefix = out / 'prefix.csv'
    lines = a.prefix.read_text().splitlines()
    # The next real GameLoop may occur after another input poll. Retain the
    # genuine source tail until the callback can take the opaque root state;
    # exported branches still contain only polls actually consumed by then.
    kept = [line for line in lines if line.startswith('poll,') or
            line.split(',')[0].isdigit()]
    assert any(line.split(',')[0] == str(a.root_poll) for line in kept), 'Prefix does not contain the requested root poll'
    if root_metadata:
        assert hashlib.sha256(rom.read_bytes()).hexdigest() == root_metadata['rom_sha256']
        prefix.write_bytes(a.prefix.read_bytes())
    else:
        prefix.write_text('\n'.join(kept) + '\n')
    config = dict(out=out.as_posix()+'/', prefix=prefix.as_posix(),
                  rootPoll=a.root_poll, goalX=a.goal_x, goalYMin=a.goal_y_min, goalYMax=a.goal_y_max,
                  goalPowerMin=a.goal_power_min,
                  width=a.width, depth=a.depth, chunk=a.chunk, airGoal=a.air_goal,
                  actions=a.actions or '', spatialLimit=a.spatial_limit, scoreMode=a.score_mode)
    if root_metadata:
        state = out / 'proof-root.state'
        ram = out / 'proof-root-ram.bin'
        shutil.copyfile(a.root_proof / (a.root_proof_basename + '-verified-root.state'), state)
        shutil.copyfile(a.root_proof / (a.root_proof_basename + '-ram.bin'), ram)
        assert hashlib.sha256(state.read_bytes()).hexdigest() == root_metadata['state_sha256']
        assert hashlib.sha256(ram.read_bytes()).hexdigest() == root_metadata['ram_sha256']
        config.update(rootState=state.as_posix(), rootRam=ram.as_posix(),
                      rootFrame=root_metadata['frame'])
    script = out / f'search-{out.name}.lua'
    core = out / 'search-core.lua'
    verify_core = out / 'verify-core.lua'
    shutil.copyfile(ROOT/'tools/playthroughs/roster_branch_search.lua', core)
    shutil.copyfile(ROOT/'tools/playthroughs/roster_branch_verify.lua', verify_core)
    source=core.read_text()
    old="elseif action=='B'then mask=fire and 64 or 0 end"
    assert source.count(old)==1
    source=source.replace(old,"""elseif action=='S'then mask=32
  elseif action=='RS'then mask=33
  elseif action=='US'then mask=40
  elseif action=='RUS'then mask=41
  elseif action=='AS'then mask=160
  elseif action=='B'then mask=fire and 64 or 0 end""")
    core.write_text(source)
    data = 'SEARCH={' + ','.join(k+'='+('true' if v is True else 'false' if v is False
                                      else str(v) if isinstance(v, int) else json.dumps(v))
                               for k, v in config.items()) + '}\n'
    script.write_text(data+'dofile('+json.dumps(core.as_posix())+')\n')
    manifest = dict(driver_sha256=hashlib.sha256((out/'driver.py').read_bytes()).hexdigest(),
                    debug_sha256=hashlib.sha256(raw_debug).hexdigest(),
                    compressed_debug_sha256=hashlib.sha256(rom.with_suffix('.dbg.gz').read_bytes()).hexdigest(),
                    search_source_sha256=hashlib.sha256(core.read_bytes()).hexdigest(),
                    verify_source_sha256=hashlib.sha256(verify_core.read_bytes()).hexdigest(),
                    rom_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),
                    prefix_sha256=hashlib.sha256(prefix.read_bytes()).hexdigest(),
                    config=config, discovery_uses_unedited_binary_savestates=True,
                    emulated_memory_or_register_patches=False,
                    reused_independent_root=root_metadata,
                    reused_root_proof=a.root_proof.resolve().as_posix() if a.root_proof else None,
                    branch_coldboot_verified=False)
    (out/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    options = [
        '--nes.ramPowerOnState=AllZeros', '--nes.randomizeCpuPpuAlignment=false',
        '--nes.randomizeMapperPowerOnState=false']
    result = run_mesen.run(script, rom, timeout=a.timeout, emulator_options=options)
    search_log = ROOT/'build/verification'/f'{rom.stem}-{script.stem}.log'
    if search_log.exists():
        shutil.copyfile(search_log, out/'search-native.log')
    basename = 'winning' if result == 0 and (out/'winning-inputs.csv').exists() else 'best'
    if (out/(basename+'-inputs.csv')).exists():
        verify = out/(basename+'-coldboot-verify-'+out.name+'.lua')
        verify.write_text('BRANCH_VERIFY={out='+json.dumps(out.as_posix()+'/')+',basename='+json.dumps(basename)+',exportRoot=true}\n'+
                          'dofile('+json.dumps(verify_core.as_posix())+')\n')
        verified = run_mesen.run(verify, rom, timeout=a.timeout, emulator_options=options) == 0
        verify_log = ROOT/'build/verification'/f'{rom.stem}-{verify.stem}.log'
        if verify_log.exists():
            shutil.copyfile(verify_log, out/(basename+'-verify-native.log'))
        manifest['branch_coldboot_verified' if basename == 'winning' else 'best_coldboot_verified'] = verified
        manifest[basename+'_inputs_sha256'] = hashlib.sha256((out/(basename+'-inputs.csv')).read_bytes()).hexdigest()
        if verified:
            manifest[basename+'_reusable_root'] = bind_root(out, basename, rom, verify_core)
        (out/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
        if basename == 'winning' and not verified:
            result = 1
    return result


if __name__ == '__main__':
    raise SystemExit(main())
