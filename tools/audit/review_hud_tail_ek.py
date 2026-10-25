"""Replay captured HUD calls exactly and check their real GameLoop consumers."""
from pathlib import Path
import collections
import argparse
import hashlib
import importlib.util
import json
import struct
import traceback

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
O = V / 'hud-tail-callers-ev'
P = V / 'agent49-samus-bill-arsenal-a/palette_native_model_cu.py'
spec = importlib.util.spec_from_file_location('hud_ek_model', P)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
helper_spec = importlib.util.spec_from_file_location('hud_ek_queues', R / 'tools/audit/check_hud_tail_ec.py')
h = importlib.util.module_from_spec(helper_spec)
helper_spec.loader.exec_module(h)


class CPU(m.q.core.NesMPU):
    cycletime = list(m.q.core.NesMPU.cycletime)
    cycletime[0xce] = 6


m.q.core.NesMPU = CPU


class Tracked(m.Bus):
    def __init__(self, *args):
        super().__init__(*args)
        self.written = set()
        self.first_reads = {}

    def __getitem__(self, ad):
        physical = ad & 0x7ff if ad < 0x2000 else ad
        if physical not in self.written:
            self.first_reads.setdefault(physical, (self.pc, self.op))
        return super().__getitem__(ad)

    def write(self, ad, physical, value):
        self.written.add(physical)
        super().write(ad, physical, value)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def differences(a, b):
    return {m.q.g.RAMS[i] for i, (v, w) in enumerate(zip(a, b)) if v != w}


def suffix(im, q, dirty_y):
    bus = Tracked(im, q['ram'], q['banks'], ())
    cpu = CPU(memory=bus)
    cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp, cpu.pc = q['regs']
    target = im.hook('PauseSkip', 'GameLoop')['address']
    first_y = None
    for steps in range(60000):
        if cpu.pc == target:
            break
        bus.pc = cpu.pc
        bus.op = bus.data[cpu.pc]
        mnemonic, mode = cpu.disassemble[bus.op]
        if dirty_y:
            assert mnemonic not in ('STY', 'TYA', 'INY', 'DEY', 'CPY') and mode not in ('aby', 'iny', 'zpy'), ('Y consumed before replacement', hex(cpu.pc), mnemonic, mode)
            if mnemonic in ('LDY', 'TAY', 'PLY'):
                dirty_y = False
                first_y = dict(PC=cpu.pc, opcode=bus.op, mnemonic=mnemonic)
        popped = bus.data[0x100+((cpu.sp+1)&255)] if bus.op in (0x28, 0x40) else None
        cpu.step()
        if popped is not None:
            cpu.p = popped & 0xcf
    else:
        raise AssertionError('Bounded actual GameLoop suffix')
    assert not dirty_y
    return dict(regs=[cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp, cpu.pc], ram=bus.ram(), banks=bus.banks,
                selector=bus.selector, ports=bus.ports, trace=bus.trace, first_reads=bus.first_reads, first_y=first_y, steps=steps)


def unused_x(im, q):
    """Follow the actual parent, then check the next GameLoop's input contract."""
    def first_replacement(pc, stop_at_idle):
        bus = Tracked(im, q['ram'], q['banks'], ())
        cpu = CPU(memory=bus)
        cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp, cpu.pc = q['regs']
        cpu.pc = pc
        idle = im.hook('IdleLoop')['address']
        for steps in range(15000):
            if stop_at_idle and cpu.pc == idle:
                return dict(reaches_idle_without_X_read=True, steps=steps)
            bus.pc = cpu.pc
            bus.op = bus.data[cpu.pc]
            mnemonic, mode = cpu.disassemble[bus.op]
            assert mnemonic not in ('STX','TXA','CPX','INX','DEX') and mode not in ('abx','inx','zpx'), ('End-frame X read before replacement', hex(cpu.pc), mnemonic, mode)
            if mnemonic in ('LDX','TAX','TSX'):
                return dict(first_replacement=dict(PC=cpu.pc, opcode=bus.op, mnemonic=mnemonic), steps=steps)
            popped = bus.data[0x100+((cpu.sp+1)&255)] if bus.op in (0x28,0x40) else None
            cpu.step()
            if popped is not None:
                cpu.p = popped & 0xcf
        raise AssertionError('Bounded next-consumer X proof')
    return dict(actual_parent=first_replacement(q['regs'][5], True),
                next_GameLoop_input=first_replacement(im.hook('GameLoop')['address'], False),
                qualification='The second phase proves the GameLoop input contract on this attained state, not a manufactured controller transition. Balanced ISR handling is tested separately.')


