"""Prepare one corrected Luigi Rg-owner test; no native launches or game edits."""
from pathlib import Path
import argparse
import difflib
import json
import re
import shutil
import subprocess
import sys

from check_tmnt_render_oa import address, load, location
from robots_weapon_cpu_v1 import Arena
from verify_native_relocation import NesMPU
from observe_chip_committed_write import lua
from mario_powerups_current3cee_static_v2 import runtime, symbols
from mario_flower900_prepare_v4 import controller_controls
from mario_flower731_prepare_v1 import ROOT, D, SOURCE, SHA, get, put, sha

OLD = D / 'luigi-flower731-east-ready-v2'


def trace_call(q, name):
    b = q.b
    sym = b['syms'][name]
    seg = b['segs'][sym['seg']]
    bank = (int(seg['ooffs'], 0) - 16) // 8192
    pc = address(b, name)
    window = (pc - 0x8000) // 8192
    q.m.page(window, bank)
    if window in [1, 2]:
        q.set('CurrentBank' if window == 1 else 'CurrentBankC', bank | 128)
    c = NesMPU(memory=q.m, pc=pc)
    c.sp = 0xfd;c.p = 0x30;c.stPushWord(0x5aff)
    q.m.writes = []
    writes = []
    watched = set(range(address(b, 'RgShotType'), address(b, 'RgShotType') + 10)) | {address(b, 'Square1SoundQueue')}
    for _ in range(100000):
        if c.pc == 0x5b00:
            assert c.sp == 0xfd
            return writes
        pc = c.pc;count = len(q.m.writes)
        physical = q.m.banks[(pc - 0x8000) // 8192] if pc >= 0x8000 else -1
        code = list(q.m[pc:pc + 3])
        c.step()
        for at, v in q.m.writes[count:]:
            if at in watched:
                writes.append(dict(address=pc, bank=physical, bytes=code, destination=at, value=v))
    raise AssertionError('Bounded actual dispatcher CPU trace')


def owner_controls(bundle, output):
    requests = []
    actual = None
    for char, power, held, previous in [(8, 1, 64, 0), (8, 2, 0, 0), (8, 2, 64, 64), (0, 2, 64, 0), (8, 2, 64, 0)]:
        q = Arena(bundle, char=char)
        q.put(CrossoverBehaviorVersion=0, MarioVariant=int(char == 8), PlayerStatus=power,
              PlayerSize=0, Player_State=0, RgCrouch=0, RgPreviousButtons=previous,
              SavedJoypadBits=held, A_B_Buttons=held, PreviousA_B_Buttons=previous, TimerControl=0)
        trace = trace_call(q, 'ProcFireball_Bubble')
        alloc = [z for z in trace if z['value'] == 3 and z['destination'] in range(address(bundle, 'RgShotType'), address(bundle, 'RgShotType') + 10)]
        expected = char == 8 and power == 2 and held == 64 and previous == 0
        assert len(alloc) == int(expected)
        requests.append(dict(character=char, power=power, held=held, previous=previous, allocation_stores=alloc))
        if expected:
            fire = [z for z in trace if z['destination'] == address(bundle, 'Square1SoundQueue') and z['value'] == address(bundle, 'Sfx_Fireball')]
            assert len(fire) == 1 and q.get('MmBulletType') == 30 and q.get('MmSlot') == 0
            actual = (q, alloc[0], fire[0])
    q, alloc, fire = actual
    for store in [alloc, fire]:
        at = 16 + store['bank'] * 8192 + store['address'] % 8192
        assert list(bundle['raw'][at:at + 3]) == store['bytes']
    assert alloc['bytes'][0] == 0x9d and fire['bytes'] == [0x8d, address(bundle, 'Square1SoundQueue') % 256, address(bundle, 'Square1SoundQueue') // 256]
    assert address(bundle, 'ExpandedWeapons') <= alloc['address'] < address(bundle, 'ExpandedWeapons') + int(bundle['syms']['ExpandedWeapons']['size'], 0)
    # Genuine fresh input edges, preserving the weapon pool between calls.
    counts = [sum(q.get('RgShotType', i) == 3 for i in range(10))]
    for _ in range(2):
        for held in [0, 64]:
            q.put(SavedJoypadBits=held, A_B_Buttons=held, PreviousA_B_Buttons=0)
            q.invoke('ProcFireball_Bubble')
        counts.append(sum(q.get('RgShotType', i) == 3 for i in range(10)))
    assert counts == [1, 2, 2]
    # A moving source shot naturally leaves the viewport; no lifetime writes.
    cleared = None
    for age in range(1, 100):
        q.put(SavedJoypadBits=0, A_B_Buttons=0, PreviousA_B_Buttons=0)
        q.invoke('ProcFireball_Bubble')
        if not any(q.get('RgShotType', i) for i in range(10)):
            cleared = age;break
    assert cleared is not None
    art = []
    for age in [0, 4, 8, 12]:
        q.set('RgShotType', 3, 9);q.set('RgShotAge', age, 9)
        q.put(RgSlot=9, XgShotAim=0)
        q.invoke('ExpandedWeaponPointer')
        ptr = q.get('R0') + 256 * q.get('R1')
        art.append(dict(age=age, record=ptr, actual_bytes=list(q.m[ptr:ptr + 10])))
    hooks = dict(RgAllocationStore={k: alloc[k] for k in ['address', 'bank', 'bytes']},
                 RgFireRequestStore={k: fire[k] for k in ['address', 'bank', 'bytes']})
    n = 'ExpandedEnemyHit'
    hooks[n] = dict(address=address(bundle, n), bank=(location(bundle, n) - 16) // 8192,
                    bytes=list(bundle['raw'][location(bundle, n):location(bundle, n) + 3]))
    q = Arena(bundle, char=8)
    q.put(MarioVariant=1, MmBulletType=30, MmSlot=0, RgSlot=9)
    q.set('RgShotType', 3, 9)
    c, _ = q.invoke('ExpandedEnemyHit', x=0)
    assert not c.p & 1 and q.get('RgEnemyStun') == 12
    output.mkdir()
    put(output / 'proof.json', dict(passed=True, source_CPU_only=True, native_executed=False,
        ROM_sha256=SHA, actual_dispatcher_controls=requests, genuine_store_hooks=hooks,
        pool_size=10, active_limit=2, actual_two_shot_counts=counts,
        actual_source_clear_after_no_new_input=cleared, bridge_type=30, source_contact_admits_damage=True,
        source_fire_request=dict(queue='Square1SoundQueue', value=address(bundle, 'Sfx_Fireball')),
        source_art_records=art, contact_scope='ExpandedEnemyHit is admitted after real MegaManWeapons enemy collision; source component proves its type30 admission only, not collision geometry',
        lifetime='Type3 integrates gravity/terrain, is killed after side terrain, consumed shared enemy hit, viewport X bounds or Y>=240; all ten slots must be zero after native drain.',
        scope='Isolated actual compiled dispatch/pool/lifetime/art/admission controls, no natural enemy/PPU/IRQ/audio waveform result. Store keys are observer metadata, not invented callable game labels.'))
    return hooks


def observer_controls(folder, module, bundle, rom, output):
    sys.path.insert(0, str(D / 'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime
    cfg = get(folder / 'configuration.json');C = cfg['item']
    labels, banks = symbols(bundle, rom)
    checks = []
    for kind in ['valid', 'foreign-bank', 'empty-pool', 'foreign-type', 'inactive-enemy', 'no-contact', 'unowned-allocation', 'wrong-opcode']:
        rt = runtime(LuaRuntime, labels, banks)
        rt.execute('ROSTER_CONFIG=' + lua(cfg['roster']) + ';MARIO_FLOWER_CONFIG=' + lua(C))
        rt.execute(module.read_text())
        rt.execute("emu.addMemoryCallback=function()error('Runtime registration forbidden')end;emu.removeMemoryCallback=function()error('Runtime removal forbidden')end")
        m = rt.globals().mem;st = rt.globals().state
        for n, v in dict(OperMode=1, OperMode_Task=3, GameEngineSubroutine=8, SelectedCharacter=8, MarioVariant=1, CrossoverBehaviorVersion=0).items():
            m[labels[n]] = v
        rt.execute('runevents(emu.eventType.endFrame)')
        def event(name):
            h = C['hooks'][name]
            rt.globals().testBank = h['bank']
            rt.execute('emu.convertAddress=function(a)return{address=testBank*8192+a%8192}end')
            for i, v in enumerate(h['bytes']):m[h['address'] + i] = v
            rt.globals().dispatch(rt.globals().emu.callbackType.exec, h['address'], 0)
        for tier, x in [(1, 336), (2, 1248)]:
            for n, v in dict(PlayerStatus=tier - 1, Enemy_Flag=1, Enemy_ID=0x2e, Enemy_State=128, Enemy_X_Position=x % 256, Enemy_PageLoc=x // 256, PowerUpType=tier - 1).items():
                m[labels[n] + (5 if n.startswith('Enemy_') or n == 'PowerUpType' else 0)] = v
            st['cpu.x'] = 5
            event('PwrUpJmp');event('MarioSourcePowerupCollision')
            m[labels['GuestPowerupActive']] = 1;m[labels['GuestPowerupTarget']] = tier
            for age in range(60):
                m[labels['GuestPowerupAge']] = age;event('GuestPowerupUpdate')
            m[labels['GuestPowerupActive']] = 0;m[labels['PlayerStatus']] = tier
        st['cpu.x'] = 9;st['cpu.a'] = 3
        if kind != 'unowned-allocation':event('RgAllocationStore')
        m[labels['RgShotType'] + 9] = 3
        if kind == 'unowned-allocation':
            try:rt.globals().dispatch(rt.globals().emu.callbackType.write, labels['RgShotType'] + 9, 3)
            except Exception as e:assert 'genuine compiled store' in str(e);checks.append(dict(kind=kind, rejected=True));continue
            raise AssertionError('Unowned allocation admitted')
        rt.globals().dispatch(rt.globals().emu.callbackType.write, labels['RgShotType'] + 9, 3)
        st['cpu.a'] = C['sfx']['fire'];event('RgFireRequestStore')
        rt.globals().dispatch(rt.globals().emu.callbackType.write, labels['Square1SoundQueue'], C['sfx']['fire'])
        for n, v in dict(RgSlot=9, MmSlot=0, MmBulletType=30, Enemy_Flag=1, Enemy_ID=6, Enemy_State=0).items():m[labels[n]] = v
        st['cpu.x'] = 0
        if kind == 'empty-pool':m[labels['RgShotType'] + 9] = 0
        if kind == 'foreign-type':m[labels['MmBulletType']] = 31
        if kind == 'inactive-enemy':m[labels['Enemy_Flag']] = 0
        if kind in ['foreign-bank', 'wrong-opcode']:
            h = C['hooks']['ExpandedEnemyHit']
            rt.globals().testBank = h['bank'] + int(kind == 'foreign-bank')
            rt.execute('emu.convertAddress=function(a)return{address=testBank*8192+a%8192}end')
            for i, v in enumerate(h['bytes']):m[h['address'] + i] = v
            if kind == 'wrong-opcode':m[h['address']] = (h['bytes'][0] + 1) % 256
            try:rt.globals().dispatch(rt.globals().emu.callbackType.exec, h['address'], 0)
            except Exception as e:assert kind == 'wrong-opcode' and 'Actual source owner' in str(e);checks.append(dict(kind=kind, rejected=True));continue
        elif kind != 'no-contact':event('ExpandedEnemyHit')
        rt.globals().MARIO_FLOWER_FINISH()
        raw = rt.eval('table.concat(texts[' + lua(cfg['roster']['out'] + 'flower-component.json') + '])')
        result = json.loads(raw)
        assert result['enemy_contacts'] == int(kind == 'valid') and result['shots'] == 1 and result['source_fire_requests'] == 1
        checks.append(dict(kind=kind, observed_enemy_contacts=result['enemy_contacts'], allocations=1, source_fire_requests=1,
                           mock_only=True, generated_native_executed_field_not_used=True))
    output.mkdir()
    put(output / 'proof.json', dict(passed=True, native_executed=False, source_mock_only=True,
        controls=checks, genuine_positive_and_foreign_empty_no_contact_rejections=True,
        runtime_callback_mutation_forbidden=True, scope='Exact observer under synthetic API/RAM/source-owner events only. No injected-state native claim.'))


def main():
    p = argparse.ArgumentParser(description=__doc__);p.add_argument('--output', type=Path, required=True);a = p.parse_args()
    out = a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True, exist_ok=False)
    rom = SOURCE / 'candidate.nes';assert sha(rom) == SHA
    failure = OLD / 'failure-freeze-v1/proof.json'
    assert sha(failure) == '0b53208063a6eaa8cbe424ea3b7abeea43da48c5a55130275f05a3810e6c9c9d'
    prior = get(failure);assert prior['native_passed'] is False
    for f, h in prior['bindings'].items():assert sha(f) == h, f
    b = load(rom);folder = out / 'luigi-easy';folder.mkdir();(folder / 'frames').mkdir()
    old = ROOT / 'tools/audit/luigi_flower731_native_v1.lua';module = ROOT / 'tools/audit/luigi_flower731_native_v2.lua'
    before = old.read_text();after = module.read_text()
    begin = before.split('function MARIO_FLOWER_RIGHT_CONTROL(c)', 1)[1].split(" if age>=45", 1)[0]
    assert begin == after.split('function MARIO_FLOWER_RIGHT_CONTROL(c)', 1)[1].split(" if age>=45", 1)[0]
    assert "age>=45 and rgInactive()" in after and "age=age+1;assert(age<500,'Bounded actual fireball use and release')" in after
    (out / 'Rg-owner-only.diff').write_text(''.join(difflib.unified_diff(before.splitlines(keepends=True), after.splitlines(keepends=True), fromfile=old.name, tofile=module.name)), encoding='utf-8', newline='\n')
    hooks = owner_controls(b, out / 'source-owner-controls-v1')
    parent = OLD / 'luigi-easy';cfg0 = get(parent / 'configuration.json');cfg = dict(cfg0['roster'])
    cfg.update(out=folder.as_posix() + '/', policy=(folder / 'policy.lua').as_posix(), audit=(folder / 'audit.lua').as_posix())
    item = dict(cfg0['item']);item['hooks'] = {n: cfg0['item']['hooks'][n] for n in ['PwrUpJmp', 'MarioSourcePowerupCollision', 'GuestPowerupUpdate']}
    item['hooks'].update(hooks)
    item['ram'] = dict(item['ram']) | {n: address(b, n) for n in ['RgShotType', 'RgSlot', 'MmSlot', 'MmBulletType']}
    put(folder / 'configuration.json', dict(roster=cfg, item=item))
    for n in ['policy.lua', 'harness.lua', 'audit.lua']:
        shutil.copyfile(parent / n, folder / n);assert sha(parent / n) == sha(folder / n)
    script = 'ROSTER_CONFIG=' + lua(cfg) + '\nMARIO_FLOWER_CONFIG=' + lua(item) + '\ndofile(' + lua(module.as_posix()) + ')\ndofile(' + lua((folder / 'harness.lua').as_posix()) + ')\nassert(MARIO_POWERUP_INSTALL_CHR_DISPATCHER)()\n'
    (folder / 'run.lua').write_text(script, encoding='utf-8', newline='\n')
    assert not re.search(r'\bemu\.(?:write\w*|setState|loadSavestate|reset)\s*\(', script + after + ''.join((folder / n).read_text() for n in ['policy.lua', 'harness.lua', 'audit.lua']))
    observer_controls(folder, module, b, rom, out / 'observer-owner-controls-v1')
    controller_controls(folder, module, b, rom, out / 'controller-source-controls-v1')
    static = [sys.executable, '-B', str(ROOT / 'tools/audit/mario_powerups_current3cee_static_v2.py'), '--fixture', str(folder), '--rom', str(rom), '--lua-root', str(D / 'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1'), '--output', str(out / 'startup-static-v1')]
    z = subprocess.run(static, cwd=ROOT, capture_output=True, text=True);(out / 'static-host.log').write_text(z.stdout + z.stderr)
    assert z.returncode == 0, z.stderr
    env = get(OLD / 'readiness.json')['environment']
    for n in ['emulator', 'core', 'worker_settings', 'user_settings']:assert sha(env[n]) == env[n + '_sha256']
    report = ROOT / 'docs/qa/luigi-flower731-Rg-preparation-2026-10-26.txt'
    deps = {Path(__file__), old, module, report, failure, rom, rom.with_suffix('.dbg'), rom.with_suffix('.lbl')}
    deps |= {Path(f) for f in prior['bindings']};deps |= {f for f in out.rglob('*') if f.is_file()}
    command = [sys.executable, '-B', str(ROOT / 'tools/audit/run_mesen_isolated.py'), '--output', str(folder), '--emulator', env['emulator'], str(folder / 'run.lua'), str(rom), '--timeout', '180'] + ['--option=' + v for v in env['deterministic_command_overrides']]
    ready = dict(passed=True, status='PREPARE_DO_NOT_RUN', native_executed=False, native_grant=False, native_workers=1, ROM_sha256=SHA, environment=env,
        profiles=[dict(name='luigi-easy', character=8, variant=1, mode=0, fixture=str(folder), command=command, limit_physical_frames=6500,
                       endpoint='Genuine two pickups/120growth, source-owned Rg3 live enemy contact, source fire request,45neutral and all ten slots inactive')],
        bindings={str(f): sha(f) for f in sorted(deps, key=str)}, controller_and_all_prior_physical_injury_mode_growth_motion_CHR_guards_unchanged=True,
        original_wrong_owner_native_FALSE_unchanged=True, actual_projectile_owner='RgShotType3/ten slots/max2; bridge30/ExpandedEnemyHit',
        scope='One corrected source-supported LuigiEasy attempt prepared; no new native/contact/drain/art/waveform/fullroute result.')
    put(out / 'readiness.json', ready)
    put(out / 'command.json', dict(not_executed=True, explicit_new_ROOT_grant_required=True,
        command=[sys.executable, '-B', str(ROOT / 'tools/audit/luigi_flower731_run_v1.py'), '--packet', str(out), '--expected-readiness-sha256', sha(out / 'readiness.json'), '--native-grant']))
    print(json.dumps(dict(passed=True, native_executed=False, bindings=len(ready['bindings']), readiness_sha256=sha(out / 'readiness.json'), command_sha256=sha(out / 'command.json')), indent=2))


if __name__ == '__main__':main()
