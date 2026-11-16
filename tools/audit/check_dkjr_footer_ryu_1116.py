"""Current Ryu27 real-caller, callee and Main liveness before footer routes."""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

import compose_dkjr_platform_footer_current_1116 as C
import check_dkjr_direct_foreign_caller_1113 as Old

Q,N,W,L,V=Old.Q,Old.N,Old.W,Old.L,Old.V
H=lambda value:sha256(value).hexdigest()


def mount(seed,raw):
    m=L.clone(seed);V.bind_rom(m,raw);return m


def native_data(m):
    return (bytes(m[:0x100]),bytes(m[0x200:0x800]),tuple(bytes(q)for q in m.ram),
        tuple(m.rawtags),bytes(m[0x5c00:0x8000]),bytes(m.vram),tuple(m.chr_latches))


def setup(seed,kind,scene,profile=25):
    m=L.clone(seed);slot=3
    N.put(m,SelectedCharacter=10,Player_X_Position=113,Player_PageLoc=0,Player_Y_Position=160,
        Player_Y_HighPos=1,Player_State=1,Player_Y_Speed=252,
        WorldNumber=0,LevelNumber=3 if scene!='ordinary'else 0,AreaType=3,
        SecondaryHardMode=0,GuestHurtTicks=0,RgCrouch=0,RgAttack=0,XgWall=0,RyPlatformSlot=0,
        RyWallSupported=1,RyWallOldHeight=profile,RyWallWasGround=1,RyWallOldX=113,
        RyWallOldPage=0,RyWallOldY=192,RyuSourceBodyProfile=profile,
        ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ObjectOffset=slot)
    for field,value in dict(Enemy_ID=kind,Enemy_Flag=1,Enemy_State=0,Enemy_BoundBoxCtrl=5,
        Enemy_X_Position=111 if scene!='outside'else 200,Enemy_PageLoc=0,
        Enemy_Y_Position=184,Enemy_Y_HighPos=1).items():m[W.address(m.bundle,field)+slot]=value
    N.invoke(m,'RelativePlayerPosition',x=0);N.invoke(m,'HuFullBox',x=0)
    N.invoke(m,'GetEnemyOffscreenBits',x=slot);N.invoke(m,'RelativeEnemyPosition',x=slot)
    N.invoke(m,'LargePlatformBoundBox',x=slot)
    return m


