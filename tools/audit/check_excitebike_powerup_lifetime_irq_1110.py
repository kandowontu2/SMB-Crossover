"""Explicit ABI, full-cookie rejection and real-vector cuts for raw37 tick.

All cases are labelled directed CPU fixtures; earned-controller evidence is
in the separate progression checker. No ROM or generated receipt is written.
"""
from collections import Counter
from hashlib import sha256
import json

import check_excitebike_powerup_progression_1110 as P

C,W,L,N=P.C,P.W,P.L,P.N
COUNTS=Counter()


def alias(b):
    # The current source Ex veneer table is physically unchanged. Select
    # this typed entry directly for foreign-owner rejection checks; routing
    # HuPowerup for a different real owner would intentionally call theirs.
    b=dict(b,syms=dict(b['syms']),segs=dict(b['segs']))
    b['segs']['EX_TEST_ROM']={'start':str(0xa000),'ooffs':str(16+65*8192)}
    base=16+65*8192
    assert b['raw'][base+0x75e]==0x20
    current_check=int.from_bytes(b['raw'][base+0x75f:base+0x761],'little')
    assert current_check==0xaee2
    for name,pc in (('ExDirectTick',0xb0ef),('ExDirectCheck',current_check)):
        b['syms'][name]={'val':str(pc),'seg':'EX_TEST_ROM'}
    return b


def prepared(seed,age=5,tier=0):
    m=L.clone(seed)
    N.put(m,NmiDisable=255,GuestPowerupActive=1,GuestPowerupAge=age,GuestPowerupOld=tier,
        GuestPowerupDisplay=tier,GuestPowerupTarget=min(2,tier+1),GameEngineSubroutine=9,TimerControl=255)
    return m


def abi(seed):
    for age in (0,1,19,35,47,58,59,60):
      for tier in (0,1,2):
       for flags in (0x30,0x31,0x74,0xf1):
        old,new=prepared(seed,age,tier),prepared(seed,age,tier)
        a=L.call(old,'GuestPowerupUpdate',a=83,x=71,y=37,p=flags)
        z=L.call(new,'ExDirectTick',a=83,x=71,y=37,p=flags)
        assert (a.a,a.x,a.y,a.p,a.sp)==(z.a,z.x,z.y,z.p,z.sp),(age,tier,flags,L.regs(a),L.regs(z))
        assert L.app(old)==L.app(new),(age,tier,flags,'native application state')
        COUNTS['exact_native_GuestPowerupUpdate_ABI_and_application']+=1
    for flags in range(256):
        m=L.clone(seed);N.put(m,NmiDisable=255)
        before=L.app(m);c=L.call(m,'ExDirectTick',a=83,x=71,y=37,p=flags)
        assert L.app(m)==before and c.x==71 and c.y==37 and c.sp==224
        COUNTS['inactive_all256_P_noop']+=1


def rejection(seed,record):
    for bank in (2,3):
      for byte in range(16):
       for bit in range(8):
        m=prepared(seed);m.ram[bank][0x1fe0+byte]^=1<<bit
        before=L.app(m);c=L.call(m,'ExDirectTick',a=83,x=71,y=37,p=0xf1)
        # Actual FarCallCommon reloads original A=$53 before the public
        # veneer, so its defined N/Z are0 at ExDispatch's saved-P boundary.
        assert L.app(m)==before and (c.a,c.x,c.y,c.p,c.sp)==(83,71,37,0x70,224),(bank,byte,bit,L.regs(c),[a==z for a,z in zip(L.app(m),before)])
        assert not m.ppu_reads-seed.ppu_reads
        COUNTS['each_bit_both_full16byte_headers_fail_closed']+=1
    for owner in range(256):
        if owner==37:continue
        m=prepared(seed);N.put(m,SelectedCharacter=owner)
        before=L.app(m);c=L.call(m,'ExDirectTick',a=83,x=71,y=37,p=0x71)
        assert L.app(m)==before and (c.a,c.x,c.y,c.p,c.sp)==(83,71,37,0x70,224)
        COUNTS['all255_foreign_owners_direct_Ex_veneer_reject']+=1
    m=prepared(seed)
    for bank in (2,3):m.ram[bank][0x1fe0:0x1ff0]=bytes.fromhex(record['old_cookie'])
    before=L.app(m);c=L.call(m,'ExDirectTick')
    assert not c.p&1 and L.app(m)==before
    COUNTS['previous_revision_warm_cache_rejected']+=1
    m=L.clone(seed);reads=m.ppu_reads;c=L.call(m,'ExDirectCheck')
    assert c.p&1 and m.ppu_reads==reads
    COUNTS['new_complete_warm_check_zero_PPU_reads']+=1


def pause(seed):
    m=prepared(seed);N.put(m,GamePauseStatus=1)
    for _ in range(4):
        m.controller_pad=0;P.Route.frame(m)
        assert (N.get(m,'GuestPowerupAge'),N.get(m,'GuestPowerupActive'))==(5,1)
    N.put(m,GamePauseStatus=0)
    m.controller_pad=0;P.Route.frame(m)
    assert N.get(m,'GuestPowerupAge')==6
    COUNTS['real_Main_pause4_then_resume1']+=1


def interrupts(seed,parent):
    L.SAMPLES.clear();L.SAMPLE_KEYS.clear();L.PATHS.clear();L.DEEPEST=None
    seen=set()
    for age in (0,59):
      for flags in (0x31,0x35):
        m=prepared(seed,age);c=L.start(m,'ExDirectTick',p=flags)
        def observe(mem,cpu):
            if cpu.pc>=0x8000 and mem.rawtags[(cpu.pc-0x8000)//8192]==3 and (cpu.pc==0xa563 or 0xaf7a<=cpu.pc<0xaf8c):
                key=(age,flags,cpu.pc)
                if key not in seen:
                    seen.add(key);q,d=L.clone(mem,cpu)
                    L.SAMPLES.append(('actual_Ex_tick_age'+str(age),(0x5b00,224),q,d))
        L.finish(m,c,(0x5b00,224),observe)
    expected={0xa563,0xaf7a,0xaf7d,0xaf7f,0xaf82,0xaf84,0xaf87,0xaf89}
    assert {pc for age,flags,pc in seen}==expected,seen
    result=L.irq_checks(parent)
    assert result['instruction_seams']==32
    return result


def main():
    parent=C.ROM.read_bytes();image,kernel,cookie,record=P.proposal(parent)
    b=W.Symbols.bundle();b['raw']=image
    row=next(r for r in C.Starts.C.inventory(image)['rows'] if r['name']=='EXCITEBIKE')
    opening,m=C.cold(b,row);m.bundle=alias(m.bundle)
    assert image[16+65*8192+0x10ef:16+65*8192+0x10f2]==bytes.fromhex('4c40a7')
    abi(m);rejection(m,record);pause(m)
    vectors=interrupts(m,parent)
    print(json.dumps(dict(passed=True,source_CPU_only=True,Mesen_run=False,output_files=0,ROM_written=False,
        parent_ROM_SHA256=C.PIN,proposal_ROM_SHA256=sha256(image).hexdigest(),
        checker_SHA256=sha256(__import__('pathlib').Path(__file__).read_bytes()).hexdigest(),
        cases=dict(COUNTS),vectors=vectors,source_proposal=record,
        scope='Directed native row33 ABI compared to original GuestPowerupUpdate, all header bits/foreign owners, actual paused Main, and paired real NMI/IRQ at every newly executed instruction. Separate ordinary-controller route qualifies natural mushroom. No physical Mesen or all-powerup/fullstage claim.')),flush=True)


if __name__=='__main__':main()
