"""Prepare ONE genuine MarioEasy later-flower/fireball component; never launch Mesen."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys

from check_tmnt_render_oa import address, load, location
from observe_chip_committed_write import lua

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
SHA = '900b669e212b878041c23e438f2fb26e310ce8f929f904681a9c4b17405b6968'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(p, z):
    p.write_text(json.dumps(z, indent=2) + '\n', encoding='utf-8')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(parents=True, exist_ok=False)
    source = D / 'current3cee-postdma-mask-v1/canonical-v2'
    rom = source / 'candidate.nes'
    assert sha(rom) == SHA
    b = load(rom)
    parent = D / 'mario-powerups900-first-v2/mario-easy'
    assert json.loads((parent / 'native-receipt.json').read_text())['passed']
    original = D / 'current3cee-remaining27-routes-v1/native/mario-easy'
    env_path = D / 'parodius-menu3cee-ready-v1/environment.json'
    env = json.loads(env_path.read_text())
    for n in ['emulator', 'core', 'worker_settings', 'user_settings']:
        assert sha(env[n]) == env[n + '_sha256'], n
    folder = out / 'mario-easy'
    folder.mkdir()
    (folder / 'frames').mkdir()
    module = ROOT / 'tools/audit/mario_flower900_native_v1.lua'
    text = module.read_text()
    hooks = {n: dict(address=address(b, n), bank=(location(b, n) - 16) // 8192,
                     bytes=list(b['raw'][location(b, n):location(b, n) + 3]))
             for n in ['PwrUpJmp', 'MarioSourcePowerupCollision', 'MarioSourcePowerupUpdate',
                       'MarioSourceFireballBrick', 'HandleEnemyFBallCol']}
    used = set(re.findall(r"\br\('([A-Za-z_][A-Za-z_0-9]*)'", text))
    used |= {'Square2SoundQueue', 'Square1SoundQueue', 'Fireball_State'}
    cfg = dict(json.loads((parent / 'configuration.json').read_text())['roster'])
    cfg.update(out=folder.as_posix() + '/', policy=(folder / 'policy.lua').as_posix(),
               audit=(folder / 'audit.lua').as_posix(), limit=6500, capture=8)
    c = dict(character=0, variant=0, mode=0, ROM_sha256=SHA, blocks=[336, 1248],
             hooks=hooks, ram={n: address(b, n) for n in used},
             sfx={k: address(b, v) for k, v in [('reveal', 'Sfx_GrowPowerUp'),
                    ('pickup', 'Sfx_PowerUpGrab'), ('fire', 'Sfx_Fireball')]})
    put(folder / 'configuration.json', dict(roster=cfg, item=c))
    body = (original / 'policy.lua').read_text().split('\n', 1)[1]
    guard = original.parent / 'native-guard.lua'
    policy = ('dofile(' + lua(guard.as_posix()) + ')\nlocal base=(function()\n' + body +
              '\nend)()\nreturn function(c)return MARIO_FLOWER_CONTROL(c,base)end\n')
    (folder / 'policy.lua').write_text(policy, encoding='utf-8', newline='\n')
    harness = (parent / 'harness.lua').read_text().replace('MARIO_POWERUP_FINISH', 'MARIO_FLOWER_FINISH').replace('MARIO_POWERUP_DONE', 'MARIO_FLOWER_DONE')
    (folder / 'harness.lua').write_text(harness, encoding='utf-8', newline='\n')
    shutil.copyfile(parent / 'audit.lua', folder / 'audit.lua')
    script = ('ROSTER_CONFIG=' + lua(cfg) + '\nMARIO_FLOWER_CONFIG=' + lua(c) +
              '\ndofile(' + lua(module.as_posix()) + ')\ndofile(' +
              lua((folder / 'harness.lua').as_posix()) + ')\nassert(MARIO_POWERUP_INSTALL_CHR_DISPATCHER)()\n')
    (folder / 'run.lua').write_text(script, encoding='utf-8', newline='\n')
    all_text = text + policy + harness + (folder / 'audit.lua').read_text() + script
    assert not re.search(r'\bemu\.(?:write\w*|setState|loadSavestate|reset)\s*\(', all_text)
    report = ROOT / 'docs/qa/mario-flower900-preparation-2026-10-26.txt'
    assert report.is_file()
    hard_report = ROOT / 'docs/qa/mario-luigi900-hard-pickup-paths-2026-10-26.txt'
    assert hard_report.is_file()
    controls = [
        [sys.executable, '-B', str(ROOT / 'tools/audit/mario_flower900_source_v1.py'),
         '--rom', str(rom), '--output', str(out / 'source-controls-v1')],
        [sys.executable, '-B', str(ROOT / 'tools/audit/mario_powerups_current3cee_static_v2.py'),
         '--fixture', str(folder), '--rom', str(rom),
         '--lua-root', str(D / 'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1'),
         '--output', str(out / 'startup-static-v1')]]
    for i, command in enumerate(controls):
        z = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        (out / ('control-' + str(i) + '.log')).write_text(z.stdout + z.stderr, encoding='utf-8')
        assert z.returncode == 0, z.stderr
    source_manifest = json.loads((source / 'source-manifest.json').read_text())
    deps = {rom, rom.with_suffix('.dbg'), rom.with_suffix('.lbl'), source / 'proof.json',
            source / 'source-manifest.json', Path(__file__), module, report, hard_report, env_path, guard,
            ROOT / 'tools/audit/mario_flower900_source_v1.py',
            ROOT / 'tools/audit/mario_flower900_run_v1.py',
            ROOT / 'tools/audit/mario_powerups_current3cee_static_v2.py',
            ROOT / 'tools/audit/parodius_visibility_hud_static_startup_v1.py',
            ROOT / 'tools/audit/robots_weapon_cpu_v1.py', ROOT / 'tools/audit/verify_native_relocation.py',
            ROOT / 'tools/audit/check_tmnt_render_oa.py', ROOT / 'tools/audit/observe_chip_committed_write.py',
            ROOT / 'tools/audit/run_mesen_isolated.py', ROOT / 'tools/run_mesen.py'}
    for rel, h in source_manifest.items():
        f = source / 'source' / rel
        assert sha(f) == h
        deps.add(f)
    for n in ['emulator', 'core', 'worker_settings', 'user_settings']:
        deps.add(Path(env[n]))
    deps |= {parent / n for n in ['native-receipt.json', 'configuration.json', 'harness.lua', 'audit.lua']}
    deps |= {original / n for n in ['policy.lua', 'manifest.json', 'trace.csv']}
    deps |= {f for f in out.rglob('*') if f.is_file()}
    lua_deps = D / 'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1'
    deps |= {f for f in lua_deps.rglob('*') if f.is_file() and '__pycache__' not in f.parts}
    command = [sys.executable, '-B', str(ROOT / 'tools/audit/run_mesen_isolated.py'),
               '--output', str(folder), '--emulator', env['emulator'], str(folder / 'run.lua'),
               str(rom), '--timeout', '180']
    command += ['--option=' + v for v in env['deterministic_command_overrides']]
    ready = dict(passed=True, status='PREPARE_DO_NOT_RUN', native_executed=False, native_grant=False,
                 native_workers=1, ROM_sha256=SHA, ordinary_route_parent_SHA256='3cee18caa732b2e85e3bdb00faf719223324f9bf24e72dd30c56be355da33b99',
                 profiles=[dict(name='mario-easy', mode=0, character=0, variant=0,
                    fixture=str(folder), limit_physical_frames=6500, command=command,
                    endpoint='Real mushroom then later flower while retainingSuper, two native transforms, actual B fireball enemy/brick contact and projectile cleanup')],
                 bindings={str(f): sha(f) for f in sorted(deps, key=str)}, environment=env,
                 no_emulated_state_RNG_resource_or_actor_writes=True,
                 real_second_block_source_coordinate=[1248, 144],
                 original_completed_loop_CHR_raster_mode_death_guards_retained=True,
                 source_CPU_Hard_mismatch_documentation_only=True,
                 limits='Controller itinerary is prepared, not native-proven. No flower/use pass, Hard/fullroute/allitems/waveform/entire5SMC-SP claim.')
    put(out / 'readiness.json', ready)
    put(out / 'command.json', dict(not_executed=True, explicit_new_ROOT_native_grant_required=True,
        command=[sys.executable, '-B', str(ROOT / 'tools/audit/mario_flower900_run_v1.py'), '--packet', str(out),
                 '--expected-readiness-sha256', sha(out / 'readiness.json'), '--native-grant']))
    print(json.dumps(dict(passed=True, native_executed=False, profiles=1,
                          bindings=len(ready['bindings']), readiness=str(out / 'readiness.json'),
                          readiness_sha256=sha(out / 'readiness.json')), indent=2))


if __name__ == '__main__':
    main()
