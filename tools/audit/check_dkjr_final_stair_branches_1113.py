"""Ordinary final-riser3 controls from a genuine full-prefix clone; stdout."""
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
import sys

import compose_dkjr_direct_platform_1113 as T
import check_dkjr_direct_platform_1113 as Gate

Q,P,H,N,W,L=Gate.Q,Gate.P,Gate.H,Gate.N,Gate.W,Gate.L


def state(m):
    row=P.B.state(m)
    row.update(prior=m.ram[2][0x6c],jump_age=m.ram[2][0x7e],
        source_rect=list(m.ram[2][0x3e:0x46]),direction=m.ram[2][0x54],
        native_box=list(m[0x658:0x65c]),source_fields={hex(at):m.ram[2][at]for at in(0x56,0x6d,0x6f,0x70,0x75,0x76,0x7b)})
    return row


def main():
    parent,candidate=T.load_inputs();e73=T.Old.reverse(parent)
    _,seed=H.cold(e73,e73[P.B.COOKIE_AT:P.B.COOKIE_AT+16]);m=Q.mounted(seed,candidate)
    text=T.controller(candidate,full=True,departure_enemy_guard=True,approach_enemy_guard=True)
    ticks=0;branch=None;output=sys.stdout
    class AtBranch(Exception):pass
    def after(m):
        nonlocal ticks,branch
        ticks+=1;s=state(m)
        if ticks%1500==0:print('DKJR_FINAL_PREFIX '+json.dumps(dict(Main=ticks,state=s),separators=(',',':')),file=output,flush=True)
        if 2930<=s['x']<=2934 and s['y']==112 and s['source_state']==s['prior']==1:
            branch=L.clone(m);raise AtBranch
    with redirect_stdout(io.StringIO()):
        try:P.B.route(m,candidate,8200,controller_text=text,after_frame=after)
        except AtBranch:pass
    assert branch is not None
    print('DKJR_FINAL_BRANCH_PREFIX '+json.dumps(dict(candidate_SHA256=T.PIN,
        Lua_SHA256=sha256(text.encode()).hexdigest(),genuine_Main=ticks,state=state(branch),
        actual_authored_cells=[dict(x=x,tiles={str(y):branch[(0x3d0 if(x>>8)&1 else 0x300)+((y-32)&240)+((x>>4)&15)]
            for y in(96,112,128,144,160)})for x in(2928,2944,2960,2976)]),separators=(',',':')),flush=True)
    rows=[]
    for takeoff in(2934,2936,2938,2940,2942,2944):
        q=L.clone(branch);trace=[];events=[];reached=False;launch=None;phase='align';minimum=255
        for age in range(120):
            s=state(q);pad=0
            if phase=='align':
                pad=1 if s['x']<takeoff else 2 if s['x']>takeoff else 0
                if s['x']==takeoff and s['source_state']==s['prior']==1:
                    phase='release';release=age;events.append((age,'ready',s['x'],s['y']))
            elif phase=='release':
                if age-release>=4:
                    phase='jump';launch=age;pad=129;events.append((age,'fresh-A',s['x'],s['y']))
            elif phase=='jump':pad=129 if age-launch<8 else 1
            def watch(mem,c):
                if mem.rawtags[1]!=3:return
                own=(c.pc in(0xa210,0xa734))or(mem[c.pc]==0x8d and bytes(mem[c.pc+1:c.pc+3])==bytes.fromhex('6bc0'))
                if own:
                    if len(trace)>=64:del trace[8]
                    trace.append(dict(age=age,pc=c.pc,A=c.a,source=mem.ram[2][0x6b],prior=mem.ram[2][0x6c],
                        jump_age=mem.ram[2][0x7e],sourceY=mem.ram[2][0x210],sourceX=mem.ram[2][0x213],
                        rect=list(mem.ram[2][0x3e:0x46])))
            Q.frame(q,pad,watch);after=state(q);minimum=min(minimum,after['y'])
            if after['source_state']==5 or after['engine']==11 or after['lives']!=2:break
            if launch is not None and after['x']>=2944 and after['y']==96 and after['source_state']==1:
                reached=True;events.append((age+1,'third-top',after['x'],after['y']));break
        row=dict(takeoff=takeoff,passed=reached,updates=age+1,minimum_native_y=minimum,
            events=events,final=state(q),original_transition_and_state_trace=trace)
        rows.append(row);print('DKJR_FINAL_STAIR_BRANCH '+json.dumps(row,separators=(',',':')),flush=True)
    print('DKJR_FINAL_STAIR_SCOPE '+json.dumps(dict(passing_takeoffs=[r['takeoff']for r in rows if r['passed']],
        genuine_prefix_Main=ticks,ordinary_inputs_only=True,state_or_geometry_writes=False,
        outputs_written=0,physical_cadence_claim=False,native_behind_case_qualified=False),separators=(',',':')),flush=True)


if __name__=='__main__':main()
