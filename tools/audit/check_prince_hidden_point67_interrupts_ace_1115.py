"""Paired current IRQ/busy-NMI at genuinely reached new point instructions."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
from hashlib import sha256
import json
import current_prince_hidden_point67_ace_1115 as Current

C,N,W,Frames=Current.C,Current.N,Current.W,Current.Frames

def run(parent):
    raw,composition=C.proposal(parent);base=N.NesMPU;counts=Counter();seen=set();cuts=[];minimum=255;trace=sha256();native=Counter()
    class Bus(W.ControllerBus):
        def __getitem__(self,at):
            if isinstance(at,int)and getattr(self,'_point_probe',False)and 0xb310<=at<0xb353 and self.rawtags[1]==3:
                self._point_reads.append(at)
            return super().__getitem__(at)
    def pair(cpu,kind):
        nonlocal minimum
        regs=(cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp,cpu.pc);trials=[];before=[]
        for old in(False,True):
            m=N.fork(cpu.memory);m.__class__=Bus;m._point_probe=False;m._point_reads=[]
            if old:m.ram[3][0x1310:0x1353]=C.OLD
            c=base(memory=m,pc=cpu.pc);c.a,c.x,c.y,c.p,c.sp=regs[:5]
            before.append(dict(private=[bytes(b)for b in m.ram],maps=m.rawtags[:],
                transport=(bytes(m[3:11]),bytes(m[0x15a:0x17b]),m.chr_latches[:]),
                upper=bytes(m[0x101+c.sp:0x200]),native=bytes(m[:0x800]),skip=N.get(m,'NmiSkipped')))
            m._point_probe=True;c.irq()if kind=='IRQ'else c.nmi();trials.append((c,m))
        for _ in range(100000):
            a,ma=trials[0];b,mb=trials[1]
            assert(a.a,a.x,a.y,a.p&239,a.sp,a.pc)==(b.a,b.x,b.y,b.p&239,b.sp,b.pc)
            minimum=min(minimum,a.sp,b.sp)
            if(a.pc,a.sp)==(regs[5],regs[4]):break
            assert a.sp<=regs[4]and ma.rawtags==mb.rawtags
            assert not(0xb310<=a.pc<0xb353 and ma.rawtags[1]==3)
            code=bytes(ma[a.pc:a.pc+3]);assert code==bytes(mb[b.pc:b.pc+3])and ma[a.pc]
            trace.update(bytes((a.pc&255,a.pc>>8,a.sp,a.p&239))+code);a.step();b.step()
        else:raise AssertionError('Paired point ISR return bound')
        assert(a.a,a.x,a.y,a.p&239,a.sp,a.pc)==(*regs[:3],regs[3]&239,*regs[4:])
        effects=[]
        for(c,m),prior in zip(trials,before,strict=True):
            m._point_probe=False;assert not m._point_reads,'ISR routing/data depends on changed point bytes'
            assert[bytes(b)for b in m.ram]==prior['private']and m.rawtags==prior['maps']
            assert(bytes(m[3:11]),bytes(m[0x15a:0x17b]),m.chr_latches[:])==prior['transport']
            assert bytes(m[0x101+regs[4]:0x200])==prior['upper']
            assert N.get(m,'NmiSkipped')==(prior['skip']+(kind=='busyNMI'))&255
            effects.append(bytes(m[:0x800]))
        assert effects[0]==effects[1]
        for at,(old,new)in enumerate(zip(before[0]['native'],effects[0])):
            if old!=new and not 0x100<=at<0x200:native[(kind,at,old,new)]+=1
        counts[kind]+=1
    class CPU(base):
        def step(self):
            m=self.memory;point=m.rawtags[1]==3 and 0xb310<=self.pc<0xb353
            leaf=self.pc==0x9eca and m.rawtags[0]==254 and self.sp<=253 and m[0x101+self.sp]+256*m[0x102+self.sp]+1==0xb33d
            if(point or leaf)and not self.p&4:
                key=(self.pc,self.sp,self.p&193)
                if key not in seen:
                    seen.add(key);assert len(seen)<=512
                    pair(self,'IRQ')
                    if N.get(m,'NmiDisable')==255:pair(self,'busyNMI')
                    cuts.append(dict(PC=self.pc,SP=self.sp,P=self.p,native_leaf=leaf))
            return super().step()
    with patch.object(N,'NesMPU',CPU):
        m,opening=Current.cold(raw)
        for tick in range(320):m.controller_pad=1 if tick>=64 else 0;Frames.frame(m,whole_pass=True)
    assert counts['IRQ']and counts['busyNMI']and any(x['native_leaf']for x in cuts)
    q=dict(passed=True,composition=composition,opening=opening,ordinary_source_Main=320,
        paired_interrupt_counts=dict(counts),reached_contexts=cuts,minimum_ISR_SP=minimum,
        identical_ISR_trace_SHA256=trace.hexdigest(),baseline_restores_only_old67=True,
        no_ISR_point_code_reads=True,all_private_and_transport_live_stack_maps_preserved=True,
        exact_candidate_parent_native_audio_effects=True,no_native_RAM_allowlist=True,
        observed_native_effects=[dict(kind=k[0],address=k[1],before=k[2],after=k[3],cases=v)for k,v in sorted(native.items())],
        scope='Genuine compiled cold and ordinary Right prefix; point/native-leaf cuts, not a full route',
        actual_CPU_ROM_SHA256=C.digest(m.bundle['raw']),outputs=0,Mesen=False)
    q['receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    def deny(*a,**k):raise AssertionError('Point ISR source attempted output/native launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
