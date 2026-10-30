"""Prepare/launch one bounded controller-only DK or Super Maaa V13 route."""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import os
import re
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
O = R/'build/character-host-union-remaining-routes-v1'
P = R/'build/character-host-union-routes-v13-v4/goku-route-v1/ready.json'
ROM = R/'build/character-host-union-v13/candidate.nes'
sys.path[:0] = [str(R/'tools'), str(R/'tools/audit')]
from current_roster_compact_11_v1 import linked, lua
from capture_budget import capture_lease
from run_mesen import run


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prepare(name):
    out = O/name
    assert not out.exists(), 'Fresh output only'
    prior = json.loads(P.read_text())
    assert sha(P) == 'ed751be59bac9e29a741fafbec17d0568160c6803799d9acae52c0ac4967bdbd'
    for path, digest in prior['bindings'].items():
        assert sha(path) == digest, path
    plan_path = R/f'build/character-host-union-routes-v13/{name}-plan.json'
    plan = json.loads(plan_path.read_text())
    assert sha(ROM) == prior['ROM_sha256'] == plan['candidate_sha256']
    raw, syms, address, location, hook = linked(ROM)
    assert list(raw[location('X5MenuCharacters'):location('X5MenuCharacters')+32]) == [
        0,1,2,3,4,5,6,7,12,9,10,11,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32]
    edges = {k: list(raw[location('X5Menu'+k.title()):location('X5Menu'+k.title())+32])
             for k in ['left', 'right', 'up', 'down']}
    navigation = []
    for start in range(32):
        queue, seen = [(start, [])], {start}
        for node, route in queue:
            if node == plan['slot']:
                navigation.append(route[0] if route else '')
                break
            for key, table in edges.items():
                dest = table[node]
                assert 0 <= dest < 32
                if dest not in seen:
                    seen.add(dest)
                    queue.append((dest, route+[key]))
        else:
            raise AssertionError('Actual compiled menu unreachable')
    cfg = copy.deepcopy(prior['config'])
    cfg.update(name=name, character=plan['raw'], menu_index=plan['slot'],
               variant_symbol='MarioVariant' if name == 'supermaaa' else None,
               variant=plan['variant'], policy=Path(plan['policy']).as_posix(),
               out=out.as_posix()+'/', prefix=out.as_posix()+'/',
               limit=plan['frames'], navigation=navigation, extra_ram={})
    script = R/'tools/audit/roster_expansion_cold_capture_v3.lua'
    refs = set()
    for path, digest in plan['policy_graph'].items():
        assert sha(path) == digest, path
    for path in [script, *map(Path, plan['policy_graph'])]:
        text = path.read_text()
        assert not re.search(r'\bemu\.(?:write\w*|setState|loadSavestate|reset)\s*\(', text), path
        if path != script:
            assert not re.search(r'\bemu\.setInput\s*\(', text), path
        refs.update(re.findall(r'''\br\(['"]([^'"]+)['"]''', text))
    if cfg['variant_symbol']:
        refs.add(cfg['variant_symbol'])
    labels = {}
    for line in ROM.with_suffix('.lbl').read_text().splitlines():
        match = re.fullmatch(r'al ([0-9A-Fa-f]+) \.([\w]+)', line)
        if match:
            labels[match[2]] = int(match[1], 16)
    for name_ in refs:
        value = address(name_)
        if name_ in labels:
            assert labels[name_] == value
        else:
            assert syms[name_]['type'] == 'equ' and (value < 0x2000 or 0x5c00 <= value < 0x8000)
            cfg['extra_ram'][name_] = value
    assert cfg['hooks']['loop'] == hook('GameLoop')
    assert cfg['hooks']['loop_return'] == hook('GameLoop', tail=True)
    assert len(cfg['smc_fields']) == 33
    out.mkdir(parents=True)
    (out/'config.json').write_text(json.dumps(cfg, indent=2)+'\n')
    (out/'run.lua').write_text('ROSTER_CONFIG='+lua(cfg)+'\n'+
        'for name,value in pairs(ROSTER_CONFIG.extra_ram)do assert(L[name]==nil or L[name]==value,"RAM alias conflict: "..name);L[name]=value end\n'+
        'dofile('+lua(script.as_posix())+')\n', newline='\n')
    bindings = {str(Path(path).resolve()): digest for path, digest in prior['bindings'].items()
                if str(Path(path).resolve()).startswith(str(R/'build/verification/kamikaze-private-emulator-v1'))}
    bindings.update({str(Path(p).resolve()): h for p, h in plan['policy_graph'].items()})
    for path in [Path(__file__).resolve(), P, plan_path, ROM, ROM.with_suffix('.dbg'), ROM.with_suffix('.lbl'),
                 R/'build/character-host-union-v13/handoff.json', script,
                 R/'tools/audit/current_roster_compact_11_v1.py',
                 R/'tools/audit/final_inventory_compact_capture_v1.lua',
                 R/'tools/audit/final_inventory_compact_capture_v1.py',
                 R/'tools/audit/capture_budget.py', R/'tools/run_mesen.py',
                 out/'config.json', out/'run.lua']:
        bindings[str(path)] = sha(path)
    ready = dict(prepared=True, native_run=False, ROM_sha256=sha(ROM), config=cfg,
                 emulator=prior['emulator'], bindings=bindings, source_changes=False,
                 native_controller_only=True, normal_sprite_limit=True, grant_required=True,
                 host_timeout_seconds=600 if name == 'dk' else 300,
                 reason_for_host_bound='Same protectedcapture cost~179hostseconds/5222PPUframes; DKplan allows11000PPUframes, needing up to600hostseconds. Frame bound unchanged.',
                 scope='Actual coldmenu/lives/controller-onlyEasy1-1→25real1-2updates, zero deaths; discovery policy may fail. No all-item/source-fidelity/constant60Hz claim.')
    (out/'ready.json').write_text(json.dumps(ready, indent=2)+'\n')
    print(json.dumps(dict(prepared=name, ready=str(out/'ready.json'), sha256=sha(out/'ready.json'),
                          bindings=len(bindings), native_run=False)))