def isr_x_contract(im, events, raw, hardware):
    """Run actual compiled leaf ISRs with every incoming X value."""
    groups = []
    chosen = set()
    records = {}
    for e in events:
        if e['event'] in ('isr-entry','isr-pre-RTI'):
            records.setdefault((e['name'],e['id']), {})[e['event']] = e
    for (name, ident), pair in records.items():
        if name in chosen or set(pair) != {'isr-entry','isr-pre-RTI'}:
            continue
        e, z = pair['isr-entry'], pair['isr-pre-RTI']
        if any(v['event']=='isr-entry' and e['cycle']<v['cycle']<z['cycle'] for v in events):
            continue
        initial = m.snapshot(raw,e)
        final = m.snapshot(raw,z)
        sp = e['SP']
        target = initial[0x100+((sp+2)&255)] + 256*initial[0x100+((sp+3)&255)]
        restored_p = initial[0x100+((sp+1)&255)] & 0xcf
        banks = {ad:e[n] for ad,n in ((0x8000,'bank8'),(0xa000,'bankA'),(0xc000,'bankC'),(0xe000,'bankE'))}
        reads = [v for v in hardware if e['cycle']<v['cycle']<z['cycle']]
        baseline = None
        for x in range(256):
            q = m.execute(im,initial,[e['A'],x,e['Y'],e['P'],sp],banks,e['PC'],target,(sp+3)&255,hardware=reads)
            assert q['regs']==[e['A'],x,e['Y'],restored_p,(sp+3)&255,target]
            assert q['banks']==banks
            if baseline is None:
                baseline=q
            else:
                dead = {ad for pc,op,ad0,ad,value in q['trace']+baseline['trace'] if 0x100<=ad<=0x100+sp and op in (0x08,0x48,0x20)}
                assert differences(q['ram'],baseline['ram']) <= dead, ('ISR incoming X affects live memory',name,x)
                assert q['selector']==baseline['selector']
                for port in set(q['ports']) | set(baseline['ports']):
                    if q['ports'].get(port)==baseline['ports'].get(port):
                        continue
                    # MMC3 IRQ disable acknowledges on any data byte. The
                    # unchanged handler's PHX leaves incoming X in A before
                    # STA $E000. Bind this one ignored-data register write to
                    # its actual compiled producer, retaining both raw traces.
                    assert im.mapper==4 and name=='IRQ' and port==0xe000
                    ack_pc=im.hook('IrqScrollSplit')['address']+3
                    for result in (q,baseline):
                        ack=[v for v in result['trace'] if v[2]==0xe000]
                        assert len(ack)==1 and ack[0][0]==ack_pc and ack[0][1]==0x8d
            if x==e['X']:
                assert q['ram']==final, 'Actual ISR final RAM before RTI remains exact after RTI'
        chosen.add(name)
        groups.append(dict(name=name, id=ident, native_frame=e['frame'], incoming_X_cases=256,
                           live_RAM_ports_mapper_effect_equal=True, input_X_restored=True,
                           ignored_IRQ_ack_data_source='https://www.nesdev.org/wiki/MMC3#IRQ_disable_($E000-$FFFE,_even)' if name=='IRQ' and im.mapper==4 else None))
    return groups


