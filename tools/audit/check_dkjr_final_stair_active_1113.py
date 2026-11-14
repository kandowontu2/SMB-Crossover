"""Exercise emitted final-stair Lua on a genuine ordinary-control prefix."""
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
import sys

import check_dkjr_final_stair_branches_1113 as Base
import replay_dkjr_final_stair_takeoff_1113 as Proposal
from check_ff_stdout_controller_source_1110 import LuaRuntime

T,Q,P,H,N,W,L=Base.T,Base.Q,Base.P,Base.H,Base.N,Base.W,Base.L
OLD_PREDICATE='(fast or finalRiser==1) and player>=takeoff-2 and player<takeoff and camera()>=anchor-80'
NEW_PREDICATE='((fast and finalRiser~=3)or finalRiser==1) and player>=takeoff-2 and player<takeoff and camera()>=anchor-80'


def policy(raw,model,active):
    text=Proposal.active_controller(raw)if active else T.controller(raw,full=True,
        departure_enemy_guard=True,approach_enemy_guard=True)
    assert text.count(' local fast=true\n')==1
    start=text.index(" if phase=='final-stairs'then\n")
    end=text.index(" if phase=='final-cap'then\n",start)
    fragment=text[start:end]
    assert fragment.count('if '+(NEW_PREDICATE if active else OLD_PREDICATE)+' then')==1
    predicate=NEW_PREDICATE if active else OLD_PREDICATE
    fragment=fragment.replace('if '+predicate+' then',
        'if '+OLD_PREDICATE+' then predicateEvents[#predicateEvents+1]={updates,player,camera(),'+predicate+'} end\n    if '+predicate+' then',1)
    rt=LuaRuntime(unpack_returned_tuples=True)
    rt.globals().read=lambda at:model[at]
    rt.globals().ram=lambda bank,at:model.ram[bank][at]
    rt.globals().camera=lambda:N.get(model,'ScreenLeft_X_Pos')+256*N.get(model,'ScreenLeft_PageLoc')
    rt.globals().nativeX=lambda:N.get(model,'Player_X_Position')+256*N.get(model,'Player_PageLoc')
    rt.globals().nativeY=lambda:N.get(model,'Player_Y_Position')
    code='''
local fast=true
local finalRiser,finalRiserStart,finalRiserAttempts=3,nil,0
local finalWaitX,finalWaitStart,finalLandAt
local finalLaunches={{2912,2912,2907},{2923,2928,2925},{2939,2944,2941},
 {2955,2960,2957},{2971,2976,2973},{2987,2991,2992,2989}}
local phase,hold,rearm,updates='final-stairs',0,0,0
local events,predicateEvents={},{}
local function remember(name)events[#events+1]={updates,name,nativeX(),nativeY()}end
local function setPhase(name)phase=name end
return function(age)
 updates=age;local player,y=nativeX(),nativeY()
 local settled=ram(2,0x6b)==1 and read(0x1e)==0
 local right,left=false,false
'''+fragment+'''
 return (right and 1 or 0)|(left and 2 or 0)|(updates<hold and 128 or 0),finalRiser,events,predicateEvents
end
'''
    return rt.execute(code),sha256(text.encode()).hexdigest(),sha256(fragment.encode()).hexdigest()


def values(row):
    return [[item[i]for i in range(1,len(item)+1)]for item in(row[j]for j in range(1,len(row)+1))]


def main():
    parent,candidate=T.load_inputs();e73=T.Old.reverse(parent)
    _,seed=H.cold(e73,e73[P.B.COOKIE_AT:P.B.COOKIE_AT+16]);m=Q.mounted(seed,candidate)
    text=T.controller(candidate,full=True,departure_enemy_guard=True,approach_enemy_guard=True)
    ticks=0;branch=None;output=sys.stdout
    class AtBranch(Exception):pass
    def after(mem):
        nonlocal ticks,branch
        ticks+=1;s=Base.state(mem)
        if ticks%1500==0:print('DKJR_ACTIVE_PREFIX '+json.dumps(dict(Main=ticks,x=s['x'],y=s['y']),separators=(',',':')),file=output,flush=True)
        if 2930<=s['x']<=2934 and s['y']==112 and s['source_state']==s['prior']==1:
            branch=L.clone(mem);raise AtBranch
    with redirect_stdout(io.StringIO()):
        try:P.B.route(m,candidate,8200,controller_text=text,after_frame=after)
        except AtBranch:pass
    assert branch is not None
    # This diagnostic setup consists solely of real Right then neutral input,
    # reproducing the observed post-clamp2942/camera2864 predicate domain.
    prepared=L.clone(branch);preparation=[]
    for age in range(100):
        s=Base.state(prepared)
        if s['x']==2944 and s['y']==112 and s['source_state']==s['prior']==1 and s['state']==0:break
        Q.frame(prepared,1)
    else:raise AssertionError(('No ordinary2944 preparation',Base.state(prepared)))
    preparation.append(dict(event='walked-anchor',updates=age,state=Base.state(prepared)))
    for _ in range(4):Q.frame(prepared,0)
    preparation.append(dict(event='neutral-four',updates=age+4,state=Base.state(prepared)))
    assert Base.state(prepared)['x']==2942 and Base.state(prepared)['camera']==2864
    rows=[]
    for active in(False,True):
        q=L.clone(prepared);drive,lua_sha,fragment_sha=policy(candidate,q,active)
        lands=[];settled=0;passed=False;error=None;events=[];predicates=[]
        for age in range(160):
            try:pad,riser,event_rows,predicate_rows=drive(age)
            except Exception as exc:error=str(exc);break
            events=values(event_rows);predicates=values(predicate_rows)
            def watch(mem,c):
                if mem.rawtags[1]==3 and c.pc==0xa966 and mem.ram[2][0x43]==128:
                    lands.append(dict(age=age,native_x=N.get(mem,'Player_X_Position')+256*N.get(mem,'Player_PageLoc'),target=list(mem.ram[2][0x42:0x46])))
            Q.frame(q,pad,watch);s=Base.state(q)
            upper=s['x']>=2944 and s['y']==96 and s['source_state']==s['prior']==1 and s['state']==0
            settled=settled+1 if upper else 0
            if settled>=3 and lands:passed=True;break
            if s['source_state']==5 or s['engine']==11 or s['lives']!=2:break
        row=dict(active=active,passed=passed,updates=age+1,controller_SHA256=lua_sha,
            actual_emitted_fragment_SHA256=fragment_sha,predicate_events=predicates[:16],
            predicate_event_count=len(predicates),events=events,actual_upper_landings=lands,
            script_error=error,final=Base.state(q))
        rows.append(row);print('DKJR_ACTIVE_SUFFIX '+json.dumps(row,separators=(',',':')),flush=True)
    print('DKJR_ACTIVE_SCOPE '+json.dumps(dict(genuine_prefix_Main=ticks,
        preparation=preparation,active_branch_reached=bool(rows[1]['predicate_event_count']),
        all_active_early_predicates_suppressed=all(not q[3]for q in rows[1]['predicate_events']),
        active_crossing_passed=rows[1]['passed'],ordinary_inputs_only=True,
        actual_emitted_Lua_fragment=True,source_or_native_state_writes=False,
        outputs_written=0,physical_cadence_claim=False),separators=(',',':')),flush=True)
    assert rows[1]['predicate_event_count']>0,'Executed active predicate was not reached'
    assert all(not q[3]for q in rows[1]['predicate_events']),'Active early fallback was not suppressed'
    assert rows[1]['passed'],'Active emitted policy did not reach a settled actual upper floor'


if __name__=='__main__':main()
