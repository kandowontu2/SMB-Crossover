"""Check convergence of the changed return registers at native actor ingress."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

import check_native_actor_bounds_1110 as B
import check_native_actor_bounds_irq_1110 as I
from check_mini_funded_actor_1108_v3 import install, registers, run
from check_mini_inactive_weapon_gate_irq_1110_v1 import fork


D,P,N,M=B.D,B.P,B.N,B.M
NORMAL, PLATFORM=0xa493,0xb44d


def branch_state(c):
    return D.bank_pc(c),registers(c,0xef)


def first_return(c):
    m=c.memory
    return (1+m[0x100+c.sp+1]+256*m[0x100+c.sp+2],c.sp+2)


def converge(a,b):
    initial_a,initial_b=registers(a,0xef),registers(b,0xef)
    steps=0
    while branch_state(a)!=branch_state(b):
        assert D.bank_pc(a)==D.bank_pc(b),(branch_state(a),branch_state(b))
        assert a.sp==b.sp
        assert steps<180,('Actor return failed to converge',branch_state(a),branch_state(b))
        prior=[len(c.memory.writes) for c in (a,b)]
        B.trace_bounds(b)
        a.step()
        b.step()
        assert a.memory.writes[prior[0]:]==b.memory.writes[prior[1]:],(
            steps,branch_state(a),branch_state(b),a.memory.writes[prior[0]:],b.memory.writes[prior[1]:])
        steps+=1
    diff=[name for name,x,y in zip(('A','X','Y','P','SP'),initial_a,initial_b,strict=True) if x!=y]
    return tuple(diff),steps,D.bank_pc(a)


def compare(context,images,pc,x,eid,p,mode):
    a,b=[fork(context,im) for im in images]
    end=first_return(a)
    assert end==first_return(b)
    for side,c in enumerate((a,b)):
        m=c.memory
        N.put(m,ScreenLeft_X_Pos=200,ScreenLeft_PageLoc=127,
              ScreenRight_X_Pos=199,ScreenRight_PageLoc=128)
        for name,value in (('Enemy_X_Position',x&255),('Enemy_PageLoc',x>>8),('Enemy_ID',eid)):
            M.place(m,name,c.x,value)
        if mode is not None:
            area,hard,cloud,frame=mode
            N.put(m,AreaType=area,SecondaryHardMode=hard,CloudTypeOverride=cloud,FrameCounter=frame)
        c.p=p
        run(c,lambda q:(q.pc,q.sp)==end,B.trace_bounds if side else None)
        if pc==PLATFORM:
            expected=0x54+2*int(area!=3 and not hard)+4*bool(cloud)+(frame&1)
            actual=N.get(m,'EnemyMetasprite',c.x)
            assert actual==expected,(mode,actual,expected)
    return converge(a,b)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    raw=B.ROM.read_bytes()
    proof=args.output/'proof.json'
    q=json.loads(proof.read_text())
    assert P.sha(raw)==q['parent_SHA256']==B.PIN
    image=install(raw,q['patches'])
    assert P.sha(image)==q['expected_memory_only_SHA256']
    images=[P.bundle(data) for data in (raw,image)]
    seeds=B.cold_pair(images,(0,2,25,32,41))
    scene=json.loads(B.PEAK.read_text())['scene']
    stats=Counter()
    for owner,pc in product(seeds,(NORMAL,PLATFORM)):
        context=I.prepare(seeds[owner][0],scene)
        run(context,lambda c:D.bank_pc(c)==(128,pc))
        left=127*256+200
        if pc==NORMAL:
            cases=((left+rel,eid,p,None) for rel,eid,p in
                   product((-329,-1,0,63,255,256,329,32769),(5,6,13,20),(0x20,0xe1)))
        else:
            cases=((left+rel,eid,p,mode) for rel,eid,p,mode in
                   product((-1,63),range(0x24,0x2b),(0x20,0xe1),
                           product((0,1,2,3),(0,1,255),(0,3),(0,1))))
        for x,eid,p,mode in cases:
            flags,steps,site=compare(context,images,pc,x&65535,eid,p,mode)
            stats[pc,flags,steps,site]+=1
    out=dict(passed=True,parent_SHA256=B.PIN,expected_memory_only_SHA256=P.sha(image),ROM_written=False,
             cases=sum(stats.values()),maximum_common_instructions=max(key[2] for key in stats),
             native_platform_IDs=list(range(0x24,0x2b)),
             rows=[[pc,flags,steps,site,count] for (pc,flags,steps,site),count in sorted(stats.items())],
             bindings={str(p):P.sha(p.read_bytes()) for p in (Path(__file__),proof,B.ROM,B.PEAK)})
    (args.output/'return.json').write_text(json.dumps(out,indent=2)+'\n')
    print(out['cases'],out['maximum_common_instructions'],flush=True)


if __name__=='__main__':
    main()
