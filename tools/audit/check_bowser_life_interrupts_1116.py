"""Reached genuine6a3 life-path IRQ/busyNMI and Ensure continuation fidelity."""
from collections import Counter
from pathlib import Path
from hashlib import sha256
from unittest.mock import patch
import json
import replay_bowser_life_gain_1116 as F
import bowser_life_source_components_1116 as T
import check_smb1_alts_full11_1114 as Runner
import wwf_stock_source_model_1115 as Model

C,N,W=F.C,F.N,F.W
def run(parent):
    raw,composition=C.proposal(parent);base=N.NesMPU;counts=Counter();seen=set();cuts=[];minimum=255;trace=sha256();effects=Counter();continuations=0
    start,end=C.lease()['envelope']['CPU_half_open'];cookie=bytes.fromhex(C.lease()['cookie_views']['new_hex'])
    class Bus(W.ControllerBus):
        def __getitem__(self,at):
            if isinstance(at,int)and getattr(self,'_irq_probe',False)and at>=0x8000:
                tag=self.rawtags[(at-0x8000)//8192]
                if not tag&128 and tag&3==3:
                    offset=at&8191
                    if start&8191<=offset<end&8191 or 0x1fe4<=offset<0x1ff0:self._changed_reads.append(at)
                elif tag&128:
                    file=16+(tag&127)*8192+(at&8191)
                    if any(lo+4<=file<lo+16 for lo in C.lease()['cookie_views']['files']):self._changed_reads.append(at)
            return super().__getitem__(at)
    def transport(m):return(bytes(m[3:11]),bytes(m[0x15a:0x17b]),m.rawtags[:],m.chr_latches[:])
    def critical(m):
        names=('SelectedCharacter','CurrentPlayer','OperMode','OperMode_Task','GameEngineSubroutine','NumberofLives','PlayerStatus',
            'WorldNumber','LevelNumber','Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_State','StarInvincibleTimer')
        return tuple(N.get(m,n)for n in names)
    def same_continuation(original,interrupted,regs):
        nonlocal continuations
        control=T.fork(original);control.__class__=Bus;control._irq_probe=False
        c=base(memory=control,pc=regs[5]);c.a,c.x,c.y,c.p,c.sp=regs[:5]
        a,ma=interrupted;ma._irq_probe=False
        pc=(control[0x101+regs[4]]+256*control[0x102+regs[4]]+1)&65535;sp=(regs[4]+2)&255
        for _ in range(5000):
            if(c.pc,c.sp)==(pc,sp)and(a.pc,a.sp)==(pc,sp):break
            assert(c.pc,c.sp)==(a.pc,a.sp)
            assert(c.a,c.x,c.y,c.p&239)==(a.a,a.x,a.y,a.p&239)
            assert control[c.pc]and ma[a.pc];c.step();a.step()
        else:raise AssertionError('Interrupted Ensure continuation return bound')
        assert(c.a,c.x,c.y,c.p&239,c.sp,c.pc)==(a.a,a.x,a.y,a.p&239,a.sp,a.pc)
        assert[bytes(v)for v in control.ram]==[bytes(v)for v in ma.ram]
        assert critical(control)==critical(ma)and transport(control)==transport(ma)
        assert bytes(control[0x101+regs[4]:0x200])==bytes(ma[0x101+regs[4]:0x200])
        continuations+=1
    def pair(cpu,kind):
        nonlocal minimum
        regs=(cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp,cpu.pc);machines=[];prior=[]
        for old in(False,True):
            m=T.reference(cpu.memory,parent)if old else T.fork(cpu.memory);m.__class__=Bus;m._irq_probe=False;m._changed_reads=[]
            c=base(memory=m,pc=cpu.pc);c.a,c.x,c.y,c.p,c.sp=regs[:5]
            prior.append(dict(private=[bytes(v)for v in m.ram],transport=transport(m),critical=critical(m),native=bytes(m[:0x800]),
                host=bytes(m[0x5c00:0x8000]),upper=bytes(m[0x101+c.sp:0x200]),skip=N.get(m,'NmiSkipped')))
            m._irq_probe=True;c.irq()if kind=='IRQ'else c.nmi();machines.append((c,m))
        for _ in range(100000):
            a,ma=machines[0];b,mb=machines[1]
            assert(a.a,a.x,a.y,a.p&239,a.sp,a.pc)==(b.a,b.x,b.y,b.p&239,b.sp,b.pc)
            minimum=min(minimum,a.sp,b.sp)
            if(a.pc,a.sp)==(regs[5],regs[4]):break
            assert a.sp<=regs[4]and ma.rawtags==mb.rawtags
            assert not(start<=a.pc<end and ma.rawtags[1]==3),'ISR may not execute changed Ensure'
            code=bytes(ma[a.pc:a.pc+3]);assert code==bytes(mb[b.pc:b.pc+3])and ma[a.pc]
            trace.update(bytes((a.pc&255,a.pc>>8,a.sp,a.p&239))+code);a.step();b.step()
        else:raise AssertionError('Paired actual ISR RTI return bound')
        assert(a.a,a.x,a.y,a.p&239,a.sp,a.pc)==(*regs[:3],regs[3]&239,*regs[4:])
        native=[];host=[]
        for(c,m),before in zip(machines,prior,strict=True):
            m._irq_probe=False;assert not m._changed_reads,'ISR reads changed code or fingerprint fields'
            assert[bytes(v)for v in m.ram]==before['private']
            assert transport(m)==before['transport']and critical(m)==before['critical']
            assert bytes(m[0x101+regs[4]:0x200])==before['upper']
            assert N.get(m,'NmiSkipped')==(before['skip']+(kind=='busyNMI'))&255
            native.append(bytes(m[:0x800]));host.append(bytes(m[0x5c00:0x8000]))
        assert native[0]==native[1]and host[0]==host[1],'Candidate and actual-parent ISR effects differ'
        for at,(old,new)in enumerate(zip(prior[0]['native'],native[0])):
            if old!=new and not 0x100<=at<0x200:effects[(kind,at,old,new)]+=1
        same_continuation(cpu.memory,machines[0],regs);counts[kind]+=1
    class CPU(base):
        def step(self):
            m=self.memory
            if start<=self.pc<end and m.rawtags[1]==3 and not self.p&4:
                if m.bundle.get('raw')is raw and N.get(m,'SelectedCharacter')==27 and bytes(m.ram[3][0x1fe0:0x1ff0])==cookie:
                    key=m.ram[3][0x1e27]
                    if key not in(0,4):return super().step()
                    gain=N.get(m,'NumberofLives')!=m.ram[3][0x1f82+key]
                    context=(self.pc,self.sp,self.p&195,gain)
                    if context not in seen:
                        seen.add(context);assert len(seen)<=512
                        pair(self,'IRQ')
                        if N.get(m,'NmiDisable')==255:pair(self,'busyNMI')
                        cuts.append(dict(PC=self.pc,SP=self.sp,P=self.p,real_life_mismatch=gain))
            return super().step()
    family=F.family(0,'oneup')
    with patch.object(N,'NesMPU',CPU),patch.object(Runner,'Factory',family),patch.object(Runner,'cold',F.Current.cold),patch.object(Runner,'strict_metadata',family.metadata):route=Model.run(raw,'smb3',1400)
    assert route['passed']and counts['IRQ']and counts['busyNMI']
    assert any(cut['PC']==0xa153 and cut['real_life_mismatch']for cut in cuts),'Reached actual post-INC saved-life STA required'
    stock=route['receipt']['stock'];q=dict(passed=True,composition=composition,genuine_route_receipt_SHA256=route['source_receipt_SHA256'],
        genuine_life=dict(collector=stock['collector'],credit=stock['credit'],resumed=stock['resumed'],preserved_HP=stock['preserved_HP'],saved_life=stock['saved_life']),
        paired_interrupt_counts=dict(counts),reached_contexts=cuts,minimum_ISR_SP=minimum,completed_Ensure_continuations=continuations,
        exact_ISR_trace_SHA256=trace.hexdigest(),actual_parent_ROM_and_header_baseline=True,no_changed_code_or_fingerprint_ISR_reads=True,
        all33_SMC_live_stack_maps_and_critical_fields_preserved=True,all_private_RAM_unchanged_by_ISR=True,
        exact_same_native_host_audio_effects=True,no_native_RAM_allowlist=True,
        native_effects=[dict(kind=k[0],address=k[1],before=k[2],after=k[3],cases=v)for k,v in sorted(effects.items())],
        scope='Actual candidate cold +same genuine M/hiddenL route; reached IRQ/busyNMI plus complete Ensure-return continuation, not full-stage proof',outputs=0,Mesen=False)
    q['receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    parent=C.ROM.read_bytes()
    def deny(*a,**kw):raise AssertionError('Reached ISR source attempted files/native')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny),patch.object(Runner.Native,'run',deny):q=run(parent)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