def launch(name):
    out = O/name
    ready = json.loads((out/'ready.json').read_text())
    assert not (out/'capture-budget.json').exists(), 'No implicit repeat/overwrite'
    for path, digest in ready['bindings'].items():
        assert sha(path) == digest, path
    with capture_lease():
        pass
    cmd = 'Get-CimInstance Win32_Process -Filter "Name = \'Mesen.exe\'" | Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress'
    data = subprocess.check_output(['powershell', '-NoProfile', '-Command', cmd], text=True).strip()
    rows = json.loads(data) if data else []
    rows = rows if isinstance(rows, list) else [rows]
    assert not [q for q in rows if '--testRunner' in (q.get('CommandLine') or '')
                and R.as_posix().lower() in q['CommandLine'].replace('\\', '/').lower()]
    os.environ['SMB_RUN_OUTPUT'] = str(out)
    code = run(out/'run.lua', ROM, ready['emulator'], timeout=ready['host_timeout_seconds'],
               emulator_options=['--doNotSaveSettings', '--nes.removeSpriteLimit=false',
                   '--nes.ramPowerOnState=AllZeros', '--nes.randomizeCpuPpuAlignment=false',
                   '--nes.randomizeMapperPowerOnState=false'])
    for path, digest in ready['bindings'].items():
        assert sha(path) == digest, path
    binding = dict(ROM_sha256=sha(ROM), ready_sha256=sha(out/'ready.json'), exit_code=code,
                   inputs=ready['bindings'], native_controller_only=True, normal_sprite_limit=True,
                   source_SMC_guard_bytes=33)
    (out/'binding.json').write_text(json.dumps(binding, indent=2)+'\n')
    result = json.loads((out/'result.json').read_text()) if (out/'result.json').exists() else None
    print(json.dumps(dict(exit_code=code, result=result)))
    raise SystemExit(code)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('name', choices=['dk', 'supermaaa'])
    parser.add_argument('--launch', action='store_true')
    args = parser.parse_args()
    launch(args.name) if args.launch else prepare(args.name)
