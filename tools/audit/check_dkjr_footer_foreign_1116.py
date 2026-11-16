"""Owning footer foreign/timer real RunLargePlatform continuations, no files."""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from unittest.mock import patch

import check_dkjr_footer_ryu_1116 as R
import check_dkjr_carry_camera_route_1116 as Route

C,N,W,L,Q=R.C,R.N,R.W,R.L,R.Q
H=lambda value:sha256(value).hexdigest()


def snapshot(m,result):
    # N.invoke asserts the actual complete farcall return SP224 internally.
    return (R.native_data(m),bytes(m[0x15a:0x17b]),tuple(result[k]for k in('A','X','Y','P')))


def component(base,parent,candidate,owner,timer,*,direct_dk=False):
    outputs=[];cost=[];events=[]
    for raw in(parent,candidate):
        m=R.mount(base,raw)
        N.put(m,SelectedCharacter=owner,TimerControl=timer,ObjectOffset=3,Z2Variant=int(owner==4),RyuSourceBodyProfile=25)
        if direct_dk:
            assert owner==40 and timer
            N.put(m,Player_State=2,Player_Y_Speed=0,Player_Y_Position=106)
            m[0x65b]=136;m[0xbe+3]=138;m[0x566+3]=3
        seen=[]
        def observe(memory,c):
            tag=memory.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
            if(tag,c.pc)in((186,0xbf5c),(186,0xbf83),(128,0xb453)):
                seen.append([tag,c.pc])
        Base=N.NesMPU
        class Observed(Base):
            def step(self):
                observe(m,self);return Base.step(self)
        with patch.object(N,'NesMPU',Observed):
            result=N.invoke(m,'RunLargePlatform',a=85,x=3,y=91,p=0x79)
        outputs.append(snapshot(m,result));cost.append(result['CPU']);events.append(seen)
    assert outputs[0][0]==outputs[1][0] and outputs[0][2]==outputs[1][2],(
        owner,timer,direct_dk,'complete RunLargePlatform AXYP/native/private/maps/VRAM',
        [i for i,(a,b)in enumerate(zip(outputs[0],outputs[1]))if a!=b])
    differences=[0x15a+i for i,(a,b)in enumerate(zip(outputs[0][1],outputs[1][1]))if a!=b]
    return dict(delta=cost[1]-cost[0],parent=cost[0],candidate=cost[1],events=events,
        intermediate_public_function_SMC=differences)


