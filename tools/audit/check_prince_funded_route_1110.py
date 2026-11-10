"""Controller-only exploration on funded Prince and actual fourth-pipe data."""
import argparse
import json

import check_prince_floor_carrier_1110 as Q

C,N,F=Q.C,Q.N,Q.Foot.F


def trial(env,seed,labels,wait,back_pad,face_pad,bound=1200):
    m=Q.Sonic.slim_fork(seed);stage='park' if wait else 'run';changed=0;events=[];debits=[];last_hp=5
    cap=False;maximum=0;last_action=None;poses=[];pads=[]
    def go(name,row):
        nonlocal stage,changed
        events.append(dict(event=stage+' -> '+name,**{k:row[k] for k in
            ('epoch','x','y','foot','action','frame','mode','hp')}))
        stage,changed=name,row['epoch']
    for tick in range(bound):
        row=F.sample(m,tick);x,y=row['x'],row['y'];maximum=max(maximum,x)
        if row['hp']!=last_hp:debits.append(dict(tick=tick,x=x,before=last_hp,after=row['hp']));last_hp=row['hp']
        key=row['action'],row['frame'],row['mode']
        if 850<=x<=950 and key!=last_action:poses.append({k:row[k] for k in ('epoch','x','y','foot','action','frame','mode','hp')})
        last_action=key
        if row['hp']==0 or row['lives']!=2 or row['engine']!=8:stage='dead';break
        if stage=='park' and x>=739 and y==112:go('wait',row)
        if stage=='wait':
            walkers=[a for a in row['actors'] if a['id']==6 and a['state']<2]
            if tick>=wait and (not walkers or all(a['dir']==2 and a['x']<850 for a in walkers)):go('takeoff',row)
            elif y>115:stage='left-cap-while-waiting';break
        if stage=='run' and 745<=x<=752 and abs(y-112)<=2 and C.Recovery.running(m,row):go('takeoff',row)
        elif stage=='takeoff' and row['action'] in (3,4):go('flight',row)
        elif stage=='flight' and x>=790 and y==176 and row['support']:go('floor-walk',row)
        elif stage=='floor-walk' and (x>=881 or row['action']==47):go('wall-settle',row)
        elif stage=='wall-settle' and row['mode']==0 and row['frame']==15 and row['support']:go('up',row)
        elif stage=='backoff' and x<=882 and row['support']:go('face',row)
        elif stage=='face' and row['facing']==255 and row['support']:go('up',row)
        elif stage=='up' and tick-changed>=55:go('reach',row)
        elif stage=='reach' and tick-changed>=6:go('climb',row)
        if stage in ('up','reach','climb') and 899<=x<944 and y==112 and row['support'] and row['mode']==0:
            cap=True;go('cap-run',row)
        if stage=='cap-run' and x>=960 and y==176 and row['support']:go('pit-approach',row)
        if stage=='pit-approach' and 1059<=x<=1090 and row['phase'] in (0,1) and C.Recovery.running(m,row):go('pit-takeoff',row)
        elif stage=='pit-takeoff' and row['action']==4:go('pit-flight',row)
        elif stage=='pit-flight' and x>=1152 and y==176 and row['support']:go('first-gap-clear',row);break
        if stage in ('up','reach','climb') and x>=944 and y==176:
            stage='unqualified-floor-crossing';break
        if tick-changed>280 and stage not in ('wait','run','flight'):
            stage+='-bound';break
        pad={'park':1,'wait':0,'run':1,'takeoff':129,'flight':1,'floor-walk':1,'wall-settle':0,'backoff':back_pad,'face':face_pad,
             'up':8,'reach':9,'climb':8,'cap-run':1,'pit-approach':1,'pit-takeoff':129,'pit-flight':1}[stage]
        if not pads or pads[-1]['pad']!=pad:pads.append(dict(start=tick,pad=pad))
        C.Route.controls(env,m,labels,pad);N.consume(m)
    else:stage='bounded'
    return dict(outcome=stage,wait=wait,back_pad=back_pad,face_pad=face_pad,maximum_x=maximum,
        actual_fourth_cap=cap,events=events,HP_debits=debits,terminal=row,poses=poses,pads=pads,
        native_terrain=F.terrain_signature(m),helpers_added=0)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--wait',type=int,default=96)
    p.add_argument('--back-pad',type=int,default=66);p.add_argument('--face-pad',type=int,default=65)
    p.add_argument('--baseline',action='store_true');args=p.parse_args()
    _,bundle,_,layout,_,_,_=Q.proposal();env,seed,labels=C.fixture(bundle)
    N.put(seed,CrossoverBehaviorVersion=0);N.consume(seed);F.REAL_NMI=True;_,seed=F.authored(seed)
    print('ROUTE_PARENT '+json.dumps(dict(in_memory_SHA256=layout['in_memory_SHA256'],
        points=F.point_probes(seed),ROM_written=False,outputs_written=0)),flush=True)
    if args.baseline:
        result,_=F.trial(env,seed,labels,'roll-up',bound=220)
    else:result=trial(env,seed,labels,args.wait,args.back_pad,args.face_pad)
    print('CONTROLLER_ROUTE '+json.dumps(result,separators=(',',':')),flush=True)


if __name__=='__main__':main()
