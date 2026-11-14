"""One genuine universal-stair prefix, then acknowledged cap-to-girder jump.

In-memory component only. Root owns the emulator queue. No state, geometry,
ROM, capture, or per-frame output files are written.
"""
from contextlib import redirect_stdout
from hashlib import sha256
import argparse
import io
import json
import sys

import replay_dkjr_stair_geometry_turn_1113 as Frozen
import check_dkjr_final_stair_branches_1113 as State
from replay_dkjr_final_handoff_1114 import load_inputs

T,G=Frozen.T,Frozen.Gate
Q,P,H,N,W,L=G.Q,G.P,G.H,G.N,G.W,G.L


def view(m):
    s=State.state(m)
    slots=[]
    for slot in range(6):
        if N.get(m,'Enemy_Flag',slot) and N.get(m,'Enemy_ID',slot)==37:
            x=N.get(m,'Enemy_X_Position',slot)+256*N.get(m,'Enemy_PageLoc',slot)
            if x==3040:
                a=0x65c+slot*4
                slots.append(dict(slot=slot,left=x,top=N.get(m,'Enemy_Y_Position',slot),
                    speed=N.get(m,'Enemy_Y_Speed',slot),passenger=m[0x566+slot],
                    bbox=list(m[a:a+4])))
    s['final_helpers']=slots
    return s


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--early-depart',action='store_true');args=ap.parse_args()
    parent,raw=load_inputs();text=Frozen.controller(raw);e73=T.Old.reverse(parent)
    _,seed=H.cold(e73,e73[P.B.COOKIE_AT:P.B.COOKIE_AT+16]);m=Q.mounted(seed,raw)
    ticks=0;branch=None;output=sys.stdout
    class AtCap(Exception):pass
    def after(mem):
        nonlocal ticks,branch
        ticks+=1;s=P.B.state(mem)
        if ticks%1500==0:print('DKJR_HANDOFF_PREFIX '+json.dumps(dict(Main=ticks,x=s['x'],y=s['y']),separators=(',',':')),file=output,flush=True)
        if s['x']>=2996 and s['y']==48 and s['source_state']==mem.ram[2][0x6c]==1:
            branch=L.clone(mem);raise AtCap
    with redirect_stdout(io.StringIO()):
        try:P.B.route(m,raw,8200,controller_text=text,after_frame=after)
        except AtCap:pass
    assert branch is not None,('No genuine top-six prefix',ticks,P.B.state(m))
    print('DKJR_HANDOFF_START '+json.dumps(dict(Main=ticks,state=view(branch)),separators=(',',':')),flush=True)
    phase='approach';events=[];passengers=[];cap_clear=None;launch=None;settled=0
    q=branch;final=None;failed=None
    def event(age,name,**extra):
        events.append(dict(age=age,event=name,state=view(q),**extra))
    for age in range(1200):
        s=view(q);pad=0;helpers=s['final_helpers'];helper=helpers[0]if helpers else None
        donor_ground=s['source_state']==s['prior']==1 and s['source_y']==s['y']+15
        if phase=='approach':
            pad=1 if s['x']<3027 else 0
            if s['x']>=3027 and donor_ground:
                phase='wait';event(age,'cap_wait')
        elif phase=='wait':
            # One geometry-derived timing: source's16px-high backward hop
            # starts while the descender approaches the cap's80px top.
            if helper and 64<=helper['top']<=68 and helper['speed']<128 and donor_ground:
                phase='left';pad=2;event(age,'prepare_backward',helper_top=helper['top'])
        elif phase=='left':
            pad=2
            if donor_ground and q.ram[2][0x6d]==0 and q.ram[2][0x54]==3 and q.ram[2][0x14]&130==2:
                phase='jump';launch=age;pad=129;event(age,'request_backward_right')
        elif phase=='jump':
            pad=(1 if s['x']<3048 else 0)|(128 if age-launch<8 else 0)
            if s['source_state']==3 and not any(e['event']=='acknowledged_jump'for e in events):
                assert q.ram[2][0x6d]==0 and q.ram[2][0x54]==4 and q.ram[2][0x14]&129==129
                event(age,'acknowledged_jump')
            if passengers and passengers[-1]['age']==age-1 and s['x']>=3048 and donor_ground:
                phase='lower';event(age,'actual_centered_passenger')
        elif phase=='lower':
            pad=1 if s['x']<3048 else 2 if s['x']>3049 else 0
            departure_top=160 if args.early_depart else 192
            if helper and passengers and passengers[-1]['age']==age-1 and departure_top<=helper['top']<=208 and helper['speed']<128:
                phase='depart';pad=1;event(age,'late_safe_departure')
        elif phase=='depart':
            pad=1
            if s['x']>=3080 and s['y']==176 and donor_ground:
                phase='floor';pad=0;event(age,'reached_floor')
        elif phase=='floor':
            settled=settled+1 if s['y']==176 and donor_ground else 0
            if settled>=25:final=s;break
        def watch(mem,c):
            if c.pc==0xac18 and mem.rawtags[1]==199 and helper and c.x==helper['slot']:
                assert mem[0x566+c.x]==c.x and c.a+32==N.get(mem,'Enemy_Y_Position',c.x)
                if len(passengers)<8 or age%16==0:
                    passengers.append(dict(age=age,slot=c.x,x=P.B.state(mem)['x'],top=N.get(mem,'Enemy_Y_Position',c.x),pending_y=c.a))
                else:passengers[-1]=dict(age=age,slot=c.x,x=P.B.state(mem)['x'],top=N.get(mem,'Enemy_Y_Position',c.x),pending_y=c.a)
        Q.frame(q,pad,watch);s=view(q)
        body_left=s['camera']+q.ram[2][0x213]+7;body_bottom=q.ram[2][0x210]+15
        if not cap_clear and body_left>3039:
            cap_clear=dict(age=age,left=body_left,bottom=body_bottom,cap_right=3039,cap_top=80)
            if body_bottom>=80:failed='Cap cleared after original body reached solid height';break
            event(age,'body_cleared_cap',clearance=cap_clear)
        if s['source_state']==5 or s['engine']==11 or s['lives']!=2:
            failed='Original injury or life loss';break
    else:failed='Bounded handoff component'
    result=dict(passed=final is not None,failed=failed,candidate_SHA256=T.PIN,
        frozen_prefix_Lua_SHA256=sha256(text.encode()).hexdigest(),genuine_prefix_Main=ticks,
        suffix_Main=age+1,phase=phase,events=events,passengers=passengers,
        earlier_descent_departure=args.early_depart,
        cap_clearance=cap_clear,final=final or view(q),outputs_written=0,
        ordinary_inputs_only=True,state_or_geometry_writes=False,physical_cadence_claim=False,
        scope='Single genuine source-route prefix and one adaptive ordinary-control suffix; not native/full-stage qualification.')
    print('DKJR_HANDOFF_COMPONENT '+json.dumps(result,separators=(',',':')),flush=True)
    assert result['passed'],result


if __name__=='__main__':main()
