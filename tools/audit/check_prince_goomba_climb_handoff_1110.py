"""Try a grounded approach handoff after earning camera travel in the corridor."""

import argparse
from hashlib import sha256
import json
from pathlib import Path

import check_prince_goomba_recovery_1110 as Recovery
import check_prince_roof_goomba_earned_1110 as Earned


Route,R,P,N,Current,Seam=Recovery.Route,Recovery.R,Recovery.P,Recovery.N,Recovery.Current,Recovery.Seam


def replay(env,seed,labels,right_start,goal,nudge,ledge_pad):
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
    mode='right'
    events=[]
    changed=0
    terminal='bound'
    birth=land=None

    def go(new):
        nonlocal mode,changed
        events.append(dict(transition=f'{mode} to {new}',row=q))
        mode,changed=new,epoch

    for epoch in range(650):
        q=Recovery.sample(m,epoch)
        x,y,pose=q['x'],q['y'],q['frame']
        idle=(pose==15 and q['mode']==0 and q['a_lock']==0 and y==176 and 208<=q['foot']<=211
              and any(Route.query_support(m,x+i,208) for i in (2,13)))
        if len(q['actors'])==2 and birth is None:
            birth=q
        if q['hp']==0 or q['engine']!=8 or q['lives']!=2:
            terminal='death'
            break
        if mode=='right' and x>=698:
            go('brake-right')
        elif mode=='left' and x<=699:
            go('brake-left')
        elif mode=='brake-right' and idle:
            go('nudge' if q['camera_right']>=goal else 'left')
        elif mode=='brake-left' and idle:
            go('right')
        elif mode=='nudge' and x>=nudge:
            go('settle')
        elif mode=='settle' and idle and q['facing']==255:
            go('ledge')
        elif mode=='ledge':
            if q['mode'] in (2,6) or q['action']==10:
                go('climb')
            elif epoch-changed>132:
                terminal='unreached-ledge'
                break
        elif mode=='climb':
            if q['action']==10 and q['foot']<=147:
                go('cap')
            elif epoch-changed>150:
                terminal='climb-bound'
                break
        elif mode=='cap':
            if 745<=x<=763 and 111<=y<=115 and Recovery.running(m,q):
                go('jump')
            elif x>766 or epoch-changed>150:
                terminal='no-cap-takeoff'
                break
        elif mode=='jump':
            if q['action']==4:
                go('flight')
            elif epoch-changed>28:
                terminal='no-running-A'
                break
        elif mode=='flight':
            if x>=784 and y==176 and Recovery.grounded(m,q) and land is None:
                land=q
            if land and birth and x>=872 and q['actors'] and all(
                    a['x']+13<x+2 for a in q['actors']) and Recovery.grounded(m,q):
                terminal='cleared'
                break
        if mode in ('right','left','brake-right','brake-left','nudge','settle') and (x<656 or x>723 or not 172<=y<=182):
            terminal='ground-corridor-bound'
            break
        pad={'right':1,'left':2,'brake-right':0,'brake-left':0,'nudge':1,'settle':0,
             'ledge':ledge_pad,'climb':8,'cap':1,'jump':129,'flight':1}[mode]
        Route.controls(env,m,labels,pad)
    return dict(camera_right_initial=right_start,goal=goal,nudge=nudge,ledge_pad=ledge_pad,
                terminal=terminal,events=events,group_birth=birth,far_ground=land,end=q)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    out=parser.parse_args().output.resolve()
    assert out.is_relative_to(R/'build') and not (out/'handoff.json').exists()
    raw=Route.ROM.read_bytes()
    assert sha256(raw).hexdigest()==Route.PIN
    template,_,_=Current.current()
    env,seed,labels,reference=Earned.fixture(dict(template,raw=raw))
    results=[]
    for case in ((748,803,709,8),(748,803,713,8),(748,803,709,72),(760,803,709,8)):
        q=replay(env,seed,labels,*case)
        results.append(q)
        print(case,q['terminal'],q['end']['x'],q['end']['hp'],
              [(e['transition'],e['row']['epoch'],e['row']['x'],e['row']['camera_right'])
               for e in q['events']],flush=True)
    refs=(Path(__file__),Path(Recovery.__file__),Path(Earned.__file__),Path(Route.__file__),Route.ROM)
    receipt=dict(completed=True,ROM_written=False,Mesen_run=False,ROM_SHA256=Route.PIN,
                 source_start=reference,results=results,
                 scope='Explicit corridor starting pose and authentic pipe/group geometry. All subsequent camera, '
                       'source and native enemy movement comes from controller inputs and GameLoop.',
                 bindings={p.relative_to(R).as_posix():sha256(p.read_bytes()).hexdigest() for p in refs})
    (out/'handoff.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    main()
