"""Reached candidate Mini helpers and real Roll exit: paired IRQ/busyNMI."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import json
import replay_mini_weapon_owner_twoshot_1116 as F
import check_mini_weapon_owner_public_1116 as Public
import check_smb1_alts_full11_1114 as Runner
import wwf_stock_source_model_1115 as Model

C,N,W=F.C,F.N,F.W
PCS={0xaaea,0xaafd,0xb53a,0xb53c,0xb53f,0xb541,0xb544,0xb545,0xb546,0xb547,0xb54a,0xb54b}

def run(parent):
    raw,_=C.proposal(parent);base=N.NesMPU;seen=set();cuts=[];counts=Counter();effects=Counter();minimum=255;continuations=0;probe=None
    class Bus(W.ControllerBus):
        def __getitem__(self,at):
            if isinstance(at,int)and getattr(self,'_owner_isr',False)and at>=0x8000:
                tag=self.rawtags[(at-0x8000)//8192]
                if tag&128:
                    file=16+(tag&127)*8192+(at&8191)
                    if any(lo<=file<lo+len(old)for lo,old,_ in C.SPANS):self._owner_changed_reads.append(at)
            return super().__getitem__(at)
    def fork(m,old=False):
        t=N.fork(m);t.__class__=Bus;t._owner_isr=False;t._owner_changed_reads=[]
        if old:
            t.bundle=dict(t.bundle,raw=parent)
            for slot,tag in enumerate(t.rawtags):
                if tag&128:t.raw_page(slot,tag)
        return t
    def transport(m):return(bytes(m[3:11]),bytes(m[0x15a:0x17b]),m.rawtags[:],m.chr_latches[:])
    def critical(m):return tuple(N.get(m,n)for n in('SelectedCharacter','CurrentPlayer','GameEngineSubroutine','NumberofLives','PlayerStatus','Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_State'))
    def continuation(original,interrupted,regs,endpoint):
        nonlocal continuations
        t=fork(original);c=base(memory=t,pc=regs[5]);c.a,c.x,c.y,c.p,c.sp=regs[:5];a,ma=interrupted;ma._owner_isr=False
        for _ in range(600000):
            if(c.pc,c.sp)in endpoint and(a.pc,a.sp)in endpoint:break
            assert(c.a,c.x,c.y,c.p&239,c.sp,c.pc)==(a.a,a.x,a.y,a.p&239,a.sp,a.pc)
            assert t[c.pc]and ma[a.pc];c.step();a.step()
        else:raise AssertionError('Reached real Main/public return continuation bound')
        assert(c.a,c.x,c.y,c.p&239,c.sp,c.pc)==(a.a,a.x,a.y,a.p&239,a.sp,a.pc)
        assert[bytes(v)for v in t.ram]==[bytes(v)for v in ma.ram]
        assert transport(t)==transport(ma)and critical(t)==critical(ma)
        assert bytes(t[0x101+regs[4]:0x200])==bytes(ma[0x101+regs[4]:0x200]);continuations+=1
    def pair(cpu,kind,endpoint):
        nonlocal minimum
        regs=(cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp,cpu.pc);machines=[];prior=[]
        for old in(False,True):
            m=fork(cpu.memory,old);c=base(memory=m,pc=cpu.pc);c.a,c.x,c.y,c.p,c.sp=regs[:5]
            prior.append(dict(private=[bytes(v)for v in m.ram],transport=transport(m),critical=critical(m),native=bytes(m[:0x800]),upper=bytes(m[0x101+c.sp:0x200]),skip=N.get(m,'NmiSkipped')))
            m._owner_isr=True;c.irq()if kind=='IRQ'else c.nmi();machines.append((c,m))
        for _ in range(100000):
            a,ma=machines[0];b,mb=machines[1];minimum=min(minimum,a.sp,b.sp)
            assert(a.a,a.x,a.y,a.p&239,a.sp,a.pc)==(b.a,b.x,b.y,b.p&239,b.sp,b.pc)
            if(a.pc,a.sp)==(regs[5],regs[4]):break
            assert a.sp<=regs[4]and ma.rawtags==mb.rawtags and ma[a.pc]
            assert bytes(ma[a.pc:a.pc+3])==bytes(mb[b.pc:b.pc+3]);a.step();b.step()
        else:raise AssertionError('Paired actual IRQ/NMI RTI bound')
        assert(a.a,a.x,a.y,a.p&239,a.sp,a.pc)==(*regs[:3],regs[3]&239,*regs[4:])
        native=[]
        for(c,m),before in zip(machines,prior,strict=True):
            m._owner_isr=False;assert not m._owner_changed_reads
            assert[bytes(v)for v in m.ram]==before['private']and transport(m)==before['transport']and critical(m)==before['critical']
            assert bytes(m[0x101+regs[4]:0x200])==before['upper']
            assert N.get(m,'NmiSkipped')==(before['skip']+(kind=='busyNMI'))&255
            native.append(bytes(m[:0x800]))
        assert native[0]==native[1],'Exact installed-parent native audio/ISR effects differ'
        for at,(old,new)in enumerate(zip(prior[0]['native'],native[0])):
            if old!=new and not 0x100<=at<0x200:effects[kind,at,old,new]+=1
        continuation(cpu.memory,machines[0],regs,endpoint);counts[kind]+=1
    class CPU(base):
        def step(self):
            m=self.memory
            if self.pc in PCS and m.rawtags[1]==207 and m.bundle.get('raw')is raw and(probe or self.sp>=224 and N.get(m,'OperMode')==1 and N.get(m,'GameEngineSubroutine')==8):
                key=(self.pc,N.get(m,'SelectedCharacter'),N.get(m,'PlayerStatus'),probe or'Main')
                if key not in seen:
                    seen.add(key);assert len(seen)<96
                    endpoint={(0x5b00,224)}if probe else{(0x82be,252),(0x82d0,252)}
                    if not self.p&4:pair(self,'IRQ',endpoint)
                    if N.get(m,'NmiDisable')==255:pair(self,'busyNMI',endpoint)
                    cuts.append(dict(PC=self.pc,SP=self.sp,P=self.p,owner=N.get(m,'SelectedCharacter'),power=N.get(m,'PlayerStatus'),scope=probe or'actual Main'))
            return super().step()
    family=F.family();opening=[]
    def cold(image,key):m,q=F.Current.cold(image,True);opening.append(q);return m
    with patch.object(N,'NesMPU',CPU),patch.object(Runner,'Factory',family),patch.object(Runner,'cold',cold),patch.object(Runner,'strict_metadata',family.metadata):route=Model.run(raw,'mini',5100)
    assert route['passed']
    # Only if natural Main did not reach a shifted handled instruction, use
    # its real compiled visible public caller on a genuine cold arena.
    with patch.object(N,'NesMPU',CPU):
        if not{0xaafd,0xb544,0xb545,0xb546,0xb547,0xb54a,0xb54b}<={q['PC']for q in cuts}:
            seed,_=F.Current.cold(raw,True);probe='actual compiled visible9 caller';Public.public(seed,9,p=0x31);probe=None
        roll,roll_opening=Public.cold_owner(raw,9,roll=True)
        for _ in range(8):roll.controller_pad=0;F.Current.Frames.frame(roll,whole_pass=True)
        if 0xb53a not in{q['PC']for q in cuts}:
            probe='actual compiled Roll34 caller';Public.public(roll,34,p=0x31);probe=None
    reached={q['PC']for q in cuts};assert PCS<=reached,(PCS-reached,cuts)
    assert counts['IRQ']and counts['busyNMI']and continuations==sum(counts.values())
    q=dict(passed=True,ROM_SHA256=C.CANDIDATE,genuine_earnedF_two_shot_receipt=route['source_receipt_SHA256'],
        paired_interrupt_counts=dict(counts),reached_contexts=cuts,minimum_ISR_SP=minimum,complete_Main_or_public_return_continuations=continuations,
        exact_parent_native_audio_effects=True,no_native_RAM_allowlist=True,no_owned_code_ISR_reads=True,
        SMC_scratch_maps_private_and_above_entry_stack_preserved=True,Roll_opening=roll_opening,
        native_effects=[dict(kind=k[0],address=k[1],before=k[2],after=k[3],cases=v)for k,v in sorted(effects.items())],
        outputs=0,Mesen=False,scope='Reached actual Main plus explicitly named compiled public component callers; paired ISR RTI and uninterrupted candidate continuation, no deepest nested ISR/hardware cadence claim')
    q['receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    parent=C.ROM.read_bytes()
    def deny(*a,**kw):raise AssertionError('Mini reached ISR attempted artifacts/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny),patch.object(Runner.Native,'run',deny):q=run(parent)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
