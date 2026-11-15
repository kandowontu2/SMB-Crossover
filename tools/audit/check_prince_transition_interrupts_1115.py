"""Reached219 IRQ/busyNMI cuts on genuine590 controls, source only."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json
import check_prince_transition_model_1115 as Model

N,W=Model.N,Model.W


def run(raw):
    base=N.NesMPU;counts=Counter();cuts=[];seen=set();minimum=255
    def snapshot(m):
        return([bytes(b)for b in m.ram],bytes(m[3:11]),bytes(m[0x15a:0x17b]),m.rawtags[:],m.chr_latches[:],bytes(m[0x200:0x800]))
    def interrupt(cpu,kind):
        nonlocal minimum
        m=N.fork(cpu.memory);m.__class__=W.ControllerBus
        c=base(memory=m,pc=cpu.pc);c.a,c.x,c.y,c.p,c.sp=cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp
        regs=(c.a,c.x,c.y,c.p,c.sp,c.pc);before=snapshot(m);skip=N.get(m,'NmiSkipped')
        protected=bytes(m[0x101+c.sp:0x200])
        c.irq()if kind=='IRQ'else c.nmi()
        for _ in range(100000):
            minimum=min(minimum,c.sp)
            if(c.pc,c.sp)==(regs[5],regs[4]):break
            assert c.sp<=regs[4]and m[c.pc],('Reached ISR stack/BRK',kind,hex(cpu.pc))
            c.step()
        else:raise AssertionError('Reached ISR bounded return')
        assert(c.a,c.x,c.y,c.p&239,c.sp,c.pc)==(*regs[:3],regs[3]&239,*regs[4:])
        after=snapshot(m);assert before[:5]==after[:5],'ISR private/scratch/map/CHR mutation'
        left,right=bytearray(before[5]),bytearray(after[5])
        if kind=='busyNMI':
            assert N.get(m,'NmiSkipped')==(skip+1)&255
            left[0x7da-0x200]=right[0x7da-0x200]=0
        else:assert N.get(m,'NmiSkipped')==skip
        assert left==right and bytes(m[0x101+regs[4]:0x200])==protected
        counts[kind]+=1
    class CPU(base):
        def step(self):
            m=self.memory
            if hasattr(m,'rawtags')and Model.Research.START<=self.pc<Model.Research.END and m.rawtags[2]==2 and not self.p&4:
                if hasattr(m,'bundle')and m.bundle.get('raw')==raw and N.get(m,'SelectedCharacter')==38:
                    key=(self.pc,self.sp,self.p&193)
                    if key not in seen:
                        seen.add(key);assert len(seen)<=256
                        interrupt(self,'IRQ')
                        if N.get(m,'NmiDisable')==255:interrupt(self,'busyNMI')
                        cuts.append(dict(PC=self.pc,SP=self.sp,P=self.p,state=Model.state(m)))
            return super().step()
    def stop(m,tick):
        s=Model.state(m)
        return tick>4507 and s['x']>=1880 and s['guard']==1 and s['hp']>0
    with patch.object(N,'NesMPU',CPU):q=Model.run(raw,full=True,limit=5100,frame_observer=stop)
    assert q['checkpoint_reached']and counts['IRQ']and counts['busyNMI']
    q.update(reached_interrupt_counts=dict(counts),reached_unique_contexts=len(cuts),
        reached_instruction_PCs=sorted({c['PC']for c in cuts}),minimum_ISR_SP=minimum,
        all_caller_AXYP_PC_SP_and_stack_above_entry_exact=True,all_private_scratch_maps_CHR_exact=True,
        native_RAM_exact_except_declared_busy_audio_duration=True,
        interrupt_scope='Real reached contexts on temporary copies; original ordinary foreground execution unchanged')
    q['interrupt_receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':
    def deny(*args,**kwargs):raise AssertionError('Reached ISR proof attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
