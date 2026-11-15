"""Bounded input-only star boarding planner from a genuine mature Flower."""
from hashlib import sha256
import argparse
import json
from pathlib import Path
from unittest.mock import patch

import compose_battletoads_native_service_1114 as Current
import check_gimmick_natural_flower_1114 as G


def signed(v):return v-256 if v>=128 else v


def compact(q):
    return{k:q[k]for k in('x','y','vx','vy','ground','star','flags','sx','sy','svx','svy','face','hp','cap','held','inventory','next','lives','score')}


def align(b,target,limit=120):
    for _ in range(limit):
        q=G.state(b.m);v=signed(q['vx']);stop=q['x']+v*abs(v)/32
        if abs(q['x']-target)<=2 and abs(v)<=2 and q['ground']>=128:return q
        b.step(1 if stop<target-1 else 2 if stop>target+1 else 0)
    raise AssertionError(('Ordinary alignment bound',target,G.state(b.m)))


def scene(seed,target,air_charge,chase):
    b=G.Branch(seed);align(b,target);b.step(1|64)
    for _ in range(100):
        q=b.step(64)
        if q['star']>=169:break
    else:raise AssertionError('Original charge bound')
    for _ in range(air_charge):b.step(64|128)
    b.step(128)
    released=b.t;boarded=None;last_a=True;best_gap=99999
    for _ in range(150):
        q=G.state(b.m)
        if b.pickups:break
        if b.rides and boarded is None:
            boarded=dict(t=b.t,state=compact(q));b.step(0);last_a=False
        if boarded:
            direction=1 if q['x']<1241 else 2 if q['x']>1245 else 0
            pad=direction|(128 if not last_a or q['vy']>=128 else 0)
        else:
            aim=q['sx']-8 if chase else target
            v=signed(q['vx']);stop=q['x']+v*abs(v)/32
            direction=1 if stop<aim-1 else 2 if stop>aim+2 else 0
            pad=direction
            if q['ground']>=128 and not last_a and abs(q['x']-aim)<36:pad|=128
            elif q['ground']<128 and q['vy']>=128:pad|=128
        last_a=bool(pad&128);q=b.step(pad)
        gap=abs(q['x']+8-q['sx'])+abs(q['y']+32-(q['sy']-14))
        best_gap=min(best_gap,gap)
    if b.pickups:
        for _ in range(25):b.step(0)
    trace=b.trace
    # One aggregate receipt, bounded snapshots; no per-case files.
    return dict(target=target,air_charge=air_charge,chase=chase,release_update=released,
        boarding=boarded,pickups=b.pickups,real_supports=len(b.rides),best_star_gap=best_gap,
        terminal=compact(G.state(b.m)),trace=trace[:3]+trace[-3:])