def main():
    global O
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',type=Path,default=V/'hud-tail-dz/source')
    parser.add_argument('--capture',type=Path,default=V/'hud-tail-native-er')
    parser.add_argument('--tag',default='hud-tail-callers-ev')
    args=parser.parse_args()
    O=V/args.tag
    assert not O.exists()
    O.mkdir()
    report = dict(status='REVIEWING', groups=[], model_sha256=sha(P), source_sha256=sha(__file__),
                  scope='Every captured native call: literal10240RAM, registers, actual attained ISR, hardware reads and ordered writes. Matched noISR old/new calls then execute the actual parent GameLoop suffix, tracking all differing private/scratch/stack cells and changed Y. Queue differences require equal final PPU writes.', goal_complete=False)
    context = None
    try:
        for mapper in ('mmc3', 'mmc5'):
            ims = [m.q.Image(R / f'build/checkpoints/water-visible-cw/build/smb-crossover-{mapper}.nes'), m.q.Image(args.candidate / f'build/smb-crossover-{mapper}.nes')]
            assert ims[0].ram == ims[1].ram
            L = ims[0].ram
            queue_cells = {L['VRAM_Buffer1_Offset']} | set(range(L['VRAM_Buffer1'], L['VRAM_Buffer1']+85))
            for version in ('CW', 'DZ'):
                folder = args.capture / f'{version}-{mapper}'
                binding = json.loads((folder/'binding.json').read_text())
                actual_path=Path(binding['ROM']['rom']['path'])
                if version=='CW' and sha(actual_path)!=binding['ROM']['rom']['sha256']:
                    actual_path=R/f'build/checkpoints/water-visible-cw/build/smb-crossover-{mapper}.nes'
                actual_im=m.q.Image(actual_path)
                assert sha(actual_im.path) == binding['ROM']['rom']['sha256']
                native = folder / 'native'
                events = [json.loads(line) for line in (native/'caller.jsonl').read_text().splitlines()]
                ram = (native/'caller-ram.bin').read_bytes()
                writes = list(struct.Struct('<HHBIh').iter_unpack((native/'caller-writes.bin').read_bytes()))
                hardware = [json.loads(line) for line in (native/'caller-hardware.jsonl').read_text().splitlines()]
                pairs = {}
                for z in events:
                    if z['event'] in ('entry', 'return'):
                        pairs.setdefault(z['id'], {})[z['event']] = z
                group = dict(mapper=mapper, version=version, calls=[], differing_cells=collections.Counter(),
                             ISR_X_contract=isr_x_contract(actual_im,events,ram,hardware))
                assert {z['name'] for z in group['ISR_X_contract']} == {'NMI','IRQ'}, 'Both real leaf interrupt handlers must be captured'
                report['groups'].append(group)
                for ident, pair in pairs.items():
                    assert set(pair) == {'entry', 'return'}
                    e, z = pair['entry'], pair['return']
                    context = dict(mapper=mapper, version=version, id=ident, frame=e['frame'])
                    before, after = m.snapshot(ram, e), m.snapshot(ram, z)
                    regs = [e[n] for n in ('A', 'X', 'Y', 'P', 'SP')]
                    banks = {ad:e[n] for ad, n in ((0x8000,'bank8'), (0xa000,'bankA'), (0xc000,'bankC'), (0xe000,'bankE'))}
                    interrupts = m.irq_records(events, ram, e, z)
                    reads = [r for r in hardware if e['cycle'] < r['cycle'] < z['cycle']]
                    exact = m.execute(actual_im, before, regs, banks, e['PC'], z['PC'], z['SP'], interrupts=interrupts, hardware=reads)
                    assert exact['regs'] == [z[n] for n in ('A','X','Y','P','SP','PC')], ('native registers', context)
                    assert exact['ram'] == after, ('native allRAM', context)
                    assert [(w[1],w[2]) for w in writes[e['writeCount']:z['writeCount']]] == [(t[2],t[4]) for t in exact['trace']], ('native ordered writes', context)
                    assert exact['banks'] == banks
                    if mapper == 'mmc3':
                        assert exact['selector'] == after[L['BankShadow']]
                    qs = [m.execute(im, before, regs, banks, e['PC'], z['PC'], z['SP']) for im in ims]
                    a, b = qs
                    assert a['regs'][:2]+a['regs'][3:] == b['regs'][:2]+b['regs'][3:], ('public AX/P/SP/PC', context)
                    assert a['banks'] == b['banks'] and a['selector'] == b['selector']
                    assert h.output(h.queue(ims[0], a['ram'])) == h.output(h.queue(ims[1], b['ram']))
                    diff = differences(a['ram'], b['ram'])
                    ss = [suffix(im, q, a['regs'][2] != b['regs'][2]) for im, q in zip(ims, qs)]
                    for s in ss:
                        assert not (diff-queue_cells) & set(s['first_reads']), ('changed input consumed by actual parent', context,
                            [(hex(ad),s['first_reads'][ad]) for ad in (diff-queue_cells)&set(s['first_reads'])])
                    assert ss[0]['regs'][:1]+ss[0]['regs'][2:] == ss[1]['regs'][:1]+ss[1]['regs'][2:], ('parent A/Y/P/SP/PC', context)
                    x_proof = [unused_x(im,s) for im,s in zip(ims,ss)] if ss[0]['regs'][1]!=ss[1]['regs'][1] else None
                    assert ss[0]['banks'] == ss[1]['banks'] and ss[0]['selector'] == ss[1]['selector']
                    assert ss[0]['ports'] == ss[1]['ports'], ('parent hardware port effects', context)
                    assert h.output(h.queue(ims[0], ss[0]['ram'])) == h.output(h.queue(ims[1], ss[1]['ram'])), ('parent queue image', context)
                    final_diff = differences(ss[0]['ram'], ss[1]['ram'])
                    # The same public PCs and all original callsites stay fixed.
                    # Any new non-queue difference in the suffix must be a dead
                    # cell from an actual push, or an explicitly assigned rare
                    # call's result/SMC operand that the next loop overwrites.
                    private = {L[n] for n in ('BillNativeReturnP','BillNativeReturnA','BillNativeReturnSelector')}
                    private |= {L[n]+d for n,d in [('SafecallA_SMC',1),('FarcallJmpTarget_SMC',1),('FarcallJmpTarget_SMC',2),('NextBank_SMC',1),('SafereturnA_SMC',1)]}
                    dead = {ad for s in ss for pc,op,ad0,ad,value in s['trace'] if 0x100 <= ad <= 0x100+z['SP'] and op in (0x08,0x48,0x20)}
                    assert final_diff <= diff | queue_cells | private | dead, ('new parent difference', context, sorted(final_diff-diff-queue_cells-private-dead))
                    group['differing_cells'].update(hex(ad) for ad in diff-queue_cells)
                    group['calls'].append(dict(id=ident, frame=e['frame'], actual_interrupts=len(exact['interrupts']), native_exact=True,
                        matched_cycles=[a['cycles'],b['cycles']], queue_bytes=[len(h.queue(im,q['ram']))-1 for im,q in zip(ims,qs)],
                        changed_input_cells=sorted(diff-queue_cells), dead_through_GameLoop=True, first_y=[s['first_y'] for s in ss],
                        parent_steps=[s['steps'] for s in ss], parent_PPU_image_equal=True, end_frame_X_proof=x_proof))
                print(mapper, version, len(group['calls']), 'calls', sum(z['actual_interrupts'] for z in group['calls']), 'attained ISR', flush=True)
        report['status'] = 'PASS_NATIVE_EXACT_AND_IMMEDIATE_HUD_PARENT_CONSUMERS'
    except Exception as error:
        report.update(status='FAILURE_RETAINED', context=context, error=repr(error), traceback=traceback.format_exc())
        raise
    finally:
        (O/'summary.json').write_text(json.dumps(report, indent=2)+'\n')


if __name__ == '__main__':
    main()