def pair(seed,parent,candidate,kind,scene,*,p=0x31,saved=0,profile=25):
    base=setup(seed,kind,scene,profile);models=[];results=[];events=[]
    for raw in(parent,candidate):
        m=mount(base,raw);m[3]=184;m[0x16a]=saved;calls=[];pending=None
        def watch(cpu):
            nonlocal pending
            tag=m.rawtags[(cpu.pc-0x8000)//8192]if cpu.pc>=0x8000 else-1
            if(tag,cpu.pc)==(150,0xb854):
                calls.append(('callee',cpu.a,cpu.p,cpu.sp))
                pending=(((m[0x100+((cpu.sp+1)&255)]+256*m[0x100+((cpu.sp+2)&255)]+1)&65535),(cpu.sp+2)&255)
            if pending==(cpu.pc,cpu.sp):
                calls.append(('callee-return',cpu.a,cpu.p,cpu.sp));pending=None
            if(tag,cpu.pc)==(254,0x9a2c):calls.append(('native-proc',cpu.a,cpu.p,cpu.sp))
        # Real sole B483 JSR then B486 LDX ObjectOffset/RTS, not a new stub.
        assert raw[16+0x1483:16+0x1489]==bytes.fromhex('2063b9a60d60')
        r=Q.direct(m,0xb483,a=85,x=3,y=16,p=p,observe=watch)
        models.append(m);results.append(r);events.append(calls)
    assert native_data(models[0])==native_data(models[1]),(kind,scene,p,saved,'actual native/private data')
    assert tuple(results[0][k]for k in('X','Y','SP'))==tuple(results[1][k]for k in('X','Y','SP'))
    assert results[0]['P']&12==results[1]['P']&12==p&12
    if kind!=40:
        assert not any(e[0]=='callee'for e in events[0])
        returned=next(e for e in events[1]if e[0]=='callee-return')
        assert returned[2]&1 and any(e[0]=='native-proc'for e in events[1]),(kind,events)
    return dict(differing_SMC=[at for at in range(0x15a,0x17b)if models[0][at]!=models[1][at]],
        intermediate_AXYP_equal=all(results[0][k]==results[1][k]for k in('A','X','Y','P')),
        minimum_SP=min(r['minimum_SP']for r in results))


def actual_mains(parent,candidate):
    rows=[];taints=0;vectors=Counter();minimum=255;smc=set()
    for kind,scene in product((37,40),('ordinary','authored')):
        cuts,origin,seen=Old.collect(parent,candidate,kind,scene)
        differing={at for at in range(0x15a,0x17b)if cuts[0][0][at]!=cuts[1][0][at]}
        smc|=differing;baseline=[]
        for state,cpu in cuts:
            m,c=L.clone(state,cpu)
            L.finish(m,c,(W.address(m.bundle,'IdleLoop')+12,252),observe=lambda m,c:V.declared_admission(m,c,origin))
            baseline.append(Old.outcome(m,c))
        assert baseline[0]==baseline[1],(kind,scene,'complete current actual Main continuation')
        # Every possible A/NZCV value at the real B486 return; I/D retained.
        for a,flags in product((0,1,40,255),range(16)):
            m,c=L.clone(*cuts[1]);c.a=a
            c.p=(c.p&~0xc3)|(flags&3)|((flags&4)<<4)|((flags&8)<<4)
            L.finish(m,c,(W.address(m.bundle,'IdleLoop')+12,252),observe=lambda m,c:V.declared_admission(m,c,origin))
            assert Old.outcome(m,c)==baseline[1],(kind,scene,a,flags,'actual A/NZCV first consumers')
            taints+=1
        accesses=Counter()
        for vector in('none','IRQ','lagNMI'):
            outputs=[]
            for state,cpu in cuts:
                m,c=L.clone(state,cpu);Trace=Old.tracked(m,c,differing)
                if vector!='none':
                    with Old.patch.object(N,'NesMPU',Trace):
                        low,_=V.Lease.inject_checked(c,vector)
                    minimum=min(minimum,low);vectors[vector]+=1
                L.finish(m,c,(W.address(m.bundle,'IdleLoop')+12,252),observe=lambda m,c:V.declared_admission(m,c,origin))
                accesses.update(op for op,_,_ in m.smc_events);outputs.append(Old.outcome(m,c))
            assert outputs[0]==outputs[1],(kind,scene,vector,'live SMC and actual ISR continuation')
        rows.append(dict(kind=kind,scene=scene,cuts=seen,differing_intermediate_SMC=sorted(differing),
            differing_SMC_read_only_after_current_writer=True,accesses=dict(accesses),
            full_AXYP_live_stack_SMC_WRAM_maps_graphics_exact=True))
        print('DKJR_FOOTER_RYU_MAIN '+json.dumps(rows[-1],separators=(',',':')),flush=True)
    return dict(rows=rows,A_NZCV_taints=taints,real_vectors=dict(vectors),minimum_ISR_SP=minimum,intermediate_SMC=sorted(smc))


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--public',type=Path,required=True)
    args=ap.parse_args();public=args.public.read_bytes();parent,_=C.Camera.proposal(public);candidate,composition=C.proposal(parent)
    assert C.inverse(candidate)==parent
    bundle=W.Symbols.bundle();bundle['raw']=parent
    print('DKJR_FOOTER_RYU_PHASE actual-cold',flush=True)
    _,seed=Q.Roster.cold(bundle,dict(name='RYU HAYABUSA',slot=10,cycle=0,raw=10))
    counts=Counter();minimum=255;different=set()
    print('DKJR_FOOTER_RYU_PHASE all-IDs',flush=True)
    cases=[(kind,scene,0x31,kind^0xa5,25)for kind in range(256)for scene in('ordinary','authored','outside')]
    cases += [(kind,scene,p,0x5a,profile)for kind,scene,profile,p in
        product((37,40),('ordinary','authored','outside'),(25,27),range(256))if p&0x30==0x30]
    for kind,scene,p,saved,profile in cases:
        row=pair(seed,parent,candidate,kind,scene,p=p,saved=saved,profile=profile)
        minimum=min(minimum,row['minimum_SP']);different.update(row['differing_SMC'])
        counts['native_B483_cases']+=1
        counts['intermediate_AXYP_different']+=int(not row['intermediate_AXYP_equal'])
    print('DKJR_FOOTER_RYU_PHASE actual-Main-consumers',flush=True)
    mains=actual_mains(parent,candidate)
    report=dict(passed=True,composition=composition,cases=dict(counts),minimum_SP=minimum,
        intermediate_SMC=sorted(different),actual_Main=mains,
        scope='Declared native actor/scene fixtures and actual cold/Main continuations; no ordinary DK route or native claim',
        output_files=0,native_claim=False)
    encoded=json.dumps(report,sort_keys=True,separators=(',',':'))
    print('DKJR_FOOTER_RYU '+encoded,flush=True);print('DKJR_FOOTER_RYU_SHA256 '+H(encoded.encode()),flush=True)


if __name__=='__main__':main()
