"""Prepare the exact passing east-v4 component on clean731; never run Mesen."""
from pathlib import Path
import argparse
import difflib
import hashlib
import json
import re
import shutil
import subprocess
import sys

from check_tmnt_render_oa import address, load, location
from observe_chip_committed_write import lua
from robots_weapon_cpu_v1 import Arena
from mario_flower900_prepare_v4 import controller_controls, east_controls

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
SOURCE = D / 'mm-proto-clean-menu-candidates-v1/clean-menu-irq'
SHA = '731c918b0f448564587d90fca2979afc9fc0e5eb9b26616f4241801e2e73e16c'
PRIOR = D / 'mario-flower900-east-v4-ready-v2'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def get(p):
    return json.loads(Path(p).read_text())


def put(p, z):
    assert not p.exists(), p
    p.write_text(json.dumps(z, indent=2) + '\n', encoding='utf-8')


def source_controls(b, rom, output):
    """Same literal compiled cases as frozen900; new execution/receipt on731."""
    start = location(b, 'L_GroundArea6')
    data = b['raw'][start:start + 28]
    page, authored = 0, []
    for i in range(13):
        first, second = data[2 + 2 * i:4 + 2 * i]
        assert first & 15 <= 12
        if second & 128:
            page += 1
        if second & 127 == 0:
            authored.append(dict(pair=i, pair_bytes=[first, second],
                                 x=page * 256 + (first >> 4) * 16, y=32 + (first & 15) * 16))
    assert [r['x'] for r in authored] == [336, 1248] and all(r['y'] == 144 for r in authored)
    cases = []
    for mode, power, kind in [(0, 0, 0), (0, 1, 1), (1, 1, 0), (1, 0, 1)]:
        for char, owner in [(0, 'MarioSourceBeginPowerup'), (8, 'GuestBeginPowerup')]:
            q = Arena(b, char=char)
            q.put(CrossoverBehaviorVersion=mode, PlayerStatus=power,
                  GuestPowerupActive=0, GuestPowerupTarget=0)
            q.set('PowerUpType', kind, 5)
            q.invoke(owner, x=5)
            active = q.get('GuestPowerupActive')
            target = q.get('GuestPowerupTarget') if active else power
            assert target == (min(2, power + 1) if char == 8 or mode == 0 else max(power, kind + 1))
            cases.append(dict(character=char, mode=mode, before_power=power, authored_type=kind,
                              actual_assembled_begin_owner=owner, actual_active=active, eventual_target=target))
    contacts = []
    for char in [0, 8]:
        q = Arena(b, char=char)
        q.put(CrossoverBehaviorVersion=1)
        c, _ = q.invoke('MarioSourceFireballBrick', a=0x51)
        assert bool(c.p & 1) == (char == 0)
        contacts.append(dict(character=char, Hard_brick51_passthrough=bool(c.p & 1)))
    old = get(PRIOR / 'source-controls-v1/proof.json')
    assert old['ROM_sha256'] == '900b669e212b878041c23e438f2fb26e310ce8f929f904681a9c4b17405b6968'
    assert old['begin_component_cases'] == cases and old['brick_component_cases'] == contacts
    assert old['real_level_prefix'] == authored
    output.mkdir()
    put(output / 'proof.json', dict(passed=True, native_executed=False, source_CPU_only=True,
        ROM_sha256=sha(rom), begin_component_cases=cases, brick_component_cases=contacts,
        real_level_prefix=authored, cases_and_assertions_equal_frozen900=True,
        historical900_proof_sha256=sha(PRIOR / 'source-controls-v1/proof.json'),
        scope='Fresh731 assembled ten component calls and authored bytes; no new native result. Unchanged Hard policy is documented only.'))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(parents=True, exist_ok=False)
    rom = SOURCE / 'candidate.nes'
    assert sha(rom) == SHA and get(SOURCE / 'proof.json')['ROM_sha256'] == SHA
    source_manifest = get(SOURCE / 'source-manifest.json')
    for rel, h in source_manifest.items():
        assert sha(SOURCE / 'source' / rel) == h, rel
    oldproof = PRIOR / 'native-result-freeze-v1/proof.json'
    assert sha(oldproof) == 'd2524aeb0b7701a1921f175e000db5849bc9e985c1e2ef387d90c9bf7aa60f35'
    prior = get(oldproof)
    assert prior['passed'] and prior['ROM_sha256'] != SHA
    for f, h in prior['bindings'].items():
        assert sha(f) == h, f
    environment_path = D / 'parodius-menu3cee-ready-v1/environment.json'
    env = get(environment_path)
    for n in ['emulator', 'core', 'worker_settings', 'user_settings']:
        assert sha(env[n]) == env[n + '_sha256'], n
    put(out / 'environment.json', env)
    b = load(rom)
    folder = out / 'mario-easy'
    folder.mkdir()
    (folder / 'frames').mkdir()
    parent = PRIOR / 'mario-easy'
    module = ROOT / 'tools/audit/mario_flower900_native_v4.lua'
    assert sha(module) == '60bca70d6ff1a5c2e861b9ae10a17f1635d8bc6a8e9304890a6bc52a65bf0a2c'
    before = get(parent / 'configuration.json')
    cfg = dict(before['roster'])
    cfg.update(out=folder.as_posix() + '/', policy=(folder / 'policy.lua').as_posix(),
               audit=(folder / 'audit.lua').as_posix())
    item = dict(before['item'])
    item['ROM_sha256'] = SHA
    item['hooks'] = {n: dict(address=address(b, n), bank=(location(b, n) - 16) // 8192,
                            bytes=list(b['raw'][location(b, n):location(b, n) + 3])) for n in before['item']['hooks']}
    item['ram'] = {n: address(b, n) for n in before['item']['ram']}
    item['sfx'] = {k: address(b, v) for k, v in [('reveal', 'Sfx_GrowPowerUp'),
                      ('pickup', 'Sfx_PowerUpGrab'), ('fire', 'Sfx_Fireball')]}
    put(folder / 'configuration.json', dict(roster=cfg, item=item))
    for name in ['harness.lua', 'audit.lua']:
        shutil.copyfile(parent / name, folder / name)
        assert sha(parent / name) == sha(folder / name)
    oldguard = D / 'current3cee-remaining27-routes-v1/native/native-guard.lua'
    guardbody = oldguard.read_text().split('local checks,maxWorld,maxCamera=', 1)[1]
    motion_names = ['OperMode', 'OperMode_Task', 'GameEngineSubroutine', 'WorldNumber', 'LevelNumber',
                    'Player_X_Position', 'Player_PageLoc', 'Player_Y_Position', 'ScreenLeft_X_Pos', 'ScreenLeft_PageLoc']
    offset = int(b['syms']['GameLoop']['size'], 0) - 1
    loc = location(b, 'GameLoop') + offset
    assert b['raw'][loc] == 0x60
    motion = dict(address=address(b, 'GameLoop') + offset, physical_bank=(loc - 16) // 8192,
                  bytes=list(b['raw'][loc:loc + 8]))
    guard = out / 'native-guard.lua'
    guard.write_text('OUTPUT=ROSTER_CONFIG.out\nMOTION_RAM=' + lua({n: address(b, n) for n in motion_names}) +
                     '\nMOTION_HOOK=' + lua(motion) + '\nlocal checks,maxWorld,maxCamera=' + guardbody,
                     encoding='utf-8', newline='\n')
    oldpolicy = (parent / 'policy.lua').read_text()
    policy = 'dofile(' + lua(guard.as_posix()) + ')\n' + oldpolicy.split('\n', 1)[1]
    rebinding = []
    def bind(match):
        name, old = match[1], int(match[2])
        actual = address(b, name)
        rebinding.append(dict(symbol=name, old=old, actual=actual))
        return 'L.' + name + '=' + str(actual)
    policy = re.sub(r'^L\.(\w+)=(\d+)\s*$', bind, policy, flags=re.M)
    (folder / 'policy.lua').write_text(policy, encoding='utf-8', newline='\n')
    script = ('ROSTER_CONFIG=' + lua(cfg) + '\nMARIO_FLOWER_CONFIG=' + lua(item) +
              '\ndofile(' + lua(module.as_posix()) + ')\ndofile(' + lua((folder / 'harness.lua').as_posix()) +
              ')\nassert(MARIO_POWERUP_INSTALL_CHR_DISPATCHER)()\n')
    (folder / 'run.lua').write_text(script, encoding='utf-8', newline='\n')
    assert not re.search(r'\bemu\.(?:write\w*|setState|loadSavestate|reset)\s*\(',
                         module.read_text() + policy + script + (folder / 'harness.lua').read_text() + (folder / 'audit.lua').read_text())
    changes = []
    for name in ['harness.lua', 'audit.lua', 'policy.lua', 'configuration.json', 'run.lua']:
        changes += difflib.unified_diff((parent / name).read_text().splitlines(keepends=True),
                                       (folder / name).read_text().splitlines(keepends=True),
                                       fromfile='exact900/' + name, tofile='clean731/' + name)
    (out / 'metadata-rebind-only.diff').write_text(''.join(changes), encoding='utf-8', newline='\n')
    put(out / 'actual731-source-configuration.json', dict(passed=True, native_executed=False, ROM_sha256=SHA,
        hooks=item['hooks'], ram=item['ram'], sfx=item['sfx'], completed_GameLoop_RTS=motion,
        constant_L_bindings=rebinding, observer_sha256=sha(module),
        observer_harness_and_audit_byteexact=True, dynamic_L_B_from_actual_ROM_debug_labels=True,
        no_legacy_address_alias_or_result_transfer=True))
    source_controls(b, rom, out / 'source-controls-v1')
    static = [sys.executable, '-B', str(ROOT / 'tools/audit/mario_powerups_current3cee_static_v2.py'),
              '--fixture', str(folder), '--rom', str(rom), '--lua-root',
              str(D / 'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1'),
              '--output', str(out / 'startup-static-v1')]
    z = subprocess.run(static, cwd=ROOT, capture_output=True, text=True)
    (out / 'static-host.log').write_text(z.stdout + z.stderr, encoding='utf-8')
    assert z.returncode == 0, z.stderr
    controller_controls(folder, module, b, rom, out / 'controller-source-controls-v1')
    east_controls(folder, b, rom, out / 'east-source-controls-v1')
    report = ROOT / 'docs/qa/mario-flower731-east-preparation-2026-10-26.txt'
    deps = {Path(__file__), module, report, oldproof, environment_path,
            rom, rom.with_suffix('.dbg'), rom.with_suffix('.lbl'), SOURCE / 'proof.json', SOURCE / 'source-manifest.json',
            ROOT / 'tools/audit/mario_flower900_prepare_v4.py', ROOT / 'tools/audit/mario_flower900_run_v1.py',
            ROOT / 'tools/audit/mario_powerups_current3cee_static_v2.py',
            ROOT / 'tools/audit/parodius_visibility_hud_static_startup_v1.py',
            ROOT / 'tools/audit/check_tmnt_render_oa.py', ROOT / 'tools/audit/robots_weapon_cpu_v1.py',
            ROOT / 'tools/audit/verify_native_relocation.py', ROOT / 'tools/audit/observe_chip_committed_write.py',
            ROOT / 'tools/audit/run_mesen_isolated.py', ROOT / 'tools/run_mesen.py', oldguard}
    deps |= {SOURCE / 'source' / f for f in source_manifest}
    deps |= {parent / f for f in ['policy.lua', 'configuration.json', 'harness.lua', 'audit.lua', 'run.lua']}
    deps |= {Path(f) for f in prior['bindings']}
    deps |= {Path(env[n]) for n in ['emulator', 'core', 'worker_settings', 'user_settings']}
    deps |= {f for f in out.rglob('*') if f.is_file()}
    lua_deps = D / 'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1'
    deps |= {f for f in lua_deps.rglob('*') if f.is_file() and '__pycache__' not in f.parts}
    command = [sys.executable, '-B', str(ROOT / 'tools/audit/run_mesen_isolated.py'), '--output', str(folder),
               '--emulator', env['emulator'], str(folder / 'run.lua'), str(rom), '--timeout', '180']
    command += ['--option=' + s for s in env['deterministic_command_overrides']]
    ready = dict(passed=True, status='PREPARE_DO_NOT_RUN', native_executed=False, native_grant=False,
        ROM_sha256=SHA, native_workers=1, environment=env,
        profiles=[dict(name='mario-easy', mode=0, character=0, variant=0, fixture=str(folder),
                       command=command, limit_physical_frames=6500,
                       endpoint='Genuine physical mushroom then later flower,120sourcegrowth, live enemy fireball contact, release and45drain')],
        bindings={str(f): sha(f) for f in sorted(deps, key=str)},
        exact900_pass_is_historical_only=True, observer_controller_semantic_guards_unchanged=True,
        actual731_compiled_metadata_bound=True, no_game_state_or_settings_writes=True,
        one_new_ROOT_grant_required=True,
        limits='Prepared only. No fresh731 native/contact/visual/Hard/allitems/fullroute/waveform result.')
    put(out / 'readiness.json', ready)
    put(out / 'command.json', dict(not_executed=True, explicit_new_ROOT_grant_required=True,
        command=[sys.executable, '-B', str(ROOT / 'tools/audit/mario_flower900_run_v1.py'), '--packet', str(out),
                 '--expected-readiness-sha256', sha(out / 'readiness.json'), '--native-grant']))
    print(json.dumps(dict(passed=True, native_executed=False, profiles=1, bindings=len(ready['bindings']),
        readiness_sha256=sha(out / 'readiness.json'), command_sha256=sha(out / 'command.json')), indent=2))


if __name__ == '__main__':
    main()
