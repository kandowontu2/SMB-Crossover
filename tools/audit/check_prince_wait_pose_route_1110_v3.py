"""One original careful step, actor-direction wait, pose15 Up release.

No physics, terrain, inventory, actor outcome, timer or health mutation follows
the explicit translated CPU scene construction. No artifact is produced.
"""
import argparse
import json
from unittest.mock import patch

import check_prince_floor_carrier_1110 as Q

C,N,I,F=Q.C,Q.N,Q.I,Q.Foot.F


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--park',choices=('careful','reverse'),default='reverse')
    parser.add_argument('--departure',choices=('run','standing'),default='standing')
    parser.add_argument('--approach',choices=('run','careful'),default='run')
    args=parser.parse_args()
    _,bundle,_,layout,_,_,_=Q.proposal()
    env,seed,labels=C.fixture(bundle);N.put(seed,CrossoverBehaviorVersion=0);N.consume(seed)
    F.REAL_NMI=True;_,model=F.authored(seed)
    stage='park-careful' if args.park=='careful' else 'park-run'
    changed=0;tick=0;events=[];HP=[];pads=[];poses=[];source=[]
    last_HP=5;last_pose=None;cap=False;wait_anchor=None;wait_samples=0;maximum=0
    native=N.NesMPU
    def row():return F.sample(model,tick)
    def go(name,r,**extra):
        nonlocal stage,changed
        events.append(dict(event=stage+' -> '+name,**{k:r[k] for k in
            ('epoch','x','y','foot','action','frame','mode','hp','phase')},**extra))
        stage,changed=name,tick
    def cap_support(r,left):
        x=r['x'];top=144
        return [C.Route.query_support(model,x+d,top) in (0x10,0x11,0x12,0x13)
            and not C.Route.query_support(model,x+d,top-1) and left<=x+d<left+32 for d in (2,13)]
    class Trace(native):
        def step(self):
            if self.memory is model and self.pc==0xa34d and self.y==0 and model.rawtags[1]==3:
                r=row()
                source.append(dict(tick=tick,action=self.a,x=r['x'],y=r['y'],before=r['action'],
                    frame=r['frame'],mode=r['mode'],pad=model.ram[2][0x40a]))
            return super().step()
    with patch.object(N,'NesMPU',Trace):
        for tick in range(1400):
            r=row();x,y=r['x'],r['y'];maximum=max(maximum,x)
            if r['hp']!=last_HP:HP.append(dict(tick=tick,x=x,before=last_HP,after=r['hp']));last_HP=r['hp']
            key=r['action'],r['frame'],r['mode'],y
            if key!=last_pose and (stage!='wait-walkers' or not poses):
                poses.append({k:r[k] for k in ('epoch','x','y','foot','action','frame','mode','hp','phase')})
            last_pose=key
            if not r['hp'] or r['lives']!=2 or r['engine']!=8:go('dead',r);break
            if stage=='park-run' and C.Recovery.running(model,r):go('park-brake',r)
            elif stage=='park-brake' and r['action']==6:go('park-settle',r)
            if stage=='park-careful' and r['action'] not in (0,1,10):go('park-settle',r)
            elif stage=='park-settle' and r['frame']==15 and r['mode']==0:
                full=all(cap_support(r,736)) and r['support'] and r['native_state']==0 and abs(y-112)<=1
                if not full:go('full-third-cap-not-established',r,support_feet=cap_support(r,736));break
                wait_anchor=dict(x=x,y=y,foot=r['foot'],source_x=r['source_x'],source_y=r['source_y'])
                go('wait-walkers',r,anchor=wait_anchor)
            if stage=='wait-walkers':
                full=all(cap_support(r,736)) and r['support'] and r['native_state']==0 and abs(y-112)<=1
                if not full:go('lost-full-third-cap',r,support_feet=cap_support(r,736));break
                wait_samples+=1
                walkers=[a for a in r['actors'] if a['id']==6 and a['state']<2]
                if len(walkers)==2 and all(a['dir']==2 and a['x']<=848 for a in walkers):
                    go('standing-takeoff' if args.departure=='standing' else 'run',r,
                        walkers=walkers,stable_support_samples=wait_samples)
            if stage=='run' and 736<=x<=765 and abs(y-112)<=2 and C.Recovery.running(model,r):go('takeoff',r)
            elif stage in ('takeoff','standing-takeoff') and r['action'] in (3,4):go('third-flight',r)
            elif stage=='third-flight' and x>=784 and y==176 and r['support']:go('floor-approach',r)
            if stage=='floor-approach' and x>=897:go('wall-approach',r)
            elif stage=='floor-approach' and args.approach=='careful' and r['frame']==15 and r['mode']==0:
                go('wall-precareful',r,native_state=r['native_state'],support=r['support'])
            if stage=='wall-precareful' and r['support'] and r['native_state']==0:
                go('wall-careful',r)
            if stage=='wall-approach' and r['frame']==15 and r['mode']==0 and r['support']:
                go('wall-careful' if x<897 else 'original-Up-no-horizontal',r)
            if stage=='wall-careful' and r['action'] not in (0,1):go('wall-careful-settle',r)
            elif stage=='wall-careful-settle' and r['frame']==15 and r['mode']==0 and r['support']:
                go('wall-careful' if x<897 else 'original-Up-no-horizontal',r)
            if stage=='original-Up-no-horizontal' and r['action'] in (24,25,10):go('climb',r)
            if stage in ('original-Up-no-horizontal','climb') and any(cap_support(r,912)) and abs(y-112)<=1 and r['native_state']==0 and r['support']:
                go('fourth-anchor-step',r,support_feet=cap_support(r,912))
            if stage=='fourth-anchor-step' and r['action'] not in (0,1,10):go('fourth-anchor-settle',r)
            elif stage=='fourth-anchor-settle' and r['frame']==15 and r['mode']==0:
                if not(all(cap_support(r,912)) and r['native_state']==0 and r['support'] and abs(y-112)<=1):
                    go('fourth-full-cap-not-established',r,support_feet=cap_support(r,912));break
                cap=True;go('fourth-cap',r,support_feet=cap_support(r,912))
            if stage=='fourth-cap':go('cap-run',r)
            if stage=='cap-run' and x>=960 and y==176 and r['support']:go('pit-approach',r)
            if stage=='pit-approach' and 1059<=x<=1090 and C.Recovery.running(model,r):go('pit-takeoff',r)
            elif stage=='pit-takeoff' and r['action']==4:go('pit-flight',r)
            elif stage=='pit-flight' and x>=1152 and y==176 and r['support']:go('first-gap-clear',r);break
            if stage in ('original-Up-no-horizontal','climb') and x>=944 and y>=172:go('unqualified-pipe-crossing',r);break
            if tick-changed>400 and stage!='wait-walkers':go('controller-bound',r);break
            pad={'park-run':1,'park-brake':2,'park-careful':65,'park-settle':0,'wait-walkers':0,'run':1,'takeoff':129,'standing-takeoff':129,
                'third-flight':1,'floor-approach':1,'wall-approach':0,'wall-precareful':0,'wall-careful':65,
                'wall-careful-settle':0,'original-Up-no-horizontal':8,
                'climb':8,'fourth-anchor-step':65,'fourth-anchor-settle':0,
                'fourth-cap':1,'cap-run':1,'pit-approach':1,'pit-takeoff':129,'pit-flight':1}[stage]
            if not pads or pads[-1]['pad']!=pad:pads.append(dict(start=tick,pad=pad))
            C.Route.controls(env,model,labels,pad);N.consume(model)
        else:stage='bounded'
    print('WAIT_POSE_ROUTE '+json.dumps(dict(in_memory_SHA256=layout['in_memory_SHA256'],
        outcome=stage,actual_fourth_cap=cap,maximum_X=maximum,wait_anchor=wait_anchor,
        stable_wait_support_samples=wait_samples,events=events,HP_debits=HP,pads=pads,
        poses=poses,source_action_entries=source,terminal=row(),terrain=F.terrain_signature(model),
        helpers_added=0,ROM_written=False,outputs_written=0),separators=(',',':')),flush=True)


if __name__=='__main__':main()
