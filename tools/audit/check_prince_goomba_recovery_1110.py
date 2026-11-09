"""Measure donor input recovery around the two native 1-1 Goombas."""

import argparse
from hashlib import sha256
import json
from pathlib import Path

import check_prince_roof_goomba_route_1110 as Route


R, P, N, Current, Seam = Route.R, Route.P, Route.N, Route.Current, Route.Seam


def sample(model, epoch):
    row = Current.row(model,epoch)
    left,right = Seam.xcamera(model)
    row.update(camera_left=left,camera_right=right,actors=Route.actors(model),
               facing=model.ram[2][0x615],a_lock=model.ram[2][0x6c0],
               phase=model.ram[2][0xa6]&3)
    return row


def grounded(model,row):
    if row['native_state']!=0 or not 112<=row['y']<=176:
        return False
    return any(Route.query_support(model,row['x']+dx,row['y']+32) for dx in (2,13))


def running(model,row):
    return (grounded(model,row) and row['facing']==255 and row['action']==1 and row['mode']==1
            and 6<=row['frame']<=13 and row['a_lock']==0)


def replay(env,seed,labels,threshold,switch,flight_pad,early_delay=0):
    m=N.fork(seed)
    Seam.terrain(m,Route.tiles(224))
    Seam.layout(m,513,745,scroll=0)
    Route.install_group(m)
    events,poses={},[]
    armed=admitted=braked=second_armed=second_admitted=False
    lead_enemy=None
    terminal='bound'
    last_key=None
    contacts=[]
    native=N.NesMPU
    class Trace(native):
        def step(self):
            if self.memory is m and self.pc==0xbd22 and m.rawtags[1]==3:
                before=sample(m,epoch)
                before['slot']=self.x
                contacts.append(before)
            return super().step()
    N.NesMPU=Trace
    try:
        for epoch in range(170):
            row=sample(m,epoch)
            x,y,pose=row['x'],row['y'],row['frame']
            key=pose,row['action'],row['mode']
            if armed and key!=last_key:
                poses.append(row)
                last_key=key
            if row['actors'] and 'group_birth' not in events:
                events['group_birth']=row
            if row['hp']==0 or row['engine']!=8 or row['lives']!=2:
                terminal='death'
                break
            if not armed and x>=threshold and epoch>=early_delay and y==112 and running(m,row):
                armed=True
                events['first_A']=row
            if armed and not admitted and row['action']==4:
                admitted=True
                events['first_action4']=row
            if not armed and y>151:
                terminal='left-cap'
                break
            if admitted and x>=784 and y==176 and grounded(m,row) and 'far_ground' not in events:
                events['far_ground']=row
            if admitted and not braked and pose==switch:
                braked=True
                events['flight_input']=row
            if x>=872 and row['actors'] and all(a['x']+13<x+2 for a in row['actors']) and grounded(m,row):
                terminal='cleared-both'
                break
            if not admitted:
                pad=129 if armed else 1
            elif 'far_ground' not in events or not braked:
                pad=flight_pad if braked else 1
            else:
                ahead=[a for a in row['actors'] if a['x']>x and a['dir']==1]
                if ahead and lead_enemy is None and 33<=min(a['x'] for a in ahead)-x<=72:
                    lead_enemy=min(ahead,key=lambda a:a['x'])['slot']
                    events['second_approach']=row
                if lead_enemy is None:
                    pad=0
                else:
                    target=next((a for a in ahead if a['slot']==lead_enemy),None)
                    if not second_armed and target and running(m,row) and 30<=target['x']-x<=75:
                        second_armed=True
                        events['second_A']=row
                    if second_armed and row['action']==4 and not second_admitted:
                        second_admitted=True
                        events['second_action4']=row
                    pad=129 if second_armed and not second_admitted else 1
            Route.controls(env,m,labels,pad)
    finally:
        N.NesMPU=native
    return dict(threshold=threshold,early_delay=early_delay,switch_pose=switch,flight_pad=flight_pad,
                terminal=terminal,events=events,poses=poses,contacts=contacts,end=row)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    out=args.output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build' and not (out/'recovery.json').exists()
    old=R/'build/prince-roof-goomba-route-1110/route.json'
    assert sha256(old.read_bytes()).hexdigest()=='608ecb367be03c86d5afa6d26fe2f43fb45193891efa979d10c1e29e6d3a7db8'
    raw=Route.ROM.read_bytes()
    assert sha256(raw).hexdigest()==Route.PIN
    template,_,_=Current.current()
    env,seed,labels,start=Route.roof(dict(template,raw=raw))
    cases=[(745,999,1,0),(749,999,1,0),(745,999,1,3),(745,999,1,4),(745,999,1,5),
           *((749,pose,pad,0) for pose,pad in ((34,0),(34,2),(43,0),(43,2),(43,4),(43,8),
                                               (43,64),(43,65),(43,129),(102,2),(105,0),(105,129)))]
    results=[]
    for case in cases:
        result=replay(env,seed,labels,*case)
        results.append(result)
        print(case,result['terminal'],result['end']['x'],result['end']['hp'],
              [(k,v['epoch'],v['x']) for k,v in result['events'].items()],flush=True)
    assert results[0]['end']['x']==801 and results[1]['end']['x']==830
    out.mkdir(exist_ok=True)
    refs=(Path(__file__),Path(Route.__file__),Route.ROM,old)
    receipt=dict(completed=True,ROM_written=False,Mesen_run=False,ROM_SHA256=Route.PIN,
                 start=start,results=results,
                 scope='Exact prior cap and native group CPU fixture. The only changed runtime inputs are real controller pads. '
                       'The end condition requires both live group actors behind, far-side ground and both lives.',
                 bindings={p.relative_to(R).as_posix():sha256(p.read_bytes()).hexdigest() for p in refs})
    (out/'recovery.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    main()
