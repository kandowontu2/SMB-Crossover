"""Zero-output source routes with the authentic CF cookie observer."""
import argparse
import json
from unittest.mock import patch

import check_contra_force_full11_1114 as Previous
import replay_contra_force_full11_v2_1114 as Factory


def metadata(raw,key):
    with patch.object(Previous,'Factory',Factory):return Previous.metadata(raw,key)


def run(raw,key,limit=8500):
    with patch.object(Previous,'Factory',Factory):return Previous.run(raw,key,limit)


def prefix(raw,key):
    """Run the same full controller through real first-pipe/camera traversal."""
    config=Factory.bindings(raw,key);base=Previous.Harness.Frames.frame;last={};frames=0
    class Reached(Exception):pass
    def observed(m,*args,**kwargs):
        nonlocal frames,last
        result=base(m,*args,**kwargs)
        if kwargs.get('whole_pass'):
            frames+=1;n=Factory.N
            x=n.get(m,'Player_X_Position')+256*n.get(m,'Player_PageLoc')
            camera=n.get(m,'ScreenLeft_X_Pos')+256*n.get(m,'ScreenLeft_PageLoc')
            last=dict(Main=frames,x=x,y=n.get(m,'Player_Y_Position'),camera=camera,
                state=n.get(m,'Player_State'),lives=n.get(m,'NumberofLives'),
                source_variant=m.ram[2][0x2e0],power=n.get(m,'PlayerStatus'))
            if x>=496 and last['y']==176 and last['state']==0 and camera>=256:
                assert last['lives']==2 and last['source_variant']==config['variant']
                assert bytes(m.ram[2][0x1fe0:0x1ff0])==bytes(config['cf']['cookie'])
                assert bytes(m.ram[3][0x1fe0:])==bytes(32)
                raise Reached
        return result
    try:
        with patch.object(Previous.Harness.Frames,'frame',observed):q=run(raw,key,1500)
    except Reached:
        return dict(passed=True,identity=key,ROM_SHA256=Factory.PIN,
            controller_SHA256=Factory.sha256(Factory.controller(raw,key).encode()).hexdigest(),
            actual_first_pipe_and_camera_prefix=last,complete_C2_cookie_and_zero_C3_tail=True,
            original_full_controller_unchanged=True,full_route_not_claimed=True,
            gameplay_seeds=0,outputs=0,Mesen_run=False)
    raise AssertionError(('CF first-pipe prefix failed',last,q))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--identity',choices=Factory.IDENTITIES,required=True)
    p.add_argument('--metadata',action='store_true');p.add_argument('--prefix',action='store_true')
    p.add_argument('--limit',type=int,default=8500);args=p.parse_args()
    raw=Factory.ROM.read_bytes();q=metadata(raw,args.identity)if args.metadata else prefix(raw,args.identity)if args.prefix else run(raw,args.identity,args.limit)
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not args.metadata:assert q['passed'],'Separate CF full-route source gate not passed'
