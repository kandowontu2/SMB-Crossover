"""Try to earn the required Prince camera lead using ordinary corridor input."""

import argparse
from hashlib import sha256
import json
from pathlib import Path

import check_prince_roof_goomba_route_1110 as Route


R,P,N,Current,Seam=Route.R,Route.P,Route.N,Route.Current,Route.Seam


def fixture(base):
    cold,_=P.Q.C.C.cold(base,38)
    env,m,labels=P.Q.first8(base,cold)
    Seam.terrain(m,lambda x,y:0x54 if y>=208 else 0)
    for epoch in range(75):
        q=Current.row(m,epoch)
        if q['action']==1 and q['mode']==1 and q['frame']==6 and q['native_state']==0:
            return env,m,labels,q
        Route.controls(env,m,labels,1)
    raise AssertionError('Expected original rightward run admission on native floor')


def approach(env,seed,labels,right_start,goal,low_turn,neutral_brake,release_at_goal,idle_up):
    m=N.fork(seed)
    def tile(x,y):
        if y>=208:
            return 0x54
        for left,top in ((96,160),(224,144)):
            if left<=x<left+32 and y>=top:
                return (0x12 if y<top+16 else 0x14)+int(x>=left+16)
        return 0
    Seam.terrain(m,tile)
    Seam.layout(m,right_start-255,678,scroll=0)
    Route.install_group(m)
    mode='camera-right'
    changed=0
    events=[]
    groups=None
    landing=None
    roof_jump=None
    original_aerial=False
    bounds=[678,678]
    no_advance=0
    last_x=678
    pad=1
    terminal='bound'

    def switch(new):
        nonlocal mode,changed
        events.append(dict(transition=f'{mode} to {new}',state=q))
        mode,changed=new,epoch

    for epoch in range(680):
        q=Current.row(m,epoch)
        x,y,pose=q['x'],q['y'],q['frame']
        left,right=Seam.xcamera(m)
        q.update(left=left,right=right,actors=Route.actors(m),pad=pad)
        if q['actors'] and groups is None:
            groups=q
        if q['hp']==0 or q['lives']!=2 or q['engine']!=8:
            terminal='death'
            break
        if x==last_x:
            no_advance+=1
        else:
            last_x,no_advance=x,0
        if no_advance>240:
            terminal='stalled'
            break
        support=q['native_state']==0 and y<192 and any(Route.query_support(m,x+i,y+32) for i in (2,13))
        ready=(support and q['action']==1 and q['mode']==1 and 6<=pose<=13 and not m.ram[2][0x6c0])
        idle=(support and pose==15 and q['mode']==0 and not m.ram[2][0x6c0])
        age=epoch-changed
        if mode.startswith('camera-'):
            bounds=[min(bounds[0],x),max(bounds[1],x)]
            if not 656<=x<=721 or y<172 or y>182:
                terminal='left-safe-corridor'
                break
            if mode=='camera-right' and x>=698:
                if idle_up:
                    switch('camera-brake-right')
                elif right>=goal and (release_at_goal or ready):
                    switch('approach')
                elif right<goal:
                    switch('camera-brake-right' if neutral_brake else 'camera-left')
                elif x>=714:
                    terminal='camera-goal-without-running-pose'
                    break
            elif mode=='camera-left' and x<=low_turn:
                switch('camera-brake-left' if neutral_brake else 'camera-right')
            elif mode=='camera-brake-right' and idle:
                switch('stand-up' if idle_up and right>=goal else 'camera-left')
            elif mode=='camera-brake-left' and idle:
                switch('camera-right')
            pad=2 if mode=='camera-left' else 0 if mode.startswith('camera-brake-') else 1
        if mode=='approach':
            pad=1
            if ready and 703<=x<=719:
                switch('takeoff')
                pad=129
            elif x>=720:
                switch('settle')
                pad=0
        elif mode=='takeoff':
            pad=129
            if q['action']==4:
                original_aerial=True
                switch('aerial')
                pad=1
            elif age>28:
                switch('settle')
                pad=0
        elif mode=='aerial':
            pad=1
            if x>=694 and x<768 and q['action']==4 and 40<=pose<=42 and q['foot']-24<=175:
                pad=9
            if age>=12 and q['action']!=4 and support:
                switch('settle')
                pad=0
        elif mode=='settle':
            pad=0
            if idle:
                switch('stand-up')
                pad=8
        elif mode=='stand-up':
            pad=8 if age<64 else 201
        elif mode=='climb':
            pad=9
        if mode in ('aerial','stand-up','climb') and (q['mode'] in (2,6) or q['action']==10):
            if q['action']==10 and q['foot']<=147:
                switch('cap')
                pad=1
            elif mode!='climb':
                switch('climb')
                pad=8
        if mode=='cap':
            pad=1
            if ready and 745<=x<=752 and y==112:
                switch('roof-A')
                pad=129
        elif mode=='roof-A':
            pad=129
            if q['action']==4:
                roof_jump=q
                switch('roof-flight')
                pad=1
        elif mode=='roof-flight':
            pad=1
            if x>=784 and y==176 and q['native_state']==0 and landing is None:
                landing=q
            if x>=864 and landing and groups:
                terminal='clear'
                break
        Route.controls(env,m,labels,pad)
    return dict(start_camera_right=right_start,target_camera_right=goal,low_turn=low_turn,minimum_maximum_corridor_x=bounds,
                genuine_neutral_brake=neutral_brake,
                terminal=terminal,events=events,authentic_group_birth=groups,roof_jump=roof_jump,
                far_ground=landing,approach_aerial=original_aerial,end=q)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--low-turn',type=int,choices=(676,686,699),default=686)
    parser.add_argument('--neutral-brake',action='store_true')
    parser.add_argument('--release-at-goal',action='store_true')
    parser.add_argument('--idle-up',action='store_true')
    args=parser.parse_args()
    out=args.output.resolve()
    receipt_name=('earned-v4.json' if args.low_turn==699 else 'earned-v3.json') if args.neutral_brake \
        else 'earned.json' if args.low_turn==676 else 'earned-v2.json'
    if args.release_at_goal:
        assert args.neutral_brake and args.low_turn==699
        receipt_name='earned-v5.json'
    if args.idle_up:
        assert args.neutral_brake and args.low_turn==699 and not args.release_at_goal
        receipt_name='earned-v6.json'
    assert out.is_relative_to(R/'build') and out!=R/'build' and not (out/receipt_name).exists()
    previous=out/'route.json'
    assert sha256(previous.read_bytes()).hexdigest()=='608ecb367be03c86d5afa6d26fe2f43fb45193891efa979d10c1e29e6d3a7db8'
    raw=Route.ROM.read_bytes()
    assert sha256(raw).hexdigest()==Route.PIN
    template,_,_=Current.current()
    env,seed,labels,start=fixture(dict(template,raw=raw))
    results=[]
    cases=((748,786),(748,793),(748,803),(760,793),(760,803),(760,816)) if args.release_at_goal else \
        ((748,803),(748,816),(760,803),(760,816),(736,803))
    if args.idle_up:
        cases=((748,803),(760,803),(748,816))
    for initial,goal in cases:
        result=approach(env,seed,labels,initial,goal,args.low_turn,args.neutral_brake,args.release_at_goal,args.idle_up)
        results.append(result)
        print(initial,goal,result['terminal'],result['end']['x'],result['end']['hp'],
              [(e['transition'],e['state']['epoch'],e['state']['x'],e['state']['right']) for e in result['events']],flush=True)
    receipt=dict(completed=True,ROM_written=False,Mesen_run=False,ROM_SHA256=Route.PIN,
                 source_reference=start,results=results,
                 scope='Explicit authentic loaded Prince ground fixture at corridor start and exact 1-1 parser cursor. '
                       'All subsequent camera movement, original ledge/climb and roof inputs run through native GameLoop. '
                       'No result claims actual Mesen stage progression.',
                 bindings={p.relative_to(R).as_posix():sha256(p.read_bytes()).hexdigest() for p in
                           (Path(__file__),Path(Route.__file__),Route.ROM,previous)})
    (out/receipt_name).write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    main()
