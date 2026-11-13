"""Measure original Jay jump holds from a controller-reached authored opening."""

from collections import Counter
import argparse
import json

import compose_jay_head_bridge_1113 as P

B=P.B
N,W=B.Current.N,B.Current.W


def opening(image):
    _,m=P.cold(image,P.NEW_COOKIE,P.CANDIDATE_PIN)
    parked=None
    for epoch in range(300):
        s=B.Current.state(m)
        actors=[B.Current.actor(m,i)for i in range(6)if N.get(m,'Enemy_Flag',i)]
        near=any(a['id']<21 and not a['state']&32 and 0<a['x']-s['x']<100 and abs(a['y']-s['Player_Y_Position'])<30 for a in actors)
        shot=64 if near and epoch%12<2 else 0
        if parked is None and s['x']>=304 and s['Player_State']==0:parked=epoch
        if parked is not None and epoch-parked>=12:
            assert s['JnHealth']==6 and s['NumberofLives']==2 and s['Player_Y_Position']==176
            assert 304<=s['x']<308
            return m
        m.controller_pad=(1 if parked is None else 0)+shot
        B.Current.Frames.frame(m)
    raise AssertionError('Controller open-floor approach bound')


def measure(seed,hold):
    m=B.Current.C.L.clone(seed)
    linked=B.Gun.C.Jay.build();ram=linked['ram'];symbols=linked['symbols']
    counts=Counter();trace=[]
    before=B.Current.state(m)
    airborne=False
    apex=before['Player_Y_Position']
    for epoch in range(160):
        def observe(m,c):
            if m.rawtags[1]==3:
                for name in ('CancelUpwardVelocity','SideBlocked'):
                    if c.pc==symbols[name]:counts[name]+=1
            if c.pc==W.address(m.bundle,'PlayerHeadCollision') and m.rawtags[0]==254:
                counts['native_head']+=1
        m.controller_pad=128 if epoch<hold else 0
        B.Current.Frames.frame(m,observe)
        state=B.Current.state(m)
        state.update(epoch=epoch+1,held=epoch<hold,jump_hold=m.ram[2][ram[0x51]-0xc000],
                     donor_VY=m.ram[2][ram[0x15]-0xc000])
        trace.append(state)
        apex=min(apex,state['Player_Y_Position'])
        airborne|=state['Player_State']!=0
        if airborne and state['Player_State']==0:
            break
    else:raise AssertionError(('Jump landing bound',hold,trace[-1]))
    assert not counts and all(v['x']==before['x'] and v['JnHealth']==6 for v in trace),counts
    return dict(hold_updates=hold,start=before,apex_Y=apex,rise=before['Player_Y_Position']-apex,
                landing_update=trace[-1]['epoch'],jump_hold_values=sorted(set(v['jump_hold']for v in trace)),
                contact_counts=dict(counts),trace=[v for v in trace if v['epoch']<=16 or v['Player_Y_Position']==apex])


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--detail',action='store_true')
    args=parser.parse_args()
    import compose_jay_pickup_helper_1113 as Helper
    image=Helper.frozen_head()
    seed=opening(image)
    results=[measure(seed,h)for h in(1,12,18,28,40,60)]
    if not args.detail:
        results=[{k:v for k,v in row.items()if k not in('start','trace')}for row in results]
    print(json.dumps(dict(ROM_SHA256=P.CANDIDATE_PIN,controller_only=True,output_files=0,
        start=B.Current.state(seed),original_physics_unchanged=True,results=results)),flush=True)
