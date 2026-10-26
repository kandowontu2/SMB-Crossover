"""Finite assembled emitter/full-caller/interrupt qualification; no native run."""
from pathlib import Path
from collections import Counter
import argparse, hashlib, itertools, json, traceback
from check_tmnt_render_oa import address, location
from link_pit_rygar_sophia_audit_cpu import Arena, scoped_load
from verify_native_relocation import NesMPU

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2) + '\n', encoding='utf-8')


def prepare(bundle, char, bank, pointer, origin, cursor, rotation, active, attr):
    q = Arena(bundle, char)
    q.m.page(1, 4)
    q.m.page(2, bank)
    q.put(CurrentBank=132, CurrentBankC=bank | 128, CurrentOAMOffset=cursor,
          GuestOamRotationActive=active, RgOamRotation=rotation, R0=pointer & 255,
          R1=pointer >> 8, R3=attr, R4=origin[0], R5=origin[2], R6=origin[1], R7=origin[3])
    start = address(bundle, 'Sprite_Y_Position')
    for i in range(256):
        q.m[start + i] = (i * 73 + 29) & 255
    q.m.writes = []
    return q


def launch(q, name, flags=0x30):
    c = NesMPU(memory=q.m, pc=address(q.b, name))
    c.a, c.x, c.y, c.p, c.sp = 0xa7, 73, 19, flags, 0xfd
    c.stPushWord(0x5aff)
    q.m.writes = []
    return c


def finish(q, c, trace=False):
    pcs = []
    for _ in range(100000):
        if c.pc == 0x5b00:
            break
        if trace:
            pcs.append(c.pc)
        c.step()
    else:
        raise AssertionError(('unbounded emitter/caller', hex(c.pc), q.m.banks))
    assert c.sp == 0xfd
    return dict(regs=[c.a, c.x, c.y, c.p, c.sp], banks=q.m.banks[:], cycles=c.processorCycles,
                writes=[(p, v) for p, v in q.m.writes if not 0x100 <= p < 0x200],
                application=bytes(q.m[:0x100]) + bytes(q.m[0x200:0x8000]), pcs=pcs)


