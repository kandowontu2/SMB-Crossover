"""Real IRQ/FF and regular-NMI source cuts for the native Sonic skin."""
from collections import Counter

import check_sonic_sms_native_prototype_1110 as S
import check_mini_lift_admission_async_1108_v1 as Q
from check_mini_funded_actor_1108_v3 import registers,run,slim_fork
from check_mini_shared_offscreen_irq_1110_v1 import lag_pcs
from check_native_relative_offscreen_irq_1110 import StackGuard

P,N,R=S.P,S.N,S.R


def vectors(before,after,name_entry):
    bundles=[S.Current.W.bundle(r) for r in (before,after)]
    old,new=bundles
    previous=N.Bus;N.Bus=StackGuard
    try:
        seed=S.body_seed(new)
    finally:N.Bus=previous
    P.frame(seed,0)
    lag,regular=lag_pcs(seed)
    counts=Counter();deepest={};sites=set();minima=[255,255]
    spans=((190,0xb690,0xb693),(190,0xb6cb,0xb6ec),(190,0xb70e,0xb716),
           (190,0xbb9c,0xbba7),(190,0xa9c0,0xaa00),(190,0xbaa4,0xbaf9),
           (194,0xac7d,0xaca5),(194,0xacc0,0xacd2),(225,0xa307,0xa38c))

    def clone(c,base=False):
        m=slim_fork(c.memory)
        if base:
            m.bundle=old
            for window in range(4):m.raw_page(window,m.rawtags[window])
        z=N.NesMPU(memory=m,pc=c.pc)
        z.a,z.x,z.y,z.p,z.sp=registers(c)
        return z

    def interrupt(c,kind):
        snapshot=Q.live(c);ret=(c.pc,c.sp);out=[]
        vram=bytes(c.memory[0x4ae:0x504])
        for baseline in (False,True):
            z=clone(c,baseline);m=z.memory
            m.vector_floor,m.written_stack=0x100+z.sp,set()
            skipped=N.get(m,'NmiSkipped')
            if kind=='lag_FF':
                assert N.get(m,'NmiDisable')==255;z.nmi()
            else:
                assert not z.p&4;z.irq();assert z.pc==0x8000
            hits=0
            def observe(q):
                nonlocal hits
                minima[1]=min(minima[1],q.sp)
                if kind!='lag_FF':return
                assert q.pc!=regular
                hits+=q.pc==lag
                if not baseline and not q.p&4:
                    key=Q.tags(q),q.pc,q.a,q.p&1
                    if key not in deepest or q.sp<deepest[key].sp:
                        deepest[key]=clone(q);deepest[key].memory.vector_floor=None
            run(z,lambda q:(q.pc,q.sp)==ret,observe)
            m.vector_floor=None
            assert bytes(m[0x4ae:0x504])==vram,(kind,'VRAMqueue',hex(c.pc))
            assert hits==int(kind=='lag_FF')
            assert N.get(m,'NmiSkipped')==(skipped+int(kind=='lag_FF'))&255
            actual=Q.live(z)
            if actual!=snapshot:
                assert bytes(c.memory[c.pc-3:c.pc+3])==bytes.fromhex('8d45018d1551'),(
                    kind,hex(c.pc),N.get(c.memory,'MarioVariant'),
                    [(i,str(a)[:160],str(b)[:160])for i,(a,b)in enumerate(zip(snapshot,actual))if a!=b])
                assert actual[0]==snapshot[0] and actual[2:]==snapshot[2:]
                assert actual[1][1]==snapshot[2] and actual[1][:1]+actual[1][2:]==snapshot[1][:1]+snapshot[1][2:]
                if not baseline:counts['exact_pending_A_bus_store']+=1
            out.append((z,tuple(m.writes),tuple(m.ram_writes)))
        assert out[0][1:]==out[1][1:],(kind,hex(c.pc))
        counts[kind]+=1
        return out[0][0]

    def exercise(c,stop,domain):
        cuts=set();resumes=[]
        def cut(z):
            tag,pc=Q.tags(z),z.pc
            if not domain(z):return
            if not (0x15a<=pc<0x17b or any(tag==t and lo<=pc<hi for t,lo,hi in spans)):return
            key=tag,pc,z.sp,z.p&4,tuple(z.memory.rawtags)
            if key in cuts:return
            cuts.add(key);sites.add((tag,pc));minima[0]=min(minima[0],z.sp)
            if N.get(z.memory,'NmiDisable')==255:
                resumes.append(interrupt(z,'lag_FF'))
            else:
                counts['non_FF_transport_cuts_outside_hot_frame']+=1
            if not z.p&4:resumes.append(interrupt(z,'IRQ'))
        run(c,stop,cut)
        assert cuts
        expected=Q.final(c),bytes(c.memory[:11])
        for z in resumes:
            run(z,stop)
            assert (Q.final(z),bytes(z.memory[:11]))==expected,('resume',hex(z.pc),c.sp)
        counts['complete_resumes']+=len(resumes)

    idle,loop,core=(S.address(new,n) for n in ('IdleLoop','GameLoop','GameCoreRoutine'))
    m=slim_fork(seed)
    N.put(m,CrossoverMenuState=0,SavedJoypadBits=65,SavedJoypad1Bits=65,NmiDisable=255)
    c=N.NesMPU(memory=m,pc=idle);c.sp,c.p=255,0x31;c.stPushWord(0xe33b)
    entries={}
    def domain(z):
        if Q.tags(z)==254 and z.pc in (loop,core):entries[z.pc]=z.sp
        return True
    exercise(c,lambda q:(q.pc,q.sp)==(idle+12,252),domain)
    assert entries=={loop:250,core:248},entries
    assert any(t==190 and 0xa9c0<=pc<0xaa00 for t,pc in sites),(
        'RealGameLoopDidNotReachSkin',[(n,N.get(c.memory,n))for n in
        ('SelectedCharacter','MarioVariant','GameEngineSubroutine','ShouldSkipDrawSprites','NmiDisable')],sorted(sites))
    for variant in (3,5,6,10):
        m=slim_fork(seed)
        N.put(m,MarioVariant=variant,NmiDisable=255,VRAM_Buffer1_Offset=0,CurrentBank=190)
        N.invoke(m,'CrossoverGraphicsBank')
        m.raw_page(1,190)
        N.put(m,CurrentBank=190)
        c=N.NesMPU(memory=m,pc=0xbaa4);c.a,c.x,c.y,c.p,c.sp=91,7,43,0x31,224
        c.stPushWord(0x5aff)
        exercise(c,lambda q:(q.pc,q.sp)==(0x5b00,224),lambda z:True)
    m=slim_fork(seed)
    N.put(m,OperMode=0,CrossoverMenuState=2,CrossoverMenuIndex=0,MarioVariant=10,
          SelectedCharacter=0,NmiDisable=255,VRAM_Buffer1_Offset=0,CurrentBank=194)
    m.raw_page(1,194)
    target=S.address(new,'QueueSelection')
    m[0x16a],m[0x16c],m[0x16d]=85,target&255,target>>8
    c=N.NesMPU(memory=m,pc=0x15a);c.a,c.x,c.y,c.p,c.sp=194,7,91,0x31,224
    c.stPushWord(0x5aff)
    exercise(c,lambda q:(q.pc,q.sp)==(0x5b00,224),lambda z:True)
    # Real normal publication reaches the new mode85 mapper; all reachable
    # I0 cuts accept a genuine IRQ and preserve exact post-publication state.
    m=slim_fork(seed);N.put(m,CrossoverMenuState=0,NmiDisable=255)
    N.invoke(m,'GameLoop',a=0,x=0,y=0)
    assert N.get(m,'NmiDisable')==0 and N.get(m,'ReloadCHRBank')
    c=N.NesMPU(memory=m,pc=idle);c.sp,c.p=248,0x31;ret=(c.pc,c.sp);c.nmi()
    regular_cuts=[]
    def normal(q):
        if Q.tags(q)==190 and 0xa9c0<=q.pc<0xaa00:
            sites.add((190,q.pc));counts['normal_NMI_mapper_cuts']+=1
            if not q.p&4:regular_cuts.append(interrupt(q,'IRQ'))
    run(c,lambda q:(q.pc,q.sp)==ret,normal)
    for q in regular_cuts:
        run(q,lambda z:(z.pc,z.sp)==ret)
        assert Q.final(q)==Q.final(c)
    assert counts['normal_NMI_mapper_cuts']
    for q in deepest.values():interrupt(q,'nested_IRQ')
    assert counts['lag_FF'] and counts['IRQ'] and counts['nested_IRQ']
    assert min(minima)>0x7a
    return dict(counts=dict(counts),min_SP=minima,unique_sites=len(sites),
                actual_GameLoop_SP=250,actual_GameCore_SP=248,
                scope='Actual source IRQ/FF at reached skin/transport cuts, strict live '
                      'AXYP/SMC/stack/maps/private/actor state, exact paired handler writes, '
                      'and complete source continuation. RegularNMI mapper IRQ also resumes.')
