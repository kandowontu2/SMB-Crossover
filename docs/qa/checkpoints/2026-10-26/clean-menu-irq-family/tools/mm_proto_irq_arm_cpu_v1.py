"""Independent complete NMI/IRQ controls for the private IRQ-arm relocation."""
from pathlib import Path
import argparse, hashlib, itertools, json, traceback
import current3cee_postdma_mask_cpu_v4 as H

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(p, data):
    Path(p).write_text(json.dumps(data, indent=2) + '\n')


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(',', ':')).encode()).hexdigest()


OriginalBus = H.Bus
instances = []


class AuditBus(OriginalBus):
    def __init__(self, b, initial, pads=(0xa5, 0x5a)):
        self.IOreads = []
        self.IRQwrites = []
        self.IRQreads = []
        self.in_irq = False
        super().__init__(b, initial, pads)
        self.irq_lo = H.address(b, 'IrqScrollSplit')
        self.irq_hi = self.irq_lo + 68
        instances.append(self)

    def irq_pc(self):
        return self.cpu is not None and self.irq_lo <= self.cpu.pc <= self.irq_hi

    def __getitem__(self, at):
        value = super().__getitem__(at)
        if isinstance(at, int) and 0x2000 <= at < 0x5c00:
            if self.irq_pc():
                self.IRQreads.append((at, value))
            else:
                self.IOreads.append((at, value))
        return value

    def __setitem__(self, at, value):
        super().__setitem__(at, value)
        if isinstance(at, int) and self.irq_pc() and not 0x100 <= at < 0x200:
            self.IRQwrites.append((at, value))


H.Bus = AuditBus


def seed(b, char, oper, lag, blank, reload, packet, sprite):
    q = H.seed(b, char, oper, lag, blank, reload, packet)
    q.put(Sprite0HitDetectFlag=sprite)
    return q


def run(b, q, stall=None, inject=None, trace=False):
    result = H.run(b, q, stall=stall, inject_index=inject, trace=trace)
    bus = instances.pop()
    result['raw_writes'] = [(at, value) for _, at, value in result['stamps']]
    result['IOreads'] = bus.IOreads
    result['IRQwrites'] = bus.IRQwrites
    result['IRQreads'] = bus.IRQreads
    return result