def assert_exact(old, new, label):
    for field in ['regs', 'banks', 'writes', 'application']:
        assert old[field] == new[field], (label, field,
                                        old[field] if field in ['regs', 'banks'] else 'saved in native-free CPU state',
                                        new[field] if field in ['regs', 'banks'] else 'first difference')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prepared', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    try:
        source = json.loads((a.prepared / 'proof.json').read_text())
        assert source['passed'] and source['source_only'] and not source['native_run']
        old, new = [scoped_load(a.prepared / (n + '.nes')) for n in ['baseline', 'candidate']]
        assert sha(a.prepared / 'candidate.nes') == source['candidate_ROM_sha256']
        records = {}
        for side in ['Left', '']:
            lo, hi = [location(old, 'XgSOPHIAWeapon' + side + s) for s in ['Lo', 'Hi']]
            for i in range(53):
                ptr = old['raw'][lo + i] + 256 * old['raw'][hi + i]
                records.setdefault(ptr, []).append(dict(side=side or 'Right', frame=i))
        rows = []
        origins = [(96, 120, 0, 1), (11, 120, 0, 1), (12, 120, 0, 1),
                   (251, 120, 0, 1), (252, 120, 0, 1), (96, 2, 0, 1),
                   (96, 3, 0, 1), (96, 255, 0, 1), (96, 120, 1, 1),
                   (96, 120, 255, 1), (96, 120, 0, 0), (96, 120, 0, 2)]

        def emitter(char, bank, ptr, origin, cursor, rotation, active=1, attr=0, flags=0x30, category='all-records'):
            results = []
            for b, name in [(old, 'MetaspriteRenderLoop'), (new, 'SophiaWaveGate')]:
                q = prepare(b, char, bank, ptr, origin, cursor, rotation, active, attr)
                results.append(finish(q, launch(q, name, flags), trace=True))
            assert_exact(*results, (char, bank, ptr, origin, cursor, rotation, active, attr, flags))
            hot = address(new, 'SophiaWaveLeft') in results[1]['pcs'] or address(new, 'SophiaWaveRight') in results[1]['pcs']
            rows.append(dict(category=category, char=char, bank=bank, pointer=ptr, origin=origin,
                             cursor=cursor, rotation=rotation, active=active, attr=attr, flags=flags,
                             hot=hot, baseline_cycles=results[0]['cycles'], candidate_cycles=results[1]['cycles'],
                             delta=results[1]['cycles'] - results[0]['cycles']))

        for ptr, origin, cursor, rotation in itertools.product(records, origins, [0, 232, 243, 244, 252], [0, 208, 252]):
            emitter(11, 36, ptr, origin, cursor, rotation)
        for ptr, flags, active, rotation in itertools.product([0xc00a, 0xc017], range(256), [0, 1], [0, 252]):
            emitter(11, 36, ptr, (96, 120, 0, 1), 232, rotation, active, flags=flags, category='all-flags')
        for ptr, attr in itertools.product([0xc00a, 0xc017], [1, 3, 4, 0x20, 0xff]):
            emitter(11, 36, ptr, (96, 120, 0, 1), 0, 208, attr=attr, category='nonzero-attr-fallback')
        for family, char in [('PIT', 6), ('RYGAR', 7), ('LUIGI', 8), ('BASS', 9), ('RYU', 10)]:
            for side in ['Right', 'Left']:
                name = 'Xg' + family + 'Weapon0' + side
                at = location(old, name)
                bank, ptr = (at - 16) // 8192, address(old, name)
                for origin, cursor, rotation in itertools.product(origins[:5], [0, 232, 252], [0, 252]):
                    emitter(char, bank, ptr, origin, cursor, rotation, category='foreign-original-record')
        put(a.output / 'emitter-cases.json', rows)
        print(json.dumps(dict(emitter_cases=len(rows), hot=sum(r['hot'] for r in rows))), flush=True)

        caller_rows = []
        for char, shot, counts, modes in [(11, 6, [0, 1, 3, 10], [0, 1, 2]),
                                         (11, 44, [1, 3, 10], [0]), (11, 45, [1, 3, 10], [0]),
                                         (6, 1, [1, 3], [0]), (7, 2, [1], [0]),
                                         (8, 3, [1, 3], [0]), (9, 4, [1, 3], [0]), (10, 5, [1, 3], [0])]:
            for count, mode, cursor, rotation, first in itertools.product(counts, modes, [0, 160, 244], [0, 208], [0, 9]):
                results = []
                for b in [old, new]:
                    q = prepare(b, char, 36, 0xc017, (96, 120, 0, 1), cursor, rotation, 1, 0)
                    q.put(RgDrawFirst=first, XgDiskReach=40)
                    for i in range(count):
                        for name, value in dict(RgShotType=shot, RgShotX=96 + i * 8, RgShotPage=1,
                                                RgShotY=120, RgShotYHigh=1, RgShotDir=1,
                                                RgShotAge=12, RgShotImpact=0, XgShotAim=0,
                                                SsMode=mode, RgShotVXHi=3, RgShotVYHi=0).items():
                            q.set(name, value, i)
                    results.append(finish(q, launch(q, 'ExpandedDrawShots', 0x71)))
                assert_exact(*results, ('whole ExpandedDrawShots', char, shot, count, mode, cursor, rotation, first))
                caller_rows.append(dict(char=char, shot=shot, active_slots=count, mode=mode, cursor=cursor,
                                        rotation=rotation, first=first, baseline_cycles=results[0]['cycles'],
                                        candidate_cycles=results[1]['cycles'], delta=results[1]['cycles'] - results[0]['cycles']))
        put(a.output / 'caller-cases.json', caller_rows)
        print(json.dumps(dict(full_caller_cases=len(caller_rows))), flush=True)

        interrupt_rows = []
        smc = [address(new, n) + 1 for n in ['NextBank_SMC', 'SafecallA_SMC', 'SafereturnA_SMC', 'FarcallJmpTarget_SMC']] + [address(new, 'FarcallJmpTarget_SMC') + 2]
        for ptr, origin, cursor in [(0xc017, (96, 120, 0, 1), 0), (0xc00a, (96, 120, 0, 1), 232),
                                    (0xc017, (11, 120, 0, 1), 0), (0xc017, (96, 120, 0, 1), 244)]:
            def setup():
                q = prepare(new, 11, 36, ptr, origin, cursor, 208, 1, 0)
                q.put(NmiDisable=255, DisableScreenFlag=0, InvHudActive=0, VRAM_Buffer_AddrCtrl=0,
                      Mirror_PPUCTRL=0xa0, Sprite0HitDetectFlag=1)
                return q, launch(q, 'SophiaWaveGate', 0x30)
            q, c = setup()
            expected = finish(q, c, trace=True)
            for kind in ['nmi', 'irq']:
                for boundary in range(len(expected['pcs'])):
                    q, c = setup()
                    for _ in range(boundary):
                        c.step()
                    pc, sp, regs = c.pc, c.sp, (c.a, c.x, c.y, c.p)
                    saved = ([q.m[x] for x in smc], q.get('CurrentBank'), q.get('CurrentBankC'), q.m.banks[:])
                    getattr(c, kind)()
                    for step in range(60000):
                        if c.pc == pc and c.sp == sp:
                            break
                        c.step()
                    else:
                        raise AssertionError(('interrupt timeout', kind, boundary, hex(c.pc)))
                    assert step > 0 and (c.a, c.x, c.y, c.p) == regs
                    assert saved == ([q.m[x] for x in smc], q.get('CurrentBank'), q.get('CurrentBankC'), q.m.banks[:])
                    resumed = finish(q, c)
                    assert resumed['regs'] == expected['regs'] and resumed['banks'] == expected['banks']
                    start = address(new, 'Sprite_Y_Position')
                    assert bytes(q.m[start:start + 256]) == expected['application'][0x100:0x200]
                    for name in ['R0', 'R1', 'R3', 'R4', 'R5', 'R6', 'R7', 'CurrentOAMOffset']:
                        at = address(new, name)
                        i = at if at < 0x100 else at - 0x100
                        assert q.m[at] == expected['application'][i]
                    interrupt_rows.append(dict(pointer=ptr, origin=origin, cursor=cursor, kind=kind, boundary=boundary,
                                               PC=pc, SP=sp, foreground_AXYP_5SMC_actual_banks_restored=True))
        put(a.output / 'interrupt-cases.json', interrupt_rows)
        categories = {}
        for category in sorted(set(r['category'] for r in rows)):
            selected = [r for r in rows if r['category'] == category]
            categories[category] = dict(cases=len(selected), hot=sum(r['hot'] for r in selected),
                                        min_delta=min(r['delta'] for r in selected), max_delta=max(r['delta'] for r in selected))
        proof = dict(passed=True, source_only=True, native_run=False, adopted=False,
                     baseline_ROM_sha256=sha(a.prepared / 'baseline.nes'), candidate_ROM_sha256=sha(a.prepared / 'candidate.nes'),
                     unique_original_Sophia_weapon_records=len(records), original_table_entries=106,
                     actual_emitter_cases=len(rows), categories=categories,
                     hot_cycle_delta=dict(min=min(r['delta'] for r in rows if r['hot']), max=max(r['delta'] for r in rows if r['hot'])),
                     full_ExpandedDrawShots_cases=len(caller_rows), full_caller_cycle_delta=dict(min=min(r['delta'] for r in caller_rows), max=max(r['delta'] for r in caller_rows)),
                     interrupt_cases=len(interrupt_rows), NMI_cases=sum(r['kind'] == 'nmi' for r in interrupt_rows),
                     IRQ_cases=sum(r['kind'] == 'irq' for r in interrupt_rows), all_AXYP_SP_nonstack_RAM_ordered_writes_banks_exact=True,
                     resumed_foreground_AXYP_SP_5SMC_C_and_A_banks_exact=True,
                     files={name: sha(a.output / name) for name in ['emitter-cases.json', 'caller-cases.json', 'interrupt-cases.json']},
                     tool_sha256=sha(__file__),
                     limits='Finite synthetic assembled production emitter/caller states and compiled lag-NMI/IRQ boundaries only. No native timing, DMC worst-case, frame cadence, reduced scanline demand, starvation repair or visibility improvement claim. All OAM tuples and their fairness are intentionally identical.')
        put(a.output / 'proof.json', proof)
        print(json.dumps(proof, indent=2))
    except BaseException as error:
        put(a.output / 'failure.json', dict(passed=False, source_only=True, native_run=False, error=repr(error),
                                           traceback=traceback.format_exc(), tool_sha256=sha(__file__)))
        (a.output / 'failed-tool.py').write_bytes(Path(__file__).read_bytes())
        raise


if __name__ == '__main__':
    main()
