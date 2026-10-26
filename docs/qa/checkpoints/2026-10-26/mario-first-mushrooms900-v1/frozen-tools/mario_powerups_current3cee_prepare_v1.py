"""Prepare four natural first-mushroom components, without running Mesen."""
from pathlib import Path
import argparse
import csv
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
SHA = '3cee18caa732b2e85e3bdb00faf719223324f9bf24e72dd30c56be355da33b99'
NAMES = ['mario', 'luigi', 'mario3', 'luigi3']


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(p, value):
    p.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def once(s, old, new):
    assert s.count(old) == 1, old
    return s.replace(old, new)


def static_chr(s):
    """Retain the actual CHR observer, moving its return slot to startup."""
    pattern = (r'  if not returns\[pc\]then\n   returns\[pc\]=true\n'
               r'   emu\.addMemoryCallback\(function\(\)\n(.*?)\n'
               r'   end,emu\.callbackType\.exec,pc\)\n  end')
    matches = list(re.finditer(pattern, s, re.S))
    assert len(matches) == 1
    m = matches[0]
    body = m.group(1)
    assert body.strip() in [
        'if inside and inside.pc==pc and emu.getState()[\'cpu.sp\']==inside.sp then finishBody()end',
        'if inside and inside.pc==pc and emu.getState()[\'cpu.sp\']==inside.sp then inside=nil end']
    s = s[:m.start()] + '  returns[pc]=true' + s[m.end():]
    at = s.index(' emu.addEventCallback(function()', s.index('local returns='))
    deferred = (" MARIO_POWERUP_INSTALL_CHR_DISPATCHER=function()\n"
                "  emu.addMemoryCallback(function(pc)\n" + body +
                "\n  end,emu.callbackType.exec,0,65535)\n end\n")
    return s[:at] + deferred + s[at:]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--rom', type=Path, default=D / 'root-chip-hud-composed-v1/candidate.nes')
    p.add_argument('--expected-rom-sha256', default=SHA)
    a = p.parse_args()
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(parents=True, exist_ok=False)
    rom = a.rom.resolve()
    source = rom.parent
    target_sha = a.expected_rom_sha256
    assert sha(rom) == target_sha
    bundle = load(rom)
    source_manifest = json.loads((source / 'source-manifest.json').read_text())
    for name, h in source_manifest.items():
        assert sha(source / 'source' / name) == h, name
    env_path = D / 'parodius-menu3cee-ready-v1/environment.json'
    env = json.loads(env_path.read_text())
    for n in ['emulator', 'core', 'worker_settings', 'user_settings']:
        assert sha(env[n]) == env[n + '_sha256'], n
    shutil.copyfile(env_path, out / 'environment.json')
    native = D / 'current3cee-remaining27-routes-v1/native'
    profile_index = json.loads((native / 'proof.json').read_text())
    coverage = []
    required = ['PwrUpJmp', 'MarioSourcePowerupCollision', 'MarioSourcePowerupUpdate',
                'GuestPowerupUpdate', 'M3CollectPickup', 'M3Graphics']
    hooks = {n: dict(address=address(bundle, n), bank=(location(bundle, n) - 16) // 8192,
                     bytes=list(bundle['raw'][location(bundle, n):location(bundle, n) + 3]))
             for n in required}
    module = ROOT / 'tools/audit/mario_powerups_current3cee_native_v1.lua'
    module_text = module.read_text(encoding='utf-8')
    used = set(re.findall(r"\br\('([A-Za-z_][A-Za-z_0-9]*)'", module_text))
    used |= {'MarioVariant', 'M3Variant', 'Square2SoundQueue'}
    ram = {n: address(bundle, n) for n in used}
    deps = {Path(__file__), module, env_path, source / 'proof.json', source / 'source-manifest.json',
            rom, rom.with_suffix('.dbg'), rom.with_suffix('.lbl'), native / 'proof.json',
            ROOT / 'tools/audit/mario_powerups_current3cee_run_v1.py',
            ROOT / 'tools/audit/mario_powerups_current3cee_static_v1.py',
            ROOT / 'tools/audit/run_mesen_isolated.py', ROOT / 'tools/run_mesen.py',
            ROOT / 'tools/audit/check_tmnt_render_oa.py', ROOT / 'tools/audit/observe_chip_committed_write.py',
            ROOT / 'tools/audit/parodius_visibility_hud_static_startup_v1.py'}
    deps |= {Path(env[n]) for n in ['emulator', 'core', 'worker_settings', 'user_settings']}
    deps |= {source / 'source' / n for n in source_manifest}
    profiles = []
    for name in NAMES:
        original = native / (name + '-easy')
        m = json.loads((original / 'manifest.json').read_text())
        assert m['ROM_sha256'] == SHA and m['controller_only'] and m['memory_writes'] is False
        row = next(v for v in profile_index['runs'] if v['identity'] == name)
        assert row['passed'] and row['replay']['passed']
        trace = list(csv.DictReader((original / 'trace.csv').open()))
        changes = [{k: after[k] for k in ['frame', 'x', 'y', 'power', 'engine']}
                   for before, after in zip(trace, trace[1:]) if before['power'] != after['power']]
        coverage.append(dict(identity=name, ROM_sha256=SHA, actual_numeric_mode=0,
                             current_trace=str(original / 'trace.csv'), transitions=changes,
                             item_kind_private_stamp_M3Form_and_full_lifecycle_not_logged=True,
                             qualified_item_scope='No progression' if not changes else
                             'Generic0-to1 then injury1-to0 only; item owner/form/use unproved'))
        folder = out / (name + '-easy')
        folder.mkdir()
        (folder / 'frames').mkdir()
        cfg = dict(m['config'])
        cfg.update(out=folder.as_posix() + '/', policy=(folder / 'policy.lua').as_posix(),
                   audit=(folder / 'audit.lua').as_posix(), limit=4000, capture=8,
                   record=False, replay=None, prefix=None)
        cfg_item = dict(character=cfg['character'], variant=cfg['variant'],
                        variantSymbol=cfg['variantSymbol'], mode=0, ROM_sha256=target_sha,
                        hooks=hooks, ram=ram,
                        sfx=dict(reveal=address(bundle, 'Sfx_GrowPowerUp'),
                                 pickup=address(bundle, 'Sfx_PowerUpGrab')))
        put(folder / 'configuration.json', dict(roster=cfg, item=cfg_item))
        body = (original / 'policy.lua').read_text().split('\n', 1)[1]
        assert not re.search(r'\bemu\.(?:write\w*|setState|loadSavestate|reset)\s*\(', body)
        guard = original.parent / 'native-guard.lua'
        policy = ('dofile(' + lua(guard.as_posix()) + ')\nlocal base=(function()\n' + body +
                  '\nend)()\nreturn function(c)return MARIO_POWERUP_CONTROL(c,base)end\n')
        (folder / 'policy.lua').write_text(policy, encoding='utf-8', newline='\n')
        harness = (original / 'harness.lua').read_text()
        harness = once(harness, 'if audit then audit.finish()end',
                       'if audit then audit.finish()end\n MARIO_POWERUP_FINISH()')
        harness = once(harness, '{"cleared":', '{"component_complete":')
        old_endpoint = ("  if c.world==0 and c.level==1 and c.engine==8 then\n"
                        "   nextControl=nextControl+1;if not nextX then nextX=c.x end\n"
                        "   if nextControl>=25 and c.x>nextX+5 then finish(true);return end\n  end")
        harness = once(harness, old_endpoint,
                       "  if MARIO_POWERUP_DONE and c.engine==8 then finish(true);return end")
        harness = once(harness, 'if cfg.replay and audit and audit.failure then',
                       'if audit and audit.failure then')
        (folder / 'harness.lua').write_text(harness, encoding='utf-8', newline='\n')
        audit_before = (original / 'audit.lua').read_text()
        audit_after = static_chr(audit_before)
        (folder / 'audit.lua').write_text(audit_after, encoding='utf-8', newline='\n')
        script = ('ROSTER_CONFIG=' + lua(cfg) + '\nMARIO_POWERUP_CONFIG=' + lua(cfg_item) +
                  '\ndofile(' + lua(module.as_posix()) + ')\ndofile(' +
                  lua((folder / 'harness.lua').as_posix()) + ')\n'
                  'assert(MARIO_POWERUP_INSTALL_CHR_DISPATCHER)()\n')
        (folder / 'run.lua').write_text(script, encoding='utf-8', newline='\n')
        assert not re.search(r'\bemu\.(?:write\w*|setState|loadSavestate|reset)\s*\(',
                             script + module_text + policy + harness + audit_after)
        deps |= {original / n for n in ['manifest.json', 'policy.lua', 'harness.lua',
                                        'audit.lua', 'trace.csv', 'events.csv', 'render.csv']}
        deps |= {guard, Path(row['replay']['folder']) / 'proof.json'}
        command = [sys.executable, '-B', str(ROOT / 'tools/audit/run_mesen_isolated.py'),
                   '--output', str(folder), '--emulator', env['emulator'], str(folder / 'run.lua'),
                   str(rom), '--timeout', '180']
        command += ['--option=' + v for v in env['deterministic_command_overrides']]
        profiles.append(dict(name=name + '-easy', mode=0, character=cfg['character'],
                             variant=cfg['variant'], fixture=str(folder), limit_physical_frames=4000,
                             command=command, ROM_sha256=target_sha,
                             endpoint='One genuine mushroom, original transform, powered crouch/jump/landing',
                             original_controller=str(original / 'policy.lua'),
                             controller_reuse='Exact current travel/first-block base; legacy historical detour only forMario/Luigi',
                             CHR_registration='Deferred fixed startup dispatcher; original returnPC/SP/body guards retained'))
    put(out / 'current-trace-coverage.json', dict(passed=True, offline_only=True, cases=coverage))
    put(out / 'source-owners.json', dict(passed=True, source_only=True, ROM_sha256=target_sha,
        hooks=hooks, ram=ram, source_files={n: source_manifest[n] for n in [
            'src/mario_source.s', 'src/luigi_native.s', 'src/smb3_mario_pickups.s',
            'src/smb3_mario_dispatch.s', 'src/smb3_mario_motion.s', 'src/smb3_mario_render.s',
            'src/smb3_mario_world.s', 'src/smb3_mario_combat.s', 'src/smb3_native_controller.inc']}))
    for profile in profiles:
        folder = Path(profile['fixture'])
        command = [sys.executable, '-B', str(ROOT / 'tools/audit/mario_powerups_current3cee_static_v1.py'),
                   '--fixture', str(folder), '--rom', str(rom),
                   '--lua-root', str(D / 'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1'),
                   '--output', str(folder / 'static-v1')]
        run = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        (folder / 'static-host.log').write_text(run.stdout + run.stderr, encoding='utf-8')
        assert run.returncode == 0, (profile['name'], run.stderr)
        assert json.loads((folder / 'static-v1/proof.json').read_text())['passed']
    report = ROOT / 'docs/qa/mario-powerups-current3cee-preparation-2026-10-26.txt'
    assert report.is_file(), 'Prepare the explicit per-item coverage/checklist report first'
    deps.add(report)
    deps |= {f for f in out.rglob('*') if f.is_file()}
    lua_deps = D / 'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1'
    deps |= {f for f in lua_deps.rglob('*') if f.is_file() and '__pycache__' not in f.parts}
    bindings = {str(f): sha(f) for f in sorted(deps, key=str)}
    ready = dict(passed=True, status='PREPARE_DO_NOT_RUN', native_executed=False, native_grant=False,
                 ROM_sha256=target_sha, ordinary_trace_ROM_sha256=SHA,
                 native_workers=1, profiles=profiles, bindings=bindings,
                 environment=env, callback_registration_static=True,
                 ordinary_trace_results_not_transferred_to_new_components=True,
                 all_source_owner_controls_are_unrun_native_assertions=True,
                 scope='Four finiteEasy physical first-mushroom components only. No game-state/RNG/resource writes, source edits, installation, every-item or full-route claim.')
    put(out / 'readiness.json', ready)
    command = [sys.executable, '-B', str(ROOT / 'tools/audit/mario_powerups_current3cee_run_v1.py'),
               '--packet', str(out), '--expected-readiness-sha256', sha(out / 'readiness.json'), '--native-grant']
    put(out / 'command.json', dict(command=command, not_executed=True, explicit_ROOT_grant_still_required=True))
    print(json.dumps(dict(passed=True, native_executed=False, profiles=4, bindings=len(bindings),
                          readiness=str(out / 'readiness.json'), readiness_sha256=sha(out / 'readiness.json'),
                          command_sha256=sha(out / 'command.json')), indent=2))


if __name__ == '__main__':
    main()
