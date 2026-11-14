"""Every granted foreground instruction: actual native IRQ/busy-NMI cuts."""
from collections import Counter
from hashlib import sha256
import json
from py65.disassembler import Disassembler

import compose_dkjr_oneway_support_1114 as S
import check_dkjr_oneway_components_1114 as K
import check_dkjr_platform_query_lifecycle_1114 as Life
import check_dkjr_retire_lease_1113 as Lease

F,G=K.F,K.G
Q,P,H,N,W,L,C=K.Q,K.P,K.H,K.N,K.W,K.L,K.C


def main():
    _,parent=F.load_inputs();raw,_=S.proposal(parent);_,labels=Life.closure(parent)
    _,seed=H.cold(raw,raw[P.B.COOKIE_AT:P.B.COOKIE_AT+16]);C.SLOT=3
    base=C.setup(Q.mounted(seed,raw));base.raw_page(1,3);base.raw_page(2,2)
    N.put(base,NmiDisable=255);base.ram[2][0x8fe]=2;base[0x6de]=32
    for i in range(4):
        at=0x210+8*i;y=120+8*(i//2);tile=2*i;x=40+8*(i&1)
        base.ram[2][at:at+8]=bytes((y,tile,0x20,x,y+8,tile+1,0x20,x))
    for name,value in dict(Enemy_Flag=1,Enemy_ID=47,Enemy_State=0,Enemy_X_Position=176,
        Enemy_PageLoc=3,Enemy_Y_Position=96,Enemy_Y_HighPos=1).items():base[W.address(base.bundle,name)+5]=value
    for name,value in dict(Vine_FlagOffset=1,Vine_ObjOffset=5,Vine_Height=48,Vine_Start_Y_Position=144).items():base[labels[name]]=value
    base[labels['Vine_ObjOffset']+1]=255
    base.ram[2][0x3e:0x42]=bytes((100,96,116,112))
    body=P.T.payload(raw);flat=bytearray(65536)
    flat[0xa000:0xc000]=body[:8192];flat[0xc900:0xcd00]=body[8192:9216];flat[0xd000:0xd800]=body[9216:]
    dis=Disassembler(N.NesMPU(memory=flat));emitted=set()
    for bank,lo,hi in((2,0xcbe0,0xcc20),(2,0xcc60,0xcc7d),(3,0xbc74,0xbd3d),
        (2,0xd65e,0xd6a7),(3,0xb4b0,0xb54e)):
        pc=lo
        while pc<hi:
            emitted.add((bank,pc));size,_=dis.instruction_at(pc);pc+=size
        assert pc==hi,(hex(lo),hex(pc),hex(hi))
    fixtures=[]
    def fixture(name,pc,changes=(),a=85):fixtures.append((name,pc,list(changes),a))
    body_cases=[[],[(0xc8fe,0)],[(0x6de,33)],[(0x6de,240)],[(0xc210,240)],[(0xc214,129)],
        [(0xc211,3)],[(0xc211,88)],[(0xc215,3)],[(0xc212,128)],[(0xc216,0)],[(0xc217,41)],
        [(0x6c0b,1),(0x6c08,17)]]
    for i,changes in enumerate(body_cases):fixture('body'+str(i),0xbc74,changes)
    for state in(0,1,2,3,4,5):fixture('Main'+str(state),0xd65e,[(0xc06b,state)])
    fixture('MainNoAnchor',0xd65e,[(0xc8fe,0)])
    for state in(1,2,3,4,5):fixture('guard-state'+str(state),0xcc14,[(0xc06b,state),(0xc082,88),(0xc083,0),(0xc086,96),(0xc087,1)])
    fixture('guard-descending',0xcc14,[(0xc06b,3),(0xc082,88),(0xc083,2),(0xc086,96),(0xc087,1)])
    # Every preserved retirement guard and both old geometry decisions.
    slot=3
    retire=[(0x6002,40),(0x764,0),(0x761,0),(0xd6,0xce),(0x10+slot,1),(0x17+slot,37),
        (0x1f+slot,0),(0x646+slot,5),(0x566+slot,255),(0x76+slot,16),(0x5d+slot,3)]
    fixture('retire',0xcbe0,retire)
    for at,value in((0x6002,41),(0x764,1),(0x761,1),(0xd6,0),(0x10+slot,0),(0x17+slot,36),
        (0x1f+slot,1),(0x646+slot,6),(0x566+slot,0),(0x76+slot,176),(0x5d+slot,2),(0x76+slot,64)):
        changes=dict(retire);changes[at]=value;fixture('retire-guard'+hex(at),0xcbe0,changes.items())
    # Real hook preserves AXYP around all native World paths.
    hook=labels['DkjrNativeTerrainHook']
    for kind in range(5):fixture('world-kind'+str(kind),hook,[(0xc06b,1)],kind)
    fixture('world-rising',hook,[(0xc06b,3),(0xc082,88),(0xc083,0),(0xc086,96),(0xc087,1)],3)
    for name,values in dict(Vine_FlagOffset=(0,1,2,3),Vine_Height=(0,7,8,48,49,95,96,97),
        Vine_ObjOffset=(0,5)).items():
        for value in values:fixture(name+str(value),hook,[(labels[name],value)],0)
    for name,values in dict(Enemy_Flag=(0,128),Enemy_ID=(0,47),Enemy_Y_HighPos=(0,1),
        Enemy_X_Position=(0,176,247,248),Enemy_PageLoc=(2,3,4),Enemy_Y_Position=(0,31,32,96,240)).items():
        for value in values:fixture(name+str(value),hook,[(W.address(base.bundle,name)+5,value)],0)
    fixture('vine-second-root',hook,[(labels['Vine_FlagOffset'],2),(labels['Vine_ObjOffset'],0),(labels['Vine_ObjOffset']+1,5)],0)
    fixture('vine-bad-bottom',hook,[(labels['Vine_Start_Y_Position'],32)],0)
    fixture('vine-clamped-bottom',hook,[(labels['Vine_Start_Y_Position'],255)],0)
    points={};reference={};reads=set();writes=set();active=False;dead_stack=set()
    Base=type(base)
    class Bus(Base):
        def __getitem__(self,at):
            if active and isinstance(at,int)and at in dead_stack:
                assert at in writes,('discarded ISR stack read before a new writer',hex(at))
            if active and isinstance(at,int):reads.add(at)
            return super().__getitem__(at)
        def __setitem__(self,at,value):
            if active and isinstance(at,int):writes.add(at)
            return super().__setitem__(at,value)
    base.__class__=Bus
    def run(index,cut=None):
        nonlocal active,dead_stack
        dead_stack=set()
        name,pc,changes,a=fixtures[index];m=L.clone(base);m.raw_page(1,3);m.raw_page(2,2)
        for at,value in changes:m[at]=value
        hit=False;minimum=255;changed=set()
        def watch(memory,cpu):
            nonlocal active,hit,minimum,changed,dead_stack
            active=True;tag=memory.rawtags[(cpu.pc-0x8000)//8192]if cpu.pc>=0x8000 else-1
            token=(tag,cpu.pc,cpu.p&4)
            if(tag,cpu.pc)in emitted:
                points.setdefault(token,index)
                if cut and not hit and token==cut[1]:
                    active=False;before=bytes(memory[:0x10000]);live=bytes(memory[0x101+cpu.sp:0x200])
                    minimum,_=Lease.inject_checked(cpu,cut[0])
                    assert bytes(memory[0x101+cpu.sp:0x200])==live,(name,cut,'live stack')
                    changed={at for at in range(0x10000)if memory[at]!=before[at]}
                    dead_stack={at for at in changed if 0x100<=at<=0x100+cpu.sp}
                    hit=True;reads.clear();writes.clear();active=True
        c=H.call(m,pc,a=a,x=slot if pc==0xcbe0 else 71,y=91,p=0x61,observe=watch);active=False
        assert hit==(cut is not None),(name,cut,hit)
        return m,c,minimum,changed
    for i in range(len(fixtures)):
        m,c,*_=run(i);reference[i]=(m,c)
    reached={(bank,pc)for bank,pc,_ in points};missing=emitted-reached
    print('DKJR_ONEWAY_VECTOR_COVERAGE '+json.dumps(dict(emitted=len(emitted),reached=len(reached),
        missing=[(bank,hex(pc),dis.instruction_at(pc)[1])for bank,pc in sorted(missing)])),flush=True)
    assert not missing,('Unreached granted instructions',sorted(missing))
    counts=Counter();minimum=255;changes_total=Counter();synthetic_B_differences=0
    for number,(point,index)in enumerate(list(points.items())):
        for kind in('IRQ','lagNMI'):
            if kind=='IRQ'and point[2]:continue
            reads.clear();writes.clear();m,c,low,changed=run(index,(kind,point));ref,rc=reference[index]
            # B is not a physical 6502 status latch. py65's RTI materializes
            # it as1; IRQ/NMI component oracles in this repo compare P&EF.
            # Keep every real C/Z/I/D/V/N bit exact and retain all saved
            # hardware-stack bytes in the independent live-stack assertion.
            synthetic_B_differences+=int(c.p!=rc.p)
            assert(c.a,c.x,c.y,c.p&0xef,c.sp,c.pc)==(rc.a,rc.x,rc.y,rc.p&0xef,rc.sp,rc.pc),(kind,point,'ABI',
                (c.a,c.x,c.y,c.p,c.sp,c.pc),(rc.a,rc.x,rc.y,rc.p,rc.sp,rc.pc))
            assert tuple(map(bytes,m.ram))==tuple(map(bytes,ref.ram)),(kind,point,'private RAM')
            assert m.rawtags==ref.rawtags and bytes(m[0x15a:0x17b])==bytes(ref[0x15a:0x17b]),(kind,point,'maps/SMC')
            assert bytes(m[0x200:0x300])==bytes(ref[0x200:0x300]),(kind,point,'OAM')
            assert bytes(m.vram)==bytes(ref.vram)and m.chr_latches==ref.chr_latches,(kind,point,'graphics')
            # Only data cells matter here; MMIO latches and discarded hardware
            # stack are not foreground source inputs. Every actual data read
            # of an ISR change is reported rather than hidden.
            consumed={at for at in changed&reads if at<0x100 or 0x200<=at<0x800 or 0x5c00<=at<0x8000}
            assert not consumed,(kind,point,'foreground consumes ISR-changed data',sorted(consumed))
            for at in changed:
                if not 0x100<=at<0x200:changes_total[hex(at)]+=1
            minimum=min(minimum,low);counts[kind]+=1
        if number%40==0:print('DKJR_ONEWAY_VECTOR_PROGRESS '+json.dumps(dict(done=number+1,total=len(points))),flush=True)
    print('DKJR_ONEWAY_VECTORS '+json.dumps(dict(passed=True,candidate_SHA256=S.PIN,
        emitted_instruction_PCs=len(emitted),all_emitted_reached=True,cut_points=len(points),cuts=dict(counts),
        minimum_ISR_SP=minimum,complete_live_stack_RTI_and_foreground_ABI_private_RAM_OAM_SMC_maps_graphics_exact=True,
        real_P_flags_CZIDVN_exact=True,reported_synthetic_B_latch_differences=synthetic_B_differences,
        discarded_ISR_stack_continuation_reader_after_writer=True,
        ISR_native_changes_not_read_by_continuation=dict(changes_total),outputs_written=0,ROM_written=False,
        scope='Declared actual private body/Main/World/Vine/retire components with every granted instruction reached, real current IRQ/busy-NMI and component continuation. Full controller/current421/native gates are separate.'),separators=(',',':')),flush=True)


if __name__=='__main__':main()