def remove_IRQ(full, irq):
    # IRQ is injected once: its complete write sequence is one contiguous
    # inserted subsequence of the ordered nonstack NMI stream.
    if not irq:
        return full
    starts = [i for i in range(len(full) - len(irq) + 1) if full[i:i + len(irq)] == irq]
    assert len(starts) == 1, ('Unique actual IRQ write insertion', starts, irq)
    i = starts[0]
    return full[:i] + full[i + len(irq):]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--parent', type=Path, required=True)
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    rows, IRQrows, input_rows, timing, defer_rows = [], [], [], [], []
    try:
        assert sha(a.parent / 'candidate.nes') == '2f0d02050cb855b85ca299bb3f5fb7044b6deaf7406412edf27fd0d2bf173afc'
        assert sha(a.candidate / 'candidate.nes') == '08c1b5032a0e1009e3c103eec0a4e27739a82b645310aeb85e83307b9d6ffa4f'
        assert json.loads((a.candidate / 'proof.json').read_text())['passed']
        bs = [H.scoped_load(q / 'candidate.nes') for q in [a.parent, a.candidate]]

        def compare(kind, spec, states, stall=None):
            outputs = [run(b, q, stall) for b, q in zip(bs, states)]
            for field in ['regs', 'ram', 'banks', 'reads', 'IOreads', 'serial']:
                assert outputs[0][field] == outputs[1][field], (kind, spec, field)
            arms = [[w for w in o['raw_writes'] if w[0] in [0x5203, 0x5204]] for o in outputs]
            rest = [[w for w in o['raw_writes'] if w[0] not in [0x5203, 0x5204]] for o in outputs]
            assert arms[0] == arms[1], (kind, spec, 'Arm values/order')
            assert rest[0] == rest[1], (kind, spec, 'All remaining ordered writes', next((i for i,(x,y) in enumerate(zip(rest[0],rest[1])) if x != y), None))
            assert outputs[0]['cycles'] == outputs[1]['cycles'], (kind, spec, 'Total cycles', outputs[0]['cycles'], outputs[1]['cycles'])
            entry = dict(kind=kind, spec=spec, stall_model=stall, cycles=outputs[0]['cycles'], delta=0,
                         complete_ordered_other_writes_sha256=digest(rest[0]), exact_arm_values_order=arms[0],
                         complete_IOreads_sha256=digest(outputs[0]['IOreads']))
            rows.append(entry)
            return outputs

        for sprite, char, oper, lag, blank, reload, packet in itertools.product([0,1], range(24), [0,1], [0,1], [0,1], [0,1], [0,1]):
            compare('complete-NMI', [sprite,char,oper,lag,blank,reload,packet],
                    [seed(b,char,oper,lag,blank,reload,packet,sprite) for b in bs])
        print(json.dumps(dict(complete_NMI=len(rows))), flush=True)
        for sprite, char, oper, lag, reload, stall in itertools.product([0,1], [0,3,11,18,19], [0,1], [0,1], [0,1], [0,1]):
            compare('complete-NMI-DMA-parity', [sprite,char,oper,lag,reload],
                    [seed(b,char,oper,lag,0,reload,1,sprite) for b in bs], stall)
        for sprite, variant, kind, ctrl in itertools.product([0,1], [1,2,3], ['full','attr','new-life','death','capture'], [0,6,4]):
            qs = []
            for b in bs:
                q = H.setup(b,0,variant,3 if kind == 'attr' else 0)
                q.put(InvHudActive=variant*2+1 if kind == 'attr' else 0,Mirror_PPUCTRL=0xa8,Mirror_PPUMASK=30,
                      Sprite0HitDetectFlag=sprite,ReloadCHRBank=1,X5WideChrActive=1,VRAM_Buffer_AddrCtrl=ctrl)
                q.invoke('PnHud')
                if kind == 'new-life': q.invoke('PnHudNewLife')
                if kind == 'death': q.invoke('VvDeathStart')
                if kind == 'capture': q.put(PnBombPaletteReady=0,PnBombCapturePending=1)
                q.array('VRAM_Buffer2',[0x20,0x80,0x81,5,0])
                q.set('VRAM_Buffer2_Offset',4)
                q.set('NmiDisable',0)
                qs.append(q)
            compare('complete-NMI-HUD-lifecycle',[sprite,variant,kind,ctrl],qs)
        assert len(rows) == 1786
        print(json.dumps(dict(complete_NMI=len(rows))), flush=True)
        for buttons, stall in itertools.product(range(256), [0,1]):
            outputs = []
            for b in bs:
                q = seed(b,0,0,0,0,1,0,1)
                m = AuditBus(b,bytes(q.m[:0x8000]),(buttons,buttons^255))
                c = H.NesMPU(memory=m,pc=H.address(b,'OAMandReadJoypad'))
                c.sp=0xfd;c.stPushWord(0x5aff);m.cpu=c;m.writes=[];m.stamps=[]
                while c.pc != 0x5b00:
                    c.step()
                    if m.pending_dma:
                        c.processorCycles += 513 + ((c.processorCycles + stall) & 1)
                        m.pending_dma=False
                instances.pop()
                outputs.append((m[H.address(b,'SavedJoypad1Bits')],m[H.address(b,'SavedJoypad2Bits')],c.a,c.x,c.y,c.p,c.sp,c.processorCycles,H.app(m),m.writes,m.IOreads))
            assert outputs[0] == outputs[1] and outputs[0][0:2] == (buttons,buttons^255)
            input_rows.append(dict(buttons=buttons,DMA_parity_model=stall,all_state_IO_and_cycles_exact=True))
        print(json.dumps(dict(input_cases=len(input_rows))), flush=True)
        # Bound actual real-code scheduling, including the CLI defer boundary.
        # Both regular flag values and the unchanged lag path are included.
        for bi, b in enumerate(bs):
            for char, lag, sprite in itertools.product([0,18], [0,1], [0,1]):
                q = seed(b,char,1,lag,0,1,1,sprite)
                reference = run(b,q,trace=True)
                audio = H.address(b,'AudioUpdate')
                end = next(i for i,(pc,_,_) in enumerate(reference['trace']) if pc == audio)
                trace = reference['trace'][:end]
                arm = [(at,v) for _,at,v in reference['stamps'] if at in [0x5203,0x5204]]
                strobes = [clock for clock,at,_ in reference['stamps'] if at == 0x4016]
                masks = [clock for clock,at,_ in reference['stamps'] if at == 0x2001]
                armclocks = [clock for clock,at,_ in reference['stamps'] if at in [0x5203,0x5204]]
                timing.append(dict(ROM=bi,char=char,lag=lag,Sprite0Flag=sprite,arm_values=arm,arm_clocks=armclocks,
                                   input_strobe_clocks=strobes,mask_write_clocks=masks,AudioUpdate_clock=reference['trace'][end][2]))
                if not lag and sprite:
                    assert arm == [(0x5203,31),(0x5204,128)]
                    assert (armclocks[-1] > strobes[-1]) == (bi == 1)
                    assert armclocks[-1] < reference['trace'][end][2]
                for index,(pc,flags,clock) in enumerate(trace):
                    if flags & 4:
                        continue
                    was_cli = index > 0 and bool(trace[index-1][1] & 4)
                    if was_cli:
                        prior = trace[index-1][0]
                        assert prior >= 0xe000 and b['raw'][16+127*8192+prior-0xe000] == 0x58
                        defer_rows.append(dict(ROM=bi,char=char,lag=lag,Sprite0Flag=sprite,boundary=index,PC=pc,
                                               preceding_CLI_PC=prior,note='One physical CLI deferred instruction; not falsely injected by py65'))
                        continue
                    actual = run(b,seed(b,char,1,lag,0,1,1,sprite),inject=index)
                    for field in ['regs','ram','banks','reads','serial','IOreads']:
                        assert actual[field] == reference[field], ('IRQ-resume',bi,char,lag,sprite,index,pc,field)
                    assert remove_IRQ(actual['raw_writes'],actual['IRQwrites']) == reference['raw_writes']
                    assert not actual['IRQreads'] or all(at == 0x5204 for at,_ in actual['IRQreads'])
                    IRQrows.append(dict(ROM=bi,char=char,lag=lag,Sprite0Flag=sprite,boundary=index,PC=pc,
                                        original_clock=clock,IRQ_writes=actual['IRQwrites'],IRQ_reads=actual['IRQreads'],
                                        resumed_full_state_and_remaining_ordered_NMI_writes_exact=True))
            print(json.dumps(dict(IRQ_ROM=bi,IRQ_cases=len(IRQrows))), flush=True)
        put(a.output/'cases.json',rows)
        put(a.output/'inputs.json',input_rows)
        put(a.output/'IRQ-cases.json',IRQrows)
        put(a.output/'schedule.json',timing)
        put(a.output/'CLI-deferred.json',defer_rows)
        result = dict(passed=True,source_only=True,native_run=False,adopted=False,
            baseline_ROM_sha256=sha(a.parent/'candidate.nes'),candidate_ROM_sha256=sha(a.candidate/'candidate.nes'),
            parent_menu_visual_and_owner_qualified=False,parent_menu_owner_negative_explicit=True,
            complete_NMI_cases=len(rows),direct_input_parity_cases=len(input_rows),actual_IRQ_cases=len(IRQrows),
            IRQ_profile='Both linked routines x char0/18 x regular/lag x Sprite0Flag0/1; every enabled preAudio boundary except actual first physical CLI-defer instruction.',
            IRQ_deferred_instruction_boundaries=len(defer_rows),complete_AXYP_SP_app_RAM_5SMC_banks_input_and_other_ordered_IO_exact=True,
            IO_order_delta='Only5203/5204 writes intentionally move. Their complete values/order compare separately; every remaining ordered nonstack write, including every2001, is exact. All IO read values/order exact.',
            total_complete_NMI_cycle_delta=[0,0],IRQ_physical_status_mask='0xcf: only py65 virtualB/U; all realN,V,D,I,Z,C exact',
            unchanged_256_DMA_assertion=True,
            limits='Synthetic CPU only; bus models DMA parity stalls and serial/palette reads. No physical256DMA/PPU31/deadline/menu ownership/native acceptance. Native CLI hardware deferral is acknowledged, not modeled by an immediate py65 irq call.',
            artifacts={n:sha(a.output/n) for n in ['cases.json','inputs.json','IRQ-cases.json','schedule.json','CLI-deferred.json']},
            bindings={str(p):sha(p) for p in [Path(__file__),Path(H.__file__),a.parent/'candidate.nes',a.parent/'candidate.dbg',a.candidate/'candidate.nes',a.candidate/'candidate.dbg',a.candidate/'proof.json',a.candidate/'source-manifest.json']})
        put(a.output/'proof.json',result)
        print(json.dumps(result,indent=2))
    except BaseException as ex:
        put(a.output/'failure.json',dict(passed=False,native_run=False,error=repr(ex),traceback=traceback.format_exc(),
                                      completed_NMI=rows,completed_inputs=input_rows,completed_IRQ=IRQrows))
        (a.output/'failed-tool.py').write_bytes(Path(__file__).read_bytes())
        raise


if __name__ == '__main__':
    main()
