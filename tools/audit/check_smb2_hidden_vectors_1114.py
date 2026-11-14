"""Actual source-frame probe callers and parent ISR oracle; zero artifacts."""
from collections import Counter
from hashlib import sha256
import json
from py65.disassembler import Disassembler
from unittest.mock import patch

import replay_smb2_hidden_response_1114 as Replay
import check_smb2_flag_handoff_1113 as Family
import check_smb2_postbg_irq_1113 as ISR

C=Replay.C
W,N=C.W,C.N


def copy_cpu(m,c,native):
    z=native(memory=m,pc=c.pc)
    for name in('a','x','y','p','sp'):setattr(z,name,getattr(c,name))
    return z


def finish(c,native,stop=None):
    if stop is None:stop=(W.address(c.memory.bundle,'IdleLoop')+12,252)
    for _ in range(500000):
        if(c.pc,c.sp)==stop:return
        assert c.memory[c.pc],('Actual resumed Main BRK',hex(c.pc),c.sp)
        native.step(c)
    raise AssertionError('Actual resumed Main bound')


def interrupt(m,c,parent,image,kind,native,stop=None):
    a=Family.view(m,image);b=Family.view(m,parent)
    ca,cb=copy_cpu(a,c,native),copy_cpu(b,c,native)
    expected=ISR.regs(c);protected=(bytes(m[3:11]),bytes(m[0x15a:0x17b]),bytes(m[0x101+c.sp:0x200]))
    at=W.address(m.bundle,'S2AudioState');music_before=bytes(m[at:at+77]);low=255
    assert N.get(m,'NmiDisable')==255
    for mm,cc in((a,ca),(b,cb)):
        maps=tuple(mm.rawtags);skip=N.get(mm,'NmiSkipped')
        cc.irq()if kind=='IRQ'else cc.nmi()
        for _ in range(150000):
            low=min(low,cc.sp)
            if(cc.pc,cc.sp)==(c.pc,c.sp):break
            tag=mm.rawtags[(cc.pc-0x8000)//8192]if cc.pc>=0x8000 else -1
            assert not(tag==246 and(0xb128<=cc.pc<0xb1d6 or 0xa637<=cc.pc<0xa640 or
                0xb86b<=cc.pc<0xb86f or 0xbc96<=cc.pc<0xbca4)),'ISR entered foreground probe code'
            assert mm[cc.pc],('Actual parent ISR BRK',kind,hex(cc.pc),cc.sp)
            native.step(cc)
        else:raise AssertionError('Actual parent ISR return bound')
        assert ISR.regs(cc)==expected
        assert(bytes(mm[3:11]),bytes(mm[0x15a:0x17b]),bytes(mm[0x101+cc.sp:0x200]))==protected
        assert tuple(mm.rawtags)==maps
        assert N.get(mm,'NmiSkipped')==(skip+(kind=='busyNMI'))&255
    assert ca.processorCycles==cb.processorCycles
    assert ISR.full_state(a)==ISR.full_state(b)and a.writes==b.writes and a.ram_writes==b.ram_writes
    advanced=bytes(a[at:at+77])!=music_before
    b=Family.view(b,image);cb.memory=b
    finish(ca,native,stop);finish(cb,native,stop)
    assert ISR.regs(ca)==ISR.regs(cb)and ISR.full_state(a)==ISR.full_state(b)
    assert a.writes==b.writes and a.ram_writes==b.ram_writes
    return low,advanced


def vectors():
    parent=C.Cache.parent_image();image,info=C.proposal(parent)
    _,spans,_=C.bindings(parent)
    synthetic=bytearray(65536)
    for at,old,new in spans:synthetic[0xa000+(at-16)%8192:0xa000+(at-16)%8192+len(new)]=new
    dis=Disassembler(N.NesMPU(memory=synthetic));required=set();regions=[]
    for at,old,new in spans:
        lo=0xa000+(at-16)%8192;hi=lo+len(new);regions.append((lo,hi))
        pc=lo
        while pc<hi:
            size=dis.instruction_at(pc)[0]
            if synthetic[pc]!=0xea and bytes(synthetic[pc:pc+size])!=old[pc-lo:pc-lo+size]:required.add(pc)
            pc+=size
        assert pc==hi
    native=N.NesMPU;seen=set();reached=set();counts=Counter();minimum=255;music=0;busy_seed=None
    class Observed(native):
        def step(self):
            nonlocal minimum,music,busy_seed
            m=self.memory
            tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else -1
            relevant=tag==246 and any(lo<=self.pc<hi for lo,hi in regions)
            if relevant and N.get(m,'NmiDisable')==255 and N.get(m,'GameEngineSubroutine')==8:
                if busy_seed is None:busy_seed=N.fork(m)
                key=(self.pc,self.sp,N.get(m,'S2Clock')&8,self.p&4)
                if key not in seen:
                    seen.add(key);reached.add(self.pc)
                    for kind in('IRQ','busyNMI'):
                        if kind=='IRQ'and self.p&4:continue
                        low,advanced=interrupt(m,self,parent,image,kind,native)
                        minimum=min(minimum,low);music+=advanced;counts[kind]+=1
            return native.step(self)
    with patch.object(N,'NesMPU',Observed):q=Replay.source_run(image,0)
    genuine_reached=set(reached);missing=required-reached
    assert q['passed']and counts['IRQ']and counts['busyNMI']and music and minimum>=128
    assert missing=={0xa63a,0xa63c,0xb1a9},('Unexpected genuine instruction gap',missing)
    # Both current literal callers force playerX0. The nonplayer predicate is
    # a defensive public probe ABI, so its source/IRQ proof is an explicitly
    # directed primitive query unit, never a claimed natural object contact.
    bank=image[16+118*8192:16+119*8192]
    calls=[0xa000+i for i in range(8190)if bank[i:i+3]==bytes.fromhex('2028b1')]
    b=dict(W.Symbols.bundle(),raw=image)
    expected=[W.address(b,n)for n in('S2N8E35','S2N8FB9')]
    assert sorted(calls)==sorted(expected)
    assert bank[calls[0]-0xa000-2:calls[0]-0xa000]==bytes.fromhex('a200')
    assert bank[calls[1]-0xa000-5:calls[1]-0xa000-3]==bytes.fromhex('a200')
    unit_seen=set();unit_counts=Counter()
    fixture=Family.view(busy_seed,image)
    base=W.address(fixture.bundle,'Block_Buffer_1')
    for i in range(416):fixture[base+i]=96
    for owner in range(4):
        for name,value in(('S2X',112),('S2Page',0),('S2Y',112),('S2YPage',0)):
            fixture[W.address(fixture.bundle,name)+owner]=value
    N.put(fixture,S2VY=128,S2ProbeDirection=0,S2HeadY=0)
    class Directed(native):
        def step(self):
            nonlocal minimum,music
            if self.pc in missing and self.memory.rawtags[1]==246:
                key=(self.pc,self.sp)
                if key not in unit_seen:
                    unit_seen.add(key);reached.add(self.pc)
                    for kind in('IRQ','busyNMI'):
                        if kind=='IRQ'and self.p&4:continue
                        low,advanced=interrupt(self.memory,self,parent,image,kind,native,(0x5b00,224))
                        minimum=min(minimum,low);music+=advanced;unit_counts[kind]+=1
            return native.step(self)
    with patch.object(N,'NesMPU',Directed):
        N.invoke(fixture,'S2NativeTileProbe',x=1,y=6,p=0x31)
    assert required<=reached and unit_counts['IRQ']==unit_counts['busyNMI']==3
    return dict(passed=True,ROM_SHA256=info['ROM_SHA256'],natural_Mario_passed=q['passed'],
        controller_SHA256=q['controller_SHA256'],reached_instruction_SP_clock_points=len(seen),
        actual_parent_ISR_cuts=dict(counts),minimum_SP=minimum,paired_real_music_advances=music,
        changed_or_new_instruction_PCs=sorted(required),unreached_new_instruction_PCs=sorted(required-reached),
        genuine_new_instruction_PCs=sorted(required&genuine_reached),
        directed_defensive_ABI_only_instruction_PCs=sorted(missing),directed_ABI_vector_cuts=dict(unit_counts),
        actual_current_probe_callers=calls,current_callers_both_force_playerX0=True,
        defensive_ABI_fixture='Genuine busy Main memory/audio prefix; explicit owner1 query coordinates and tile60 buffer; no natural object-contact claim',
        genuine_menu_controller_Main_NMI_frames=True,
        exact_parent_ISR_and_complete_candidate_Main_continuations=True,
        AXYP_SP_live_stack_SMC_RAM_WRAM_maps_peripherals_ordered_writes_exact=True,
        live_state_masks_or_repairs=0,outputs=0,Mesen_run=False)


if __name__=='__main__':
    q=vectors();print(json.dumps(q,separators=(',',':')),flush=True)
    assert q['passed'],'All new instruction vector coverage remains required'
