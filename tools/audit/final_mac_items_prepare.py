"""Freeze two source-only Mac item lifecycles without launching an emulator."""
from pathlib import Path
from collections import deque
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys

from check_tmnt_render_oa import address, location
from link_pit_rygar_sophia_audit_cpu import scoped_load

ROOT = Path(__file__).resolve().parents[2]
TARGET = '8ff245ae662059abbc77c5de517260032775b7ba881a5201b8b54686ccf08277'
OLD_FIXTURE = 'da17fa7fd11dc8bdb804d6954c56771d6177fa679bcaed14707625522a9a567d'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def lua(value):
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, str):
        return json.dumps(value)
    if isinstance(value, list):
        return '{' + ','.join(lua(x) for x in value) + '}'
    if isinstance(value, dict):
        return '{' + ','.join('[' + lua(k) + ']=' + lua(v) for k, v in value.items()) + '}'
    if value is None:
        return 'nil'
    assert isinstance(value, (int, float)), type(value)
    return str(value)


def plan():
    return [
        dict(action='damage', name='six-real-contacts96-to48', contacts=6, hp=48, stars=0),
        dict(action='block', name='physical-mushroom-heals24-to72', type=0, hp=72, stars=0),
        *[dict(action='block', name=f'physical-flower-star-{i}', type=1, hp=72, stars=min(i, 3))
          for i in range(1, 5)],
        dict(action='super', name='earned-up-B-spends-star', hp=72, stars=2),
        dict(action='damage', name='real-contact-removes-star', contacts=1, hp=64, stars=1),
        dict(action='lethal', name='eight-real-contacts-death-healthy-respawn', contacts=8),
    ]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--expected-sha256', default=TARGET)
    p.add_argument('--parser', type=Path,
                   default=ROOT/'build/verification/agent47-samus-controller-batch-h-preparation/parser')
    p.add_argument('--lua-python', type=Path, default=Path.home()/
                   '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe')
    a = p.parse_args()
    assert sha(a.rom) == a.expected_sha256
    old = ROOT/'tests/little-mac-powerups.lua'
    assert sha(old) == OLD_FIXTURE, 'Preserve the reference fixture unchanged'
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(parents=True, exist_ok=False)
    frozen = out/'frozen-current'
    frozen.mkdir()
    for ext in ['.nes', '.dbg', '.lbl', '.map']:
        shutil.copy2(a.rom.with_suffix(ext), frozen/('candidate' + ext))
    fixture = ROOT/'tools/audit/final_mac_items_native.lua'
    guards = ROOT/'tools/audit/vehicles_audio_wiring_guards.lua'
    chr_observer = ROOT/'tools/audit/chr_commit_observer.lua'
    for f in [fixture, guards, chr_observer, Path(__file__), old]:
        shutil.copy2(f, frozen/f.name)
    for f in sorted(a.source.glob('little_mac*')):
        if f.is_file():
            shutil.copy2(f, frozen/f.name)
    ledger = {f.name: sha(f) for f in frozen.iterdir() if f.is_file()}
    (frozen/'bindings.json').write_text(json.dumps(ledger, indent=2) + '\n')
    b = scoped_load(frozen/'candidate.nes')
    text = fixture.read_text()
    used = set(re.findall(r"'([A-Za-z_][A-Za-z_0-9]*)'", text))
    used |= set(re.findall(r'\bL\.([A-Za-z_][A-Za-z_0-9]*)', text))
    ram = {n: address(b, n) for n in used if n in b['syms']}
    for n in ['CurrentBank', 'CurrentBankC', 'OperMode', 'GameEngineSubroutine',
              'NonMaskableInterrupt', 'DisableScreenFlag', 'Mirror_PPUMASK']:
        ram[n] = address(b, n)
    direct = set(re.findall(r"\b[wr]\('([A-Za-z_][A-Za-z_0-9]*)'", text))
    assert not direct - set(ram), direct - set(ram)
    names = re.findall(r"\bhook\('([A-Za-z_][A-Za-z_0-9]*)'", text)
    hooks = {n: dict(address=address(b, n), physical_bank=(location(b, n)-16)//8192,
                     bytes=list(b['raw'][location(b, n):location(b, n)+3]))
             for n in names if n not in ['finish', 'NmiReturn']}
    for name, original in [('finish', 'GameLoop'), ('NmiReturn', 'NonMaskableInterrupt')]:
        delta = int(b['syms'][original]['size'], 0)-1
        pos = location(b, original)+delta
        assert b['raw'][pos] in [0x60, 0x40]
        hooks[name] = dict(address=address(b, original)+delta,
                           physical_bank=(pos-16)//8192, bytes=[b['raw'][pos]])
    count = address(b, 'X5MenuPresent')-address(b, 'X5MenuCharacters')
    def tab(n):
        at = location(b, n)
        return list(b['raw'][at:at+count])
    target = tab('X5MenuCharacters').index(15)
    maps = {n.lower(): tab('X5Menu'+n) for n in ['Up', 'Down', 'Left', 'Right']}
    moves = []
    for start in range(count):
        todo = deque([(start, [])]); seen = {start}
        while todo:
            node, path = todo.popleft()
            if node == target:
                moves.append(path[0] if path else '')
                break
            for direction, links in maps.items():
                if links[node] not in seen:
                    seen.add(links[node]); todo.append((links[node], path+[direction]))
        else:
            raise AssertionError('Actual menu cannot reach Mac')
    smc = next(x for x in b['segs'].values() if x.get('name') == '"SMCCODE"')
    guard_config = dict(nmi=address(b, 'NonMaskableInterrupt'),
                        nmi_return=hooks['NmiReturn']['address'], music=0,
                        smc=[address(b, n)+1 for n in ['NextBank_SMC', 'SafecallA_SMC',
                            'SafereturnA_SMC', 'FarcallJmpTarget_SMC']]+[address(b, 'FarcallJmpTarget_SMC')+2],
                        stack_floor=(int(smc['start'], 0)+int(smc['size'], 0)) & 255,
                        stack_start=int(smc['start'], 0) & 255,
                        chr_observer=(frozen/chr_observer.name).as_posix())
    common = dict(ROM_sha256=a.expected_sha256, ram=ram, hooks=hooks,
                   powerup_sfx=address(b, 'Sfx_PowerUpGrab'), menu_target=target,
                   menu_moves=moves, star_bank=(location(b, 'LmStar')-16)//8192,
                   art={n: dict(address=address(b, n), bank=(location(b, n)-16)//8192)
                        for n in ['MTileTopLeft', 'MTileTopRight', 'MTileBotLeft',
                                  'MTileBotRight', 'MTileAttribute']}, plan=plan())
    assert len(common['plan']) == 9
    # Verified, existing Lua54 compiler: parse only, never start an emulator.
    provenance = json.loads((a.parser/'provenance.json').read_text())
    for q in [provenance['wheel']] + provenance['extracted']:
        assert sha(Path(q['path'])) == q['sha256']
    compiler = ('import pathlib,sys;sys.path.insert(0,sys.argv[1]);'
                'from lupa.lua54 import LuaRuntime;'
                'LuaRuntime().eval("function(s)local f,e=load(s);assert(f,e);return true end")'
                '(pathlib.Path(sys.argv[2]).read_text(encoding="utf-8"));print("Lua54 parse PASS")')
    profiles = []
    for mode in [0, 1]:
        label = 'hard' if mode else 'easy'
        folder = out/(label+'-prepared-v1')
        folder.mkdir()
        cfg = dict(common, mode_value=mode, mode_label=label)
        script = ('VEHICLE_AUDIO_CONFIG='+lua(guard_config)+'\n' +
                  (frozen/guards.name).read_text().replace('character=19', 'character=15') +
                  '\nFINAL_MAC_ITEMS='+lua(cfg)+'\n'+text)
        assert '["mode_value"]='+str(mode) in script
        (folder/'run.lua').write_text(script, encoding='utf-8')
        compiled = subprocess.run([str(a.lua_python), '-c', compiler,
                                   str(a.parser/'runtime'), str(folder/'run.lua')],
                                  capture_output=True, text=True)
        (folder/'parse.log').write_text(compiled.stdout+compiled.stderr)
        assert compiled.returncode == 0, compiled.stdout+compiled.stderr
        (folder/'config.json').write_text(json.dumps(cfg, indent=2)+'\n')
        profiles.append(dict(mode=label, numeric_mode=mode, script=str(folder/'run.lua'),
                             script_sha256=sha(folder/'run.lua'), passed=False,
                             status='prepared_parsed_not_native_run'))
    report = dict(status='SOURCE_ONLY_PREPARED_NOT_NATIVE_RUN', passed=False,
                   ROM_sha256=a.expected_sha256, fixture_sha256=sha(fixture),
                   preparer_sha256=sha(Path(__file__)), reference_fixture_sha256=OLD_FIXTURE,
                   frozen_bindings_sha256=sha(frozen/'bindings.json'), profiles=profiles,
                   guard_sha256=sha(guards), CHR_observer_sha256=sha(chr_observer),
                   Lua54_compiler_python_sha256=sha(a.lua_python),
                   Lua54_parser_provenance_sha256=sha(a.parser/'provenance.json'),
                   expected=dict(plan_steps=9, real_Goomba_contacts=15, physical_pickups=5,
                                 flowers=4, star_cap=3, earned_super_spend=1, healthy_respawn_HP=96),
                   resource_writes=False, PlayerStatus_writes=False, injected_pickup_actors=False,
                   item_contact_teleports=False, native_emulator_launched=False,
                   scope='Source-only. Actual cold menus and numeric readback; explicit aligned terrain/player/Goomba setup; unmodified native HP, stars, stamina, injury and attacks. Controller item bumps/collection and earned super; actual contact damage/death/respawn. Timings/expectations require granted native validation.')
    (out/'preparation.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(dict(status=report['status'], ROM_sha256=a.expected_sha256,
                         preparation_sha256=sha(out/'preparation.json'), profiles=2)))


if __name__ == '__main__':
    main()
