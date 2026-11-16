"""Reached life/snapshot IRQ and busyNMI, paired with exact installed parent."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import json
import replay_metal_life_00bb_1116 as F
import check_smb1_alts_full11_1114 as Runner
import wwf_stock_source_model_1115 as Model

C,N,W=F.C,F.N,F.W


def run(parent):
    raw,_=C.proposal(parent);base=N.NesMPU;seen=set();cuts=[];counts=Counter();effects=Counter();minimum=255;continuations=0
    class Bus(W.ControllerBus):
        def __getitem__(self,at):
            if isinstance(at,int)and getattr(self,'_isr_readcheck',False)and at>=0x8000:
                tag=self.rawtags[(at-0x8000)//8192];off=at&8191
                if not tag&128:
                    if tag==2 and off in(0x14ad,0x14ae)or tag in(2,3)and 0x1fe2<=off<0x1ff0:self._changed_reads.append(at)
                else:
                    file=16+(tag&127)*8192+off
                    if any(lo+2<=file<lo+16 for lo in(212991,817141)):self._changed_reads.append(at)
            return super().__getitem__(at)
    def fork(m,old=False):
        t=N.fork(m);t.__class__=Bus;t._isr_readcheck=False;t._changed_reads=[]
        if old:
            t.bundle=dict(t.bundle,raw=parent);t.ram[2][0x14ad:0x14af]=bytes.fromhex('f039')
            for b in(2,3):t.ram[b][0x1fe0:0x1ff0]=C.OLD_COOKIE
            for slot,tag in enumerate(t.rawtags):
                if tag&128:t.raw_page(slot,tag)
        return t
    def transport(m):return(bytes(m[3:11]),bytes(m[0x15a:0x17b]),m.rawtags[:],m.chr_latches[:])
    def critical(m):return tuple(N.get(m,n)for n in('SelectedCharacter','CurrentPlayer','GameEngineSubroutine','NumberofLives','PlayerStatus','Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_State'))
    def continuation(original,interrupted,regs):
        nonlocal continuations
        t=fork(original);c=base(memory=t,pc=regs[5]);c.a,c.x,c.y,c.p,c.sp=regs[:5];a,ma=interrupted;ma._isr_readcheck=False
        pc=(t[0x101+regs[4]]+256*t[0x102+regs[4]]+1)&65535;sp=(regs[4]+2)&255
        for _ in range(500000):
            if(c.pc,c.sp)==(pc,sp)and(a.pc,a.sp)==(pc,sp):break
            assert(c.a,c.x,c.y,c.p&239,c.sp,c.pc)==(a.a,a.x,a.y,a.p&239,a.sp,a.pc)
            assert t[c.pc]and ma[a.pc];c.step();a.step()
        else:raise AssertionError('Reached movement continuation return bound')
        assert(c.a,c.x,c.y,c.p&239,c.sp,c.pc)==(a.a,a.x,a.y,a.p&239,a.sp,a.pc)
        assert[bytes(v)for v in t.ram]==[bytes(v)for v in ma.ram]
        assert transport(t)==transport(ma)and critical(t)==critical(ma)
        assert bytes(t[0x101+regs[4]:0x200])==bytes(ma[0x101+regs[4]:0x200]);continuations+=1
    def pair(cpu,kind):
        nonlocal minimum
        regs=(cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp,cpu.pc);machines=[];prior=[]
        for old in(False,True):
            m=fork(cpu.memory,old);c=base(memory=m,pc=cpu.pc);c.a,c.x,c.y,c.p,c.sp=regs[:5]
            prior.append(dict(private=[bytes(v)for v in m.ram],transport=transport(m),critical=critical(m),native=bytes(m[:0x800]),upper=bytes(m[0x101+c.sp:0x200]),skip=N.get(m,'NmiSkipped')))
            m._isr_readcheck=True;c.irq()if kind=='IRQ'else c.nmi();machines.append((c,m))
        for _ in range(100000):
            a,ma=machines[0];b,mb=machines[1];minimum=min(minimum,a.sp,b.sp)
            assert(a.a,a.x,a.y,a.p&239,a.sp,a.pc)==(b.a,b.x,b.y,b.p&239,b.sp,b.pc)
            if(a.pc,a.sp)==(regs[5],regs[4]):break
            assert a.sp<=regs[4]and ma.rawtags==mb.rawtags and ma[a.pc]
            assert bytes(ma[a.pc:a.pc+3])==bytes(mb[b.pc:b.pc+3]);a.step();b.step()
        else:raise AssertionError('Paired actual ISR RTI bound')
        assert(a.a,a.x,a.y,a.p&239,a.sp,a.pc)==(*regs[:3],regs[3]&239,*regs[4:])
        native=[]
        for(c,m),before in zip(machines,prior,strict=True):
            m._isr_readcheck=False;assert not m._changed_reads
            assert[bytes(v)for v in m.ram]==before['private']and transport(m)==before['transport']and critical(m)==before['critical']
            assert bytes(m[0x101+regs[4]:0x200])==before['upper']
            assert N.get(m,'NmiSkipped')==(before['skip']+(kind=='busyNMI'))&255
            native.append(bytes(m[:0x800]))
        assert native[0]==native[1],'Exact parent/candidate native audio/ISR effects differ'
        for at,(old,new)in enumerate(zip(prior[0]['native'],native[0])):
            if old!=new and not 0x100<=at<0x200:effects[kind,at,old,new]+=1
        continuation(cpu.memory,machines[0],regs);counts[kind]+=1
    class CPU(base):
        def step(self):
            m=self.memory
            if self.pc in(0xd4ad,0xd4e5,0xd4e8)and m.rawtags[2]==2 and not self.p&4 and m.bundle.get('raw')is raw:
                key=(self.pc,self.sp,self.p&195,N.get(m,'NumberofLives'),m.ram[2][0x83e])
                if key not in seen:
                    seen.add(key);assert len(seen)<128;pair(self,'IRQ')
                    if N.get(m,'NmiDisable')==255:pair(self,'busyNMI')
                    cuts.append(dict(PC=self.pc,SP=self.sp,P=self.p,life=N.get(m,'NumberofLives'),saved=m.ram[2][0x83e]))
            return super().step()
    family=F.family('oneup')
    with patch.object(N,'NesMPU',CPU),patch.object(Runner,'Factory',family),patch.object(Runner,'cold',F.Current.cold),patch.object(Runner,'strict_metadata',family.metadata):route=Model.run(raw,'metal',1400)
    assert route['passed']and counts['IRQ']and counts['busyNMI']
    assert any(q['PC']==0xd4e5 and q['life']==3 and q['saved']==2 for q in cuts)
    return dict(passed=True,ROM_SHA256=F.PIN,genuine_route_receipt_SHA256=route['source_receipt_SHA256'],
        paired_interrupt_counts=dict(counts),reached_contexts=cuts,minimum_ISR_SP=minimum,complete_movement_return_continuations=continuations,
        exact_parent_native_audio_effects=True,no_native_RAM_allowlist=True,no_changed_ISR_code_or_cookie_reads=True,
        SMC_scratch_maps_private_and_live_stack_preserved=True,
        native_effects=[dict(kind=k[0],address=k[1],before=k[2],after=k[3],cases=v)for k,v in sorted(effects.items())],
        outputs=0,Mesen=False,scope='Reached genuine M/INC/25 route life branch and existing snapshot STA; paired ISR plus full movement return, not deepest nested ISR or full-stage proof')


if __name__=='__main__':
    parent=F.ROM.read_bytes()
    def deny(*args,**kw):raise AssertionError('Metal ISR attempted artifacts/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny),patch.object(Runner.Native,'run',deny):q=run(parent)
    q['receipt_SHA256']=F.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