def mains(parent,candidate):
    inventory=Q.Roster.Starts.C.inventory(parent)['rows'];rows=[]
    names=('MINI MARIO','LINK','ZELDA II LINK','RYU HAYABUSA','THOMAS','JAY MCCRAY','FF FIGHTER','HULK HOGAN')
    selected=[next(r for r in inventory if r['raw']==0)]+[next(r for r in inventory if r['name']==name)for name in names]
    for row in selected:
        name=row['name']
        bundle=W.Symbols.bundle();bundle['raw']=parent
        _,seed=Q.Roster.cold(bundle,row)
        models=[R.mount(seed,raw)for raw in(parent,candidate)]
        for m in models:
            for slot in range(6):N.invoke(m,'EraseEnemyObject',x=slot)
            for field,value in dict(Enemy_ID=37,Enemy_Flag=1,Enemy_State=0,
                Enemy_X_Position=N.get(m,'Player_X_Position'),Enemy_PageLoc=N.get(m,'Player_PageLoc'),
                Enemy_Y_Position=(N.get(m,'Player_Y_Position')+32)&255,Enemy_Y_HighPos=1).items():m[W.address(m.bundle,field)+3]=value
            N.invoke(m,'InitEnemyObject',x=3);m[W.address(m.bundle,'Enemy_BoundBoxCtrl')+3]=5
        cycles=[[],[]];calls=[Counter(),Counter()];first_consumer_rows=[]
        for tick in range(8):
            cuts=[None,None]
            for index,m in enumerate(models):
                def watch(memory,c):
                    tag=memory.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
                    if(tag,c.pc)==(128,0xb43f):calls[index]['dispatch']+=1
                    if(tag,c.pc)==(128,0xb442) and cuts[index]is None:cuts[index]=L.clone(memory,c)
                cycles[index].append(Q.frame(m,0 if tick<4 else 1,watch))
            assert R.native_data(models[0])==R.native_data(models[1]),(name,tick,'complete Main data')
            assert bytes(models[0][0x15a:0x17b])==bytes(models[1][0x15a:0x17b]),(name,tick,'SMC33')
            assert models[0].contact_frame_registers==models[1].contact_frame_registers,(name,tick,'actual Main AXYP')
            if all(cuts):
                differing={at for at in range(0x15a,0x17b)if cuts[0][0][at]!=cuts[1][0][at]}
                if differing:
                    outputs=[];accesses=Counter()
                    for state,cpu in cuts:
                        m,c=L.clone(state,cpu);R.Old.tracked(m,c,differing)
                        L.finish(m,c,(W.address(m.bundle,'IdleLoop')+12,252))
                        accesses.update(op for op,_,_ in m.smc_events)
                        outputs.append(R.Old.outcome(m,c))
                    assert outputs[0]==outputs[1],(name,tick,'actual first-consumer SMC continuation')
                    first_consumer_rows.append(dict(tick=tick,addresses=sorted(differing),
                        all_reads_follow_current_writers=True,accesses=dict(accesses)))
        assert calls[0]==calls[1] and calls[0]['dispatch']>=8
        rows.append(dict(name=name,raw=row['raw'],actual_Main_updates=8,calls=dict(calls[0]),
            first_consumer_SMC=first_consumer_rows,
            additional_Main_cycles=sorted(set(b-a for a,b in zip(*cycles)))))
        print('DKJR_FOOTER_FOREIGN_MAIN '+json.dumps(rows[-1],separators=(',',':')),flush=True)
    return rows


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--public',type=Path,required=True)
    ap.add_argument('--mains',action='store_true');args=ap.parse_args()
    public=args.public.read_bytes();parent,_=C.Camera.proposal(public);candidate,composition=C.proposal(parent)
    assert C.inverse(candidate)==parent
    _,seed=Route.cold(parent);base=Q.C.setup(seed)
    count=Counter();deltas=[];differing_SMC=set();first_SMC_negative=None
    cases={(owner,timer)for owner,timer in product((0,4,9,10,11,16,40,41),range(256))}
    cases|={(owner,timer)for owner,timer in product(range(256),(0,1))}
    print('DKJR_FOOTER_FOREIGN_PHASE complete-native-functions '+str(len(cases)),flush=True)
    for owner,timer in sorted(cases):
        row=component(base,parent,candidate,owner,timer);deltas.append(row['delta']);count['complete_native_function']+=1
        differing_SMC.update(row['intermediate_public_function_SMC'])
        if row['intermediate_public_function_SMC'] and first_SMC_negative is None:
            first_SMC_negative=dict(owner=owner,timer=timer,addresses=row['intermediate_public_function_SMC'])
    for timer in(1,254,255):
        row=component(base,parent,candidate,40,timer,direct_dk=True)
        assert row['events'][0]!=row['events'][1]
        count['paused_DK_direct_matches_prepared_parent']+=1
    actual=mains(parent,candidate)if args.mains else None
    report=dict(passed=True,composition=composition,cases=dict(count),actual_foreign_cold_Main=actual,
        complete_RunLargePlatform_AXYP_native_private_maps_graphics_exact=True,
        initial_full33_at_nested_boundary_negative_retained=first_SMC_negative,
        intermediate_public_function_SMC=sorted(differing_SMC),
        SMC_live_first_consumers_and_complete_Main_all33_checked=bool(actual),
        additional_cycles_min=min(deltas),additional_cycles_max=max(deltas),
        no_performance_gain_claim=True,scope='Declared native actor/timer fixtures; optional actual foreign cold/Main fixtures, no natural route/native claim',output_files=0)
    encoded=json.dumps(report,sort_keys=True,separators=(',',':'))
    print('DKJR_FOOTER_FOREIGN '+encoded,flush=True);print('DKJR_FOOTER_FOREIGN_SHA256 '+H(encoded.encode()),flush=True)


if __name__=='__main__':main()
