"""Reached91dc entry/header cuts: paired actual IRQ/busyNMI and return fidelity."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json
import replay_battletoads_mature8_food_credit_1116 as F
import check_smb1_alts_full11_1114 as Runner
import wwf_stock_source_model_1115 as Model

C,N,W=F.C,F.N,F.W

def run(parent):
    raw,composition=C.proposal(parent);base=N.NesMPU;seen=set();counts=Counter();cuts=[];minimum=255;trace=sha256();continuations=0
    cookie=raw[C.COOKIE:C.COOKIE+16];old_cookie=parent[C.COOKIE:C.COOKIE+16];owned=((0x45,0x48),(0x1603,0x160b),(0x1fe4,0x1ff0))
    b=F.Current.bundle(raw);check_pc=W.address(b,'BtCheck');check_file=W.location(b,'BtCheck')
    pattern=b'\xdd'+W.address(b,'BtCookie').to_bytes(2,'little');hits=[i for i in range(60)if raw[check_file+i:check_file+i+3]==pattern];assert len(hits)==1
    header_cmp=check_pc+hits[0]
    class Bus(W.ControllerBus):
        def __getitem__(self,at):
            if isinstance(at,int)and getattr(self,'_isr_active',False)and at>=0x8000:
                tag=self.rawtags[(at-0x8000)//8192]
                if tag==3 and any(lo<=at&8191<hi for lo,hi in owned):self._owned_reads.append((tag,at))
                elif tag&128:
                    file=16+(tag&127)*8192+(at&8191)
                    if C.COOKIE+4<=file<C.COOKIE+16:self._owned_reads.append((tag,at))
            return super().__getitem__(at)
    def fork(m):
        q=N.fork(m);q.__class__=Bus;q._isr_active=False;q._owned_reads=[]
        q.writes.clear();q.ram_writes.clear();q.ppu_log.clear();return q
    def reference(m):
        q=fork(m);q.bundle=dict(q.bundle,raw=parent)
        for at,old,new in C.spans():
            if C.CACHE<=at<C.CACHE+8192:q.ram[3][at-C.CACHE:at-C.CACHE+len(old)]=old
        q.ram[3][0x1fe0:0x1ff0]=old_cookie
        for slot,tag in enumerate(q.rawtags):
            if tag&128:q.raw_page(slot,tag)
        q.writes.clear();q.ram_writes.clear();q.ppu_log.clear();return q
    def transport(m):return(bytes(m[3:11]),bytes(m[0x15a:0x17b]),m.rawtags[:],m.chr_latches[:])
    def critical(m):
        names=('SelectedCharacter','CurrentPlayer','OperMode','OperMode_Task','GameEngineSubroutine','NumberofLives','PlayerStatus',
            'WorldNumber','LevelNumber','Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_State','StarInvincibleTimer')
        return tuple(N.get(m,n)for n in names)
    def continuation(original,interrupted,regs,header):
        nonlocal continuations
        control=fork(original);c=base(memory=control,pc=regs[5]);c.a,c.x,c.y,c.p,c.sp=regs[:5]
        a,ma=interrupted;ma._isr_active=False
        saved=4 if header else 0
        lo=0x100+((regs[4]+saved+1)&255);hi=0x100+((regs[4]+saved+2)&255)
        pc=(control[lo]+256*control[hi]+1)&65535;sp=(regs[4]+saved+2)&255
        for _ in range(5000):
            if(c.pc,c.sp)==(pc,sp)and(a.pc,a.sp)==(pc,sp):break
            assert(c.pc,c.sp)==(a.pc,a.sp)and(c.a,c.x,c.y,c.p&239)==(a.a,a.x,a.y,a.p&239)
            assert control[c.pc]and ma[a.pc];c.step();a.step()
        else:raise AssertionError(('Interrupted private/header continuation bound',regs,pc,sp))
        assert(c.a,c.x,c.y,c.p&239,c.sp,c.pc)==(a.a,a.x,a.y,a.p&239,a.sp,a.pc)
        assert[bytes(v)for v in control.ram]==[bytes(v)for v in ma.ram]
        assert critical(control)==critical(ma)and transport(control)==transport(ma)
        assert bytes(control[0x101+regs[4]:0x200])==bytes(ma[0x101+regs[4]:0x200])
        continuations+=1
    def pair(cpu,kind,header):
        nonlocal minimum
        regs=(cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp,cpu.pc);machines=[];prior=[]
        for old in(False,True):
            m=reference(cpu.memory)if old else fork(cpu.memory)
            c=base(memory=m,pc=cpu.pc);c.a,c.x,c.y,c.p,c.sp=regs[:5]
            prior.append(dict(private=[bytes(v)for v in m.ram],transport=transport(m),critical=critical(m),
                upper=bytes(m[0x101+c.sp:0x200]),skip=N.get(m,'NmiSkipped')))
            m._isr_active=True;c.irq()if kind=='IRQ'else c.nmi();machines.append((c,m))
        for _ in range(100000):
            a,ma=machines[0];d,md=machines[1]
            assert(a.a,a.x,a.y,a.p&239,a.sp,a.pc)==(d.a,d.x,d.y,d.p&239,d.sp,d.pc)
            minimum=min(minimum,a.sp,d.sp)
            if(a.pc,a.sp)==(regs[5],regs[4]):break
            assert a.sp<=regs[4]and ma.rawtags==md.rawtags
            tag=ma.rawtags[(a.pc-0x8000)//8192]if a.pc>=0x8000 else-1
            assert not(tag==3 and(a.pc==0xa045 or 0xb603<=a.pc<0xb60b)),'ISR executes changed maturity entry'
            code=bytes(ma[a.pc:a.pc+3]);assert code==bytes(md[d.pc:d.pc+3])and ma[a.pc]
            trace.update(bytes((a.pc&255,a.pc>>8,a.sp,a.p&239))+code);a.step();d.step()
        else:raise AssertionError('Paired IRQ RTI return bound')
        assert(a.a,a.x,a.y,a.p&239,a.sp,a.pc)==(*regs[:3],regs[3]&239,*regs[4:])
        native=[];host=[]
        for(c,m),before in zip(machines,prior,strict=True):
            m._isr_active=False;assert not m._owned_reads,'ISR reads changed code or fingerprint'
            assert[bytes(v)for v in m.ram]==before['private']
            assert transport(m)==before['transport']and critical(m)==before['critical']
            assert bytes(m[0x101+regs[4]:0x200])==before['upper']
            assert N.get(m,'NmiSkipped')==(before['skip']+(kind=='busyNMI'))&255
            native.append(bytes(m[:0x800]));host.append(bytes(m[0x5c00:0x8000]))
        assert native[0]==native[1]and host[0]==host[1],'Candidate/parent ISR native or audio effects differ'
        continuation(cpu.memory,machines[0],regs,header);counts[kind]+=1
    class CPU(base):
        def step(self):
            m=self.memory
            if hasattr(m,'bundle')and m.bundle.get('raw')is raw and self.pc>=0x8000 and not self.p&4:
                tag=m.rawtags[(self.pc-0x8000)//8192]
                private=tag==3 and self.pc in(0xa045,0xb603,0xb605,0xb606,0xb608,0xb602)
                header=tag==221 and self.pc==header_cmp
                if(private or header)and bytes(m.ram[3][0x1fe0:0x1ff0])==cookie:
                    mature=m[W.address(b,'Enemy_State')+self.x]>=128 if private else False
                    key=(self.pc,self.sp,self.p&195,mature,self.x if header else-1)
                    if key not in seen:
                        seen.add(key);assert len(seen)<=256
                        pair(self,'IRQ',header)
                        if N.get(m,'NmiDisable')==255:pair(self,'busyNMI',header)
                        cuts.append(dict(PC=self.pc,SP=self.sp,P=self.p,header_X=self.x if header else-1,mature=mature))
            return super().step()
    family=F.family()
    with patch.object(N,'NesMPU',CPU),patch.object(Runner,'Factory',family),patch.object(Runner,'cold',F.Current.cold),patch.object(Runner,'strict_metadata',family.metadata):route=Model.run(raw,'rash',600)
    assert route['passed']and counts['IRQ']and counts['busyNMI']
    assert{0xa045,0xb603,0xb605,0xb606,0xb608,0xb602}<={r['PC']for r in cuts}
    assert{r['header_X']for r in cuts if r['header_X']>=0}==set(range(16))
    q=dict(passed=True,composition=composition,genuine_M_receipt_SHA256=route['source_receipt_SHA256'],
        paired_counts=dict(counts),reached_contexts=cuts,minimum_ISR_SP=minimum,completed_private_or_header_continuations=continuations,
        ISR_trace_SHA256=trace.hexdigest(),actual_parent_ROM_header_baseline=True,no_changed_code_or_cookie_ISR_reads=True,
        all33_SMC_live_stack_maps_private_critical_preserved=True,exact_same_native_host_audio_effects=True,
        no_native_RAM_allowlist=True,outputs=0,Mesen=False)
    q['receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    parent=C.ROM.read_bytes()
    def deny(*args,**kw):raise AssertionError('IRQ source attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny),patch.object(Runner.Native,'run',deny):q=run(parent)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
