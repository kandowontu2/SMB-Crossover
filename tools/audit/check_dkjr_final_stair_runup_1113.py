"""Earlier latched-Right jumps, with/without neutral release; no game writes."""
from contextlib import redirect_stdout
from itertools import product
from hashlib import sha256
import io
import json
import sys

import check_dkjr_final_stair_branches_1113 as Base

T,Q,P,H,N,W,L=Base.T,Base.Q,Base.P,Base.H,Base.N,Base.W,Base.L


def main():
    parent,candidate=T.load_inputs();e73=T.Old.reverse(parent)
    _,seed=H.cold(e73,e73[P.B.COOKIE_AT:P.B.COOKIE_AT+16]);m=Q.mounted(seed,candidate)
    text=T.controller(candidate,full=True,departure_enemy_guard=True,approach_enemy_guard=True)
    ticks=0;branch=None;output=sys.stdout
    class AtBranch(Exception):pass
    def after(m):
        nonlocal ticks,branch
        ticks+=1;s=Base.state(m)
        if ticks%1500==0:print('DKJR_RUNUP_PREFIX '+json.dumps(dict(Main=ticks,x=s['x'],y=s['y']),separators=(',',':')),file=output,flush=True)
        if 2930<=s['x']<=2934 and s['y']==112 and s['source_state']==s['prior']==1:
            branch=L.clone(m);raise AtBranch
    with redirect_stdout(io.StringIO()):
        try:P.B.route(m,candidate,8200,controller_text=text,after_frame=after)
        except AtBranch:pass
    assert branch is not None
    print('DKJR_RUNUP_BRANCH_POINT '+json.dumps(dict(candidate_SHA256=T.PIN,
        Lua_SHA256=sha256(text.encode()).hexdigest(),genuine_Main=ticks,state=Base.state(branch)),separators=(',',':')),flush=True)
    rows=[]
    for takeoff,release_ticks in product((2928,2930,2932,2944),(0,4)):
        q=L.clone(branch);phase='align';release=None;launch=None;events=[];lands=[];cause=[]
        minimum=255;maximum=0;grounded=0;passed=False;upper_seen=False
        for age in range(150):
            s=Base.state(q);pad=0
            if phase=='align':
                pad=1 if s['x']<takeoff else 2 if s['x']>takeoff else 0
                if s['x']==takeoff and s['y']==112 and s['source_state']==s['prior']==1 and s['state']==0:
                    phase='release';release=age;pad=0;events.append((age,'ready',s['x'],s['y']))
            if phase=='release'and age-release>=release_ticks:
                phase='jump';launch=age;pad=129;events.append((age,'Right+A',s['x'],s['y']))
            elif phase=='jump':pad=129 if age-launch<8 else 1
            def watch(mem,c):
                if mem.rawtags[1]!=3:return
                if c.pc==0xa966 and mem.ram[2][0x43]==128:
                    lands.append(dict(age=age,native_x=N.get(mem,'Player_X_Position')+256*N.get(mem,'Player_PageLoc'),
                        source_y=mem.ram[2][0x210],target_rect=list(mem.ram[2][0x42:0x46])))
                if c.pc==0xa321 and mem.ram[2][0x6b]==3 and len(cause)<4:
                    cause.append(dict(age=age,jump_age=mem.ram[2][0x7e],rect=list(mem.ram[2][0x3e:0x46])))
            Q.frame(q,pad,watch);s=Base.state(q);minimum=min(minimum,s['y']);maximum=max(maximum,s['x'])
            if s['source_state']==5 or s['engine']==11 or s['lives']!=2:break
            upper=s['y']==96 and s['source_state']==1
            if upper and not upper_seen:events.append((age+1,'source-upper-contact',s['x'],s['y']));upper_seen=True
            settled=upper and s['prior']==1 and s['state']==0
            grounded=grounded+1 if settled else 0
            if s['x']>=2944 and grounded>=3 and lands:
                passed=True;events.append((age+1,'actual-upper-floor',s['x'],s['y']));break
        row=dict(takeoff=takeoff,neutral_release_updates=release_ticks,passed=passed,updates=age+1,
            minimum_native_y=minimum,max_native_x=maximum,events=events,actual_upper_landings=lands,
            inclusive_side_cancellations=cause,final=Base.state(q))
        rows.append(row);print('DKJR_RUNUP_STAIR_BRANCH '+json.dumps(row,separators=(',',':')),flush=True)
    print('DKJR_RUNUP_STAIR_SCOPE '+json.dumps(dict(genuine_prefix_Main=ticks,
        passing=[(r['takeoff'],r['neutral_release_updates'])for r in rows if r['passed']],
        ordinary_inputs_only=True,source_air_direction_latched=True,state_or_ROM_writes=False,
        outputs_written=0,physical_cadence_claim=False),separators=(',',':')),flush=True)


if __name__=='__main__':main()
