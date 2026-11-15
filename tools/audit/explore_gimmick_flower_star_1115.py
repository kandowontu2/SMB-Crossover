"""Bounded input-only star boarding planner from a genuine mature Flower."""
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import compose_battletoads_native_service_1114 as Current
import check_gimmick_natural_flower_1114 as G


def signed(v):return v-256 if v>=128 else v


def compact(q):
    return{k:q[k]for k in('x','y','vx','vy','ground','star','sx','sy','svx','svy','face','hp','cap','held','inventory','next','lives','score')}


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


def run(actual):
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
    for target in(1196,1212,1228):
        for chase in(False,True):
            q=scene(m,target,8,chase);results.append(q)
            print('BRANCH '+json.dumps(q,separators=(',',':')),flush=True)
            if q['pickups']:break
        if results[-1]['pickups']:break
    return dict(actual_input_SHA256=Current.CANDIDATE,planning_runtime_SHA256=sha256(parent).hexdigest(),
        scope='Input-only historical571 planning from strictae66 inverse; no current/native admission',
        capture={k:v for k,v in capture.items()if k!='memory'},tile_rows=tile_rows,branches=results,
        source_pickup_found=any(q['pickups']for q in results),outputs=0,Mesen=False,gameplay_seeds=0)


if __name__=='__main__':
    raw=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
    def forbid(*args,**kwargs):raise RuntimeError('Star planner attempted files or Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(G.F.Runner.Native,'run',forbid):q=run(raw)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
