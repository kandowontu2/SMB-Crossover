"""Explicit compiled query arenas, not controller traversal or full calcAxis."""
from pathlib import Path
import hashlib
import itertools
import json
import re
import sys
import traceback

R = Path(__file__).resolve().parents[2]
sys.path.append('C:/Users/kando/AppData/Local/Programs/Python/Python314/Lib/site-packages')
sys.path.insert(0, str(R / 'tools/audit'))
from verify_native_relocation import load

P = R / 'build/verification/bass-corner-kh'
O = P / 'check-kr'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists()
    O.mkdir()
    report = dict(status='RUNNING', scope=__doc__, installed=False, goal_complete=False, mappers={})
    try:
        for mapper, build in (('mmc3', 'build-ko-mmc3'), ('mmc5', 'build-kq-mmc5')):
            rom = P / build / f'smb-crossover-{mapper}.nes'
            baseline = R / 'build/checkpoints/rygar-walk-kb/build' / rom.name
            new, n = load(rom)
            old, o = load(baseline)
            # Compare all former public names and values, not only RAM.
            def public(path):
                out = set()
                for line in path.with_suffix('.dbg').read_text().splitlines():
                    if not line.startswith('sym\t'):
                        continue
                    f = dict(re.findall(r'(\w+)=("[^"]*"|[^,]+)', line.split('\t', 1)[1]))
                    if f.get('scope') == '1' and 'val' in f and 'seg' in f:
                        out.add((f['name'], int(f['val'], 0)))
                return out
            assert public(baseline) <= public(rom), public(baseline) - public(rom)
            a, b = baseline.read_bytes(), rom.read_bytes()
            changed = sorted({(i - 16) // 8192 for i in range(16, 16 + 512*1024) if a[i] != b[i]})
            assert changed == [5, 63], changed
            assert a[:16] == b[:16] and a[16+512*1024:] == b[16+512*1024:]

            def reset(cpu, l, char, area, y, fy, upper, px=97):
                m = cpu.memory
                m[:2048] = [0]*2048
                m[0x6000:0x8000] = [0]*8192
                m.switch(3)
                m[l['__SMCCODE_RUN__']:l['__SMCCODE_RUN__']+len(m.smc)] = m.smc
                for name, value in (
                    ('CurrentBank', 3), ('SelectedCharacter', char), ('AreaType', area),
                    ('OperMode', 1), ('GameEngineSubroutine', 8), ('Player_Y_HighPos', 1),
                    ('Player_X_Position', px), ('Player_PageLoc', 0), ('Player_Y_Position', y),
                    ('MmYFraction', fy & 255), ('MmYFraction+1', fy >> 8),
                    ('Local_eb', upper), ('R0', 1 if upper == 35 else 2)):
                    if name.endswith('+1'):
                        m[l[name[:-2]]+1] = value
                    else:
                        m[l[name]] = value
                if 'BankShadow' in l:
                    m[l['BankShadow']] = 0x47

            def tile(cpu, l, x, y, value):
                assert 32 <= y < 240
                cpu.memory[l['Block_Buffer_1'] + (x // 16) + (y & 240) - 32] = value

            def call(cpu, l, name, index):
                cpu.a, cpu.x, cpu.y, cpu.p = 0xa5, 0x71, index, 0x25
                cpu.sp = 0xed
                cpu.stPushWord(0x5cff)
                cpu.pc = l[name]
                cpu.processorCycles = 0
                instructions = 0
                while cpu.pc != 0x5d00:
                    cpu.step()
                    instructions += 1
                    assert instructions < 10000, hex(cpu.pc)
                assert cpu.sp == 0xed
                return (cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp), cpu.processorCycles

            counts = dict(legacy_queries=0, original_nonempty_queries=0, added_bottom_queries=0, sophia_heads=0)
            cycle_costs = []
            # Every legacy character, behavior-independent visible Y, all four
            # native standing side points and all level types. Bass water lower
            # points are the sole intended changed terrain-cell result.
            for char, area, y, index in itertools.product(range(13), range(4), (32, 53, 79, 112, 176, 207), (33, 34, 35, 36)):
                for cpu, l in ((old, o), (new, n)):
                    reset(cpu, l, char, area, y, 0, index if index & 1 else index-1)
                    # Empty geometry makes old scratch results deterministic.
                rb, cb = call(old, o, 'CrossoverSourceSideProbe', index)
                ra, ca = call(new, n, 'CrossoverSourceSideProbe', index)
                assert ra[:3] == rb[:3], (char, area, y, index, rb, ra)
                for name in ('Player_X_Position', 'Player_PageLoc', 'Player_Y_Position', 'Player_Y_HighPos', 'MmVX', 'MmVY'):
                    assert new.memory[n[name]:n[name]+1] == old.memory[o[name]:o[name]+1], name
                assert new.memory[0x300:0x7ff] == old.memory[0x300:0x7ff]
                if char != 9 or area or index & 1:
                    assert new.memory[:0x100] == old.memory[:0x100], ('legacy scratch', char, area, y, index)
                    counts['legacy_queries'] += 1
                cycle_costs.append(ca-cb)

            # Actual missing-cell geometry: original lower pixel24 and final
            # interior pixel31/32 must occupy different genuine buffer rows.
            for px, y, fy, index in itertools.product((0, 15, 97, 239), range(32, 208), (0, 1, 0x7fff, 0xffff), (34, 36)):
                xpoint = px + (1 if index == 34 else 14)
                if xpoint >= 256:
                    continue
                lower = y + 31 + bool(fy)
                if lower >= 240 or (lower & 240) == ((y+24) & 240):
                    continue
                for cpu, l in ((old, o), (new, n)):
                    reset(cpu, l, 9, 0, y, fy, index-1, px)
                    tile(cpu, l, xpoint, lower, 105)
                oldregs, _ = call(old, o, 'CrossoverSourceSideProbe', index)
                newregs, _ = call(new, n, 'CrossoverSourceSideProbe', index)
                assert oldregs[0] == 0 and newregs[:3] == (105, 0, index), (px, y, fy, index, oldregs, newregs)
                assert new.memory[n['R2']] == (lower & 240)-32
                assert new.memory[n['R3']] == 105
                assert new.memory[n['R4']] == px & 15
                assert old.memory[0x300:0x7ff] == new.memory[0x300:0x7ff]
                counts['added_bottom_queries'] += 1
                # A pre-existing lower contact must win; do not replace its
                # tile/pointer with any newly sampled block below it.
                for cpu, l in ((old, o), (new, n)):
                    reset(cpu, l, 9, 0, y, fy, index-1, px)
                    tile(cpu, l, xpoint, y+24, 0x61)
                    tile(cpu, l, xpoint, lower, 105)
                rb, _ = call(old, o, 'CrossoverSourceSideProbe', index)
                ra, _ = call(new, n, 'CrossoverSourceSideProbe', index)
                assert ra[:3] == rb[:3] and ra[0] == 0x61
                assert new.memory[:0x100] == old.memory[:0x100]
                counts['original_nonempty_queries'] += 1

            # Shared resident head-call producer still dispatches both actual
            # Sophia head rows to the original head routine, not its side probe.
            for index, y, fy in itertools.product((30, 65), (32, 53, 80, 176), (0, 1, 0x8000, 0xffff)):
                for cpu, l in ((old, o), (new, n)):
                    reset(cpu, l, 11, 1, y, fy, index)
                rb, _ = call(old, o, 'SophiaSourceHeadTail', index)
                ra, _ = call(new, n, 'SophiaSourceHeadTail', index)
                assert ra == rb, ('Sophia head', index, y, fy, rb, ra)
                assert new.memory[:0x100] == old.memory[:0x100]
                assert new.memory[0x300:0x7ff] == old.memory[0x300:0x7ff]
                counts['sophia_heads'] += 1
            report['mappers'][mapper] = dict(ROM_sha256=sha(rom), changed_PRG_banks=changed,
                original_public_addresses_and_CHR_unchanged=True, counts=counts,
                empty_query_added_cycles=[min(cycle_costs), max(cycle_costs)])
        report['status'] = 'PASS_EXPLICIT_COMPILED_QUERY_ARENAS'
    except Exception as exc:
        report.update(status='FAIL_RETAINED', error=repr(exc), traceback=traceback.format_exc())
        raise
    finally:
        (O/'summary.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['status'], report['mappers'])


if __name__ == '__main__':
    main()
