"""Actual emitted footer selector, restore and original fatal-fall contract."""
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


def front(m,footer,plane,*,vy=0,state=0,passenger=3,slot=3):
    m.raw_page(1,128);N.put(m,CurrentBank=128,SelectedCharacter=40,Player_Y_Speed=vy,Player_State=state,ObjectOffset=slot)
    m[0x65b]=footer;m[0xbe+slot]=plane;m[0x566+slot]=passenger
    c=N.NesMPU(memory=m,pc=0xb97e);c.a,c.x,c.y,c.p,c.sp=85,slot,91,0x79,224;c.stPushWord(0x5aff)
    for steps in range(500):
        tag=m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
        if(tag,c.pc)==(128,0xb453):
            expected=vy<128 and state%2==0 and passenger==slot and footer>=32 and plane-footer==2
            assert m[0x65b]==(plane if expected else footer),(footer,plane,vy,state,passenger,slot,m[0x65b])
            return expected,steps
        assert m[c.pc],('selector BRK',hex(c.pc));c.step()
    raise AssertionError(('selector bound',hex(c.pc),m.rawtags))


def restoration(seed,parent,candidate,slot,top,phase,distance,*,vy=0):
    base=Q.C.setup(seed)
    N.put(base,ObjectOffset=slot,SelectedCharacter=40,Player_X_Position=929&255,Player_PageLoc=929>>8,
        Player_Y_Position=top-32,Player_Y_HighPos=1,Player_State=2,Player_Y_Speed=vy,TimerControl=0)
    # Explicit actor/source component fixture, not an ordinary route.
    for i in range(6):N.invoke(base,'EraseEnemyObject',x=i)
    for field,value in dict(Enemy_ID=37,Enemy_Flag=1,Enemy_State=0,Enemy_BoundBoxCtrl=5,
        Enemy_X_Position=944&255,Enemy_PageLoc=944>>8,Enemy_Y_Position=top,Enemy_Y_HighPos=1,
        Enemy_Y_Speed=1,Enemy_Y_MoveForce=0,Enemy_YMoveForceFractional=0,PlatformCollisionFlag=slot).items():base[W.address(base.bundle,field)+slot]=value
    Route.Cold.H.call(base,0xb24c)
    r=base.ram[2];r[0x6b]=r[0x6c]=phase;r[0x76]=(r[0x210]-distance)&255;r[0x7b]=24;r[0x8fe]=2
    N.invoke(base,'RelativePlayerPosition',x=0);N.invoke(base,'HuFullBox',x=0)
    footer=base[0x65b];assert footer==top-2
    outputs=[];calls=[];restored=[]
    for raw in(parent,candidate):
        m=R.mount(base,raw);seen=Counter();at_dispatch=False
        Base=N.NesMPU
        class Observed(Base):
            def step(self):
                nonlocal at_dispatch
                tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
                if(tag,self.pc)==(128,0xb43f):
                    at_dispatch=True
                    if raw==parent and vy<128:m[0x65b]=footer+2
                if(tag,self.pc)==(128,0xb442):
                    if raw==parent:m[0x65b]=footer
                    assert m[0x65b]==footer,('footer escaped real collision return',slot,top,phase,distance)
                    seen['footer_restored_before_native_update']+=1
                if(tag,self.pc)==(199,0xac29):seen['actual_position']+=1
                return Base.step(self)
        with patch.object(N,'NesMPU',Observed):result=N.invoke(m,'RunLargePlatform',a=85,x=slot,y=91,p=0x79)
        assert at_dispatch and seen['footer_restored_before_native_update']==1
        outputs.append((R.native_data(m),tuple(result[k]for k in('A','X','Y','P'))))
        calls.append(dict(seen));restored.append(m[0x65b])
    assert outputs[0]==outputs[1],('counterfactual old LPC with explicitly declared footer sample',slot,top,phase,distance,vy)
    assert calls[0]==calls[1] and calls[1].get('actual_position',0)==int(vy<128)
    if phase in(3,4)and distance>=24:assert m.ram[2][0x6b]==5,('fatal fall was waived',phase,distance)
    return dict(calls=calls[1],source=m.ram[2][0x6b],footer_restored=True)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--public',type=Path,required=True)
    args=ap.parse_args();public=args.public.read_bytes();parent,_=C.Camera.proposal(public);candidate,composition=C.proposal(parent)
    assert C.inverse(candidate)==parent
    _,seed=Route.cold(candidate);m=R.mount(seed,candidate)
    counts=Counter();minimum_steps=10000;maximum_steps=0
    print('DKJR_FOOTER_COMPONENT_PHASE actual-65536-selector',flush=True)
    for footer,plane in product(range(256),repeat=2):
        admitted,steps=front(m,footer,plane);counts['footer_plane']+=1;counts['admitted_footer_plane']+=admitted
        minimum_steps=min(minimum_steps,steps);maximum_steps=max(maximum_steps,steps)
    for value in range(256):
        front(m,136,138,vy=value);counts['vertical_delta']+=1
        front(m,136,138,state=value);counts['native_state']+=1
        front(m,136,138,passenger=value);counts['previous_passenger']+=1
    for slot in range(6):
        for gap in(0,1,2,3):front(m,136,136+gap,slot=slot,passenger=slot);counts['slot_gap']+=1
    print('DKJR_FOOTER_COMPONENT_PHASE actual-restoration-fatalfall',flush=True)
    restored=[]
    for slot,top,phase,distance in product((0,3,5),(64,139,208),(1,3,4),(0,23,24,25)):
        restored.append(restoration(seed,parent,candidate,slot,top,phase,distance));counts['real_native_restore_oracle']+=1
    report=dict(passed=True,composition=composition,cases=dict(counts),selector_steps=[minimum_steps,maximum_steps],
        original_fatal_threshold24_preserved=True,real_native_LPC_position_and_restore=True,
        invalid_native_state_domain='Legal0..3 admits0/2 only. Manual bytes>=4 follow explicit parity predicate; no blanket all-invalid rejection claim.',
        history_contract='Synthetic source3/nativeVY0 with poisoned same-passenger can admit; legal fresh-jump/no-recapture must be separately qualified on actual candidate.',
        expected_oracle='Parent original LPC with an explicit temporary footer+2 data fixture and exact restoration before native movement. This is not ordinary gameplay evidence.',
        output_files=0,native_claim=False)
    encoded=json.dumps(report,sort_keys=True,separators=(',',':'))
    print('DKJR_FOOTER_COMPONENT '+encoded,flush=True);print('DKJR_FOOTER_COMPONENT_SHA256 '+H(encoded.encode()),flush=True)


if __name__=='__main__':main()
