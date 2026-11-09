"""Assemble the split Mini native lift manager and test exact aa02 in memory."""

import argparse
import json
from pathlib import Path
import subprocess

from check_mini_lift_spawn_1108_v1 import N, PIN, ROM, ROOT, SOURCE, address, bundle, sha


ADMISSION = ROOT / 'tools/reference/mini_lift_admission_1108_v1.s'
SPANS = (
    ('SCAN', 24, 0xbbcf, 49, 0xff),
    ('SCAN_CALL', 24, 0xae6e, 18, 0xff),
    ('SCOPE', 61, 0xb39c, 40, 0xea),
    ('SCOPE_CALL', 61, 0xbfeb, 21, 0xff),
    ('ALLOCATE', 36, 0xb6d0, 48, 0xff),
    ('ALLOCATE_CALL', 36, 0xbfe3, 29, 0xff),
    ('SPAWN', 78, 0xbcc7, 57, 0xff),
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(exist_ok=True)
    rom = ROM.read_bytes()
    assert sha(rom) == PIN
    raw = bytearray(rom)
    cc = ROOT / 'tools/Windows/cc65/bin'
    cfg = out / 'manager.cfg'
    cfg.write_text('MEMORY {\n' + ''.join(
        f'{name}:start=${pc:04x},size={length},file="{(out / (name+".bin")).as_posix()}";\n'
        for name, _, pc, length, _ in SPANS) + '}\nSEGMENTS {\n' + ''.join(
        f'MINI_LIFT_{name}:load={name},type=ro;\n' for name, *_ in SPANS) + '}\n')
    objs = [out / 'spawn.o', out / 'admission.o']
    subprocess.run([cc/'ca65.exe', SOURCE, '-D', 'MINI_LIFT_CHAIN=1', '-o', objs[0]], check=True)
    subprocess.run([cc/'ca65.exe', ADMISSION, '-o', objs[1]], check=True)
    subprocess.run([cc/'ld65.exe', '-C', cfg, *objs, '-o', out/'unused.bin'], check=True)
    placement = []
    for name, bank, pc, length, fill in SPANS:
        data = (out/(name+'.bin')).read_bytes()
        start = 16 + bank * 8192 + pc - 0xa000
        assert len(data) <= length and raw[start:start+length] == bytes([fill])*length
        raw[start:start+len(data)] = data
        placement.append(dict(role=name, bank=bank, pc=pc, bytes=len(data), capacity=length,
                              before=rom[start:start+len(data)].hex(), after=data.hex(),
                              component_SHA256=sha(data)))
    b = bundle(raw)
    for symbol, role in (('MiniLiftTick', 'SCAN'), ('MiniLiftAllocate', 'ALLOCATE'),
                         ('MiniLiftSpawn', 'SPAWN')):
        _, bank, pc, _, _ = next(span for span in SPANS if span[0] == role)
        b['segs'][role] = dict(start=str(pc), ooffs=str(16 + bank * 8192 + pc - 0xa000))
        b['syms'][symbol] = dict(val=str(pc), seg=role)

    m = N.fresh(b)
    N.put(m, SelectedCharacter=41, OperMode=1, FamilyMainCommit=1,
          DisableScreenFlag=1, Mirror_PPUMASK=0, NmiDisable=255, Mirror_PPUCTRL=160)
    N.invoke(m, 'MiniScene')
    N.put(m, OperMode_Task=3, GameEngineSubroutine=8, AreaType=1, AreaAddrsLOffset=5,
          WorldNumber=0, LevelNumber=0, TimerControl=0, CurrentBankC=2, ObjectOffset=4)
    m[0x5116] = 2

    def tick(bus, x):
        N.put(bus, Player_X_Position=x&255, Player_PageLoc=x>>8)
        result = N.invoke(bus, 'MiniLiftTick')
        assert bus.rawtags[2] == 2 and N.get(bus, 'ObjectOffset') == 4
        return result['CPU']

    def actor(bus, slot):
        return tuple(N.get(bus, name, slot) for name in ('Enemy_Flag', 'Enemy_ID', 'Enemy_State',
                     'Enemy_X_Position', 'Enemy_PageLoc', 'Enemy_Y_Position', 'Enemy_BoundBoxCtrl'))

    def lift(bus, x, slot):
        assert actor(bus, slot) == (1, 0x25, 0x40, x&255, x>>8, 192, 5)
        assert bus.ram[2][0x30b] == slot+1

    checks = 0
    native_carry = dict(constructor_clear=0, all_busy_set=0)
    for mode in (0, 1):
        for x in (560, 688, 864):
            for slot in range(6):
                q = N.fork(m)
                N.put(q, CrossoverBehaviorVersion=mode, SecondaryHardMode=mode, Player_PageLoc=x>>8)
                result = N.invoke(q, 'MiniLiftSpawn', a=x&255, x=slot, y=4, p=0x31)
                assert not result['P']&1, (mode, x, slot, result)
                lift(q, x, slot)
                native_carry['constructor_clear'] += 1
        for first, last, x, bit in ((528, 607, 560, 1), (656, 735, 688, 2), (832, 911, 864, 4)):
            for px in (first-1, first, last, last+1):
                q = N.fork(m)
                N.put(q, CrossoverBehaviorVersion=mode, SecondaryHardMode=mode)
                tick(q, px)
                if first <= px <= last:
                    lift(q, x, 5)
                    assert q.ram[2][0x30c] == bit
                else:
                    assert q.ram[2][0x30b:0x30d] == bytes(2)
                checks += 1
        q = N.fork(m)
        N.put(q, CrossoverBehaviorVersion=mode, SecondaryHardMode=mode)
        costs = []
        for slot in range(6):
            q[address(b, 'Enemy_Flag')+slot] = 1
            q[address(b, 'Enemy_ID')+slot] = 6
            q[address(b, 'Enemy_State')+slot] = 0x21
        original = tuple(actor(q, i) for i in range(6))
        result = N.invoke(q, 'MiniLiftAllocate', p=0x30)
        assert result['P']&1, result
        native_carry['all_busy_set'] += 1
        costs.append(tick(q, 552))
        assert tuple(actor(q, i) for i in range(6)) == original
        assert q.ram[2][0x30b:0x30d] == bytes(2)
        q[address(b, 'Enemy_Flag')+2] = 0
        for x, bit in ((560, 1), (688, 3), (864, 7)):
            costs.append(tick(q, x))
            lift(q, x, 2)
            assert q.ram[2][0x30c] == bit
            assert all(actor(q, i) == original[i] for i in range(6) if i != 2)
            q[address(b, 'Enemy_Y_Position')+2] = 139
            costs.append(tick(q, x+9))
            assert N.get(q, 'Enemy_Y_Position', 2) == 139
        checks += 7
        stale = N.fork(q)
        stale.ram[2][0x30c] = 0
        stale[address(b, 'Enemy_ID')+2] = 6
        old = tuple(actor(stale, i) for i in range(6))
        tick(stale, 600)
        assert tuple(actor(stale, i) for i in range(6)) == old
        assert stale.ram[2][0x30c] == 0
        stale[address(b, 'Enemy_Flag')+3] = 0
        tick(stale, 600)
        lift(stale, 560, 3)
        assert actor(stale, 2) == old[2]
        checks += 2
    for name, value in (('SelectedCharacter', 0), ('SelectedCharacter', 40),
                        ('WorldNumber', 1), ('LevelNumber', 1), ('AreaAddrsLOffset', 0)):
        q = N.fork(m)
        N.put(q, **{name: value})
        tick(q, 560)
        assert q.ram[2][0x30b:0x30d] == bytes(2)
        assert all(N.get(q, 'Enemy_Flag', i) == 0 for i in range(6))
        checks += 1

    report = dict(passed=True, source_CPU_only=True, ROM_written=False, parent=PIN,
                  cases=checks, patch_spans=placement, source_hashes={str(f): sha(f.read_bytes())
                  for f in (SOURCE, ADMISSION, Path(__file__))},
                  native_carry=native_carry,
                  last_mode_blocked_spawn_and_repeat_cycles=costs,
                  scope='Exact AA02 CPU-only native constructor/admission. Water-owned tail reallocation, authenticated Mini Main hook, support, route, and interrupt qualification remain open.')
    (out/'proof.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(dict(passed=True, cases=checks, sizes={x['role']:x['bytes'] for x in placement},
                          CPU=costs)))


if __name__ == '__main__':
    main()
