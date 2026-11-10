"""Complete the immutable preliminary wide-helper numeric/foreign/vector proof."""
import argparse
from collections import Counter
from hashlib import sha256
import inspect
import json
from pathlib import Path

import check_manual_wide_horizontal_1110 as W
import check_generic_helper_camera_1110 as G

P,N,R,D=W.P,W.N,W.R,W.D
OUT=W.OUT
PROOF=OUT/'proof.json'


def sha(path):return sha256(path.read_bytes()).hexdigest()


def images():
    q=json.loads(PROOF.read_text())
    for path,digest in q['bindings'].items():assert sha(R/path)==digest,path
    raw=W.BASE.read_bytes();assert W.sha(raw)==q['parent_SHA256']==W.PIN
    new=P.install(raw,q['patches']);assert W.sha(new)==q['expected_memory_only_SHA256']
    old=P.install(raw,json.loads(W.PRIOR.read_text())['patches'])
    return old,new,q


def at(m,pc,*,a=85,x=0,y=0,p=0x31,sp=224,watch=None):
    m.raw_page(1,154);N.put(m,CurrentBank=154)
    c=N.NesMPU(memory=m,pc=pc)
    c.a,c.x,c.y,c.p,c.sp=a,x,y,p,sp
    c.stPushWord(0x5aff)
    P.run(c,lambda z:(z.pc,z.sp)==(0x5b00,sp),watch)
    return c


def sine(before,after,q):
    seeds=[P.scene(b,0) for b in (before,after)]
    labels={n:P.L.M.address(before,n) for n in ('HpSlot','HpPhaseHi','HpTemp2','HpSineIndex')}
    counts=Counter();states=0
    for index in range(256):
      for sign in (0,128):
       for flags in (0x30,0x31,0x70,0xf5,0x38,0xff):
        worlds=[P.slim_fork(m) for m in seeds]
        for m in worlds:
            m[labels['HpSlot']]=2;m[labels['HpPhaseHi']+2]=sign
            m[labels['HpSineIndex']]=index;m[labels['HpTemp2']]=231
        cpus=[at(m,q['format']['reader_pc'],x=2,y=index,p=flags) for m in worlds]
        assert P.memory(worlds[0])==P.memory(worlds[1]),(index,sign,flags)
        regs=[(c.a,c.x,c.y,c.p,c.sp) for c in cpus]
        assert regs[0]==regs[1],(index,sign,flags,regs)
        amplitude=bytes.fromhex(q['format']['table_values'])[index]
        assert worlds[1][labels['HpTemp2']]==amplitude
        assert cpus[1].a==((-amplitude)&255 if sign else amplitude)
        counts[cpus[1].processorCycles-cpus[0].processorCycles]+=1
        states+=1
    return dict(states=states,all256_samples_both_polarities=True,full_memory_AXYPSP=True,
                additional_CPU_cycles=dict(counts),private_scratch='Existing HpTemp2 output only; Y/P saved; source Signed tail restoresX')


def foreign(before,after):
    seeds=[P.scene(b,0) for b in (before,after)]
    cycles=Counter();count=0
    for owner in (0,29,34,41,42):
     for actor in (0x25,0x28,0x29,0x2a):
      for marker in (0,0x40,0x41,0x42,0x60,0xc0):
       for sidecar in (0,1,4):
        if owner in (34,41) and actor==0x28 and marker==0x42 and sidecar==0:continue
        worlds=[P.slim_fork(m) for m in seeds]
        for m in worlds:
            N.put(m,SelectedCharacter=owner,ObjectOffset=3,TimerControl=0,FrameCounter=3)
            P.set_slot(m,3,Enemy_Flag=1,Enemy_ID=actor,Enemy_State=marker,
                       Enemy_X_Position=136,Enemy_PageLoc=0,Enemy_Y_Position=160,
                       Enemy_Y_HighPos=1,PlatformCollisionFlag=255,Enemy_X_Speed=0,
                       Enemy_Y_Speed=0,Enemy_Y_MoveForce=0)
            m[0x73ae+3]=sidecar
        cpus=[at(m,0xae40,x=3,a=0,y=17) for m in worlds]
        assert P.memory(worlds[0])==P.memory(worlds[1]),(owner,actor,marker,sidecar)
        assert (cpus[0].a,cpus[0].x,cpus[0].y,cpus[0].p)==(cpus[1].a,cpus[1].x,cpus[1].y,cpus[1].p)
        cycles[cpus[1].processorCycles-cpus[0].processorCycles]+=1;count+=1
    return dict(cases=count,full_memory_AXYP=True,additional_CPU_cycles=dict(cycles))


def owned_vectors(bundle,labels,axis,pc):
    source=inspect.getsource(D.vectors).replace('def vectors(','def local_vectors(')
    needle="source=source.replace('if not inside or key in seen:',"
    assert needle in source
    # D.vectors constructs the unchanged original checker in its own globals.
    # Add actual bank26 new-code cuts after player control, including carry.
    source=source.replace("if not (inside or hot) or key in seen:",
        f"if not (inside or hot or tag == 154 and {pc} <= pc < {pc+256}) or key in seen:")
    env=dict(D.__dict__);exec(source,env)
    return env['local_vectors'](bundle,labels,axis)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--foreground',action='store_true');p.add_argument('--vectors',action='store_true')
    args=p.parse_args();old,new,q=images()
    before,after=P.bundles(old,new)
    if args.foreground:
        numeric=sine(before,after,q);print('Exact sine',numeric,flush=True)
        native=foreign(before,after);print('Foreign native motion',native,flush=True)
        regular={owner:P.regular_parity([P.scene(before,owner),P.scene(after,owner)],owner,old,new)
                 for owner in (0,5,25,29,34,41,42)}
        result=dict(passed=True,preliminary_proof_SHA256=sha(PROOF),
            expected_memory_only_SHA256=q['expected_memory_only_SHA256'],sine=numeric,foreign=native,regular=regular,
            bindings={Path(__file__).relative_to(R).as_posix():sha(Path(__file__))})
        (OUT/'qualification-foreground.json').write_text(json.dumps(result,indent=2)+'\n')
        print('Complete frame comparisons',regular,flush=True)
    if args.vectors:
        results={}
        for axis in (0x28,0x24):
            results[axis]=owned_vectors(after,q['labels'],axis,q['format']['table_pc'])
            print('Actual owned vectors',axis,results[axis],flush=True)
        receipt=dict(passed=True,preliminary_proof_SHA256=sha(PROOF),
                     expected_memory_only_SHA256=q['expected_memory_only_SHA256'],owned=results)
        (OUT/'irq.json').write_text(json.dumps(receipt,indent=2)+'\n')


if __name__=='__main__':main()