class ObserveBranch(G.Branch):
    """Passive actual launch/reflection witnesses around the ordinary frame."""
    def __init__(self,seed):
        super().__init__(seed);self.events=[];self.phase='align'
        self.points={}
        for name in('GmN30_829C','GmN29_8114'):
            at=G.W.location(seed.bundle,name)
            self.points[(G.W.address(seed.bundle,name),(at-16)//8192|128)]=name
    def step(self,pad):
        owner=self;base=G.N.NesMPU
        class CPU(base):
            def step(cpu):
                tag=owner.m.rawtags[(cpu.pc-0x8000)//8192]if cpu.pc>=0x8000 else-1
                label=owner.points.get((cpu.pc,tag))
                if label:
                    assert len(owner.events)<16,'Bounded original star writer witnesses'
                    owner.events.append(dict(t=owner.t,phase=owner.phase,event=label,PC=cpu.pc,tag=tag,
                        A=cpu.a,new_signed_vx=signed(cpu.a),wall=G.N.get(owner.m,'GmRam0379'),
                        state=compact(G.state(owner.m))))
                return super().step()
        with patch.object(G.N,'NesMPU',CPU):return super().step(pad)


def opposite_scene(seed,air_charge,jump_start=1244):
    b=ObserveBranch(seed);marks=[];trajectory=[]
    def mark(name):
        b.phase=name;marks.append(dict(t=b.t,phase=name,state=compact(G.state(b.m))))
    align(b,1244);mark('stationary-charge')
    for _ in range(120):
        q=b.step(64)
        if q['star']>=169:break
    else:raise AssertionError('Real original charge did not mature')
    mark('right-charge-runup')
    for _ in range(80):
        q=G.state(b.m)
        if q['x']>=1270:break
        b.step(1|64)
    else:raise AssertionError('Ordinary right runup bound')
    mark('left-charge-runup')
    for _ in range(100):
        q=G.state(b.m)
        if q['x']<=jump_start and signed(q['vx'])<0:break
        b.step(2|64)
    else:raise AssertionError('Ordinary left runup bound')
    mark('left-jump-with-charge')
    for _ in range(air_charge):b.step(2|64|128)
    mark('right-facing-release-with-left-momentum');b.step(1|128)
    mark('left-chase-through-first-descent');boarded=None;last_a=True
    for i in range(100):
        q=G.state(b.m)
        if len(trajectory)<32:trajectory.append(dict(t=b.t,phase=b.phase,state=compact(q)))
        if b.pickups:break
        if b.rides:
            boarded=boarded or dict(t=b.t,ride=b.rides[0],state=compact(q))
            if last_a:
                mark('actual-ride-A-release');b.step(0);last_a=False;continue
            mark('actual-ride-fresh-right-jump');b.step(1|128);last_a=True;break
        b.step(2|128)
        if q['star']==0 or q['x']<1152:break
    if boarded:
        mark('flower-chase-after-real-support')
        for i in range(100):
            q=G.state(b.m)
            if b.pickups:break
            b.step((1 if q['x']<1243 else 2 if q['x']>1247 else 0)|(128 if i<25 else 0))
    if b.pickups:
        for _ in range(25):b.step(0)
    return dict(kind='opposite-momentum-real-brick-reflection',air_charge=air_charge,jump_start=jump_start,
        marks=marks,actual_star_writers=b.events,boarding=boarded,real_supports=len(b.rides),
        pickups=b.pickups,trajectory=trajectory,terminal=compact(G.state(b.m)))


def run(actual,air_charges=(4,8),jump_start=1244):
    assert sha256(actual).hexdigest()==Current.CANDIDATE
    parent=Current.inverse(actual)
    # Historical571 is an explicitly recovered planning model. It is not
    # represented as actualae66 execution or native/current acceptance.
    capture=G.mature_seed(parent);m=capture['memory'];tile_rows=[]
    for y in(128,144,160,192,208):
        row=[]
        for x in range(1152,1329,16):
            at=(x//256%2)*208+((y-32)//16)*16+(x%256//16)
            row.append(G.N.get(m,'Block_Buffer_1',at))
        tile_rows.append(dict(y=y,x_start=1152,step=16,tiles=row))
    results=[]
    for air_charge in air_charges:
        q=opposite_scene(m,air_charge,jump_start);results.append(q)
        print('BRANCH '+json.dumps(q,separators=(',',':')),flush=True)
        if q['pickups']:break
    return dict(actual_input_SHA256=Current.CANDIDATE,planning_runtime_SHA256=sha256(parent).hexdigest(),
        scope='Input-only historical571 planning from strictae66 inverse; no current/native admission',
        capture={k:v for k,v in capture.items()if k!='memory'},tile_rows=tile_rows,branches=results,
        source_pickup_found=any(q['pickups']for q in results),outputs=0,Mesen=False,gameplay_seeds=0)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--air-charge',type=int,nargs='+',default=[4,8]);parser.add_argument('--jump-start',type=int,default=1244);args=parser.parse_args()
    assert len(args.air_charge)<=2 and all(3<=n<=14 for n in args.air_charge),'Only two measured short launch phases are permitted'
    assert 1242<=args.jump_start<=1246,'Measured real-brick-edge takeoff domain'
    raw=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
    def forbid(*args,**kwargs):raise RuntimeError('Star planner attempted files or Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(G.F.Runner.Native,'run',forbid):q=run(raw,args.air_charge,args.jump_start)
    digest=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    summary={k:v for k,v in q.items()if k!='branches'}
    summary.update(receipt_SHA256=digest,branches=[dict(jump_start=b['jump_start'],air_charge=b['air_charge'],
        real_supports=b['real_supports'],pickup_entries=len(b['pickups']),terminal=b['terminal'])for b in q['branches']])
    print('RESULT '+json.dumps(summary,separators=(',',':')),flush=True)
