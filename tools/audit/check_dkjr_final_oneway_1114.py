"""One genuine cap-jump prefix; diagnose native-actor floor contribution.

The disabled arm redirects only source's Platforms query leaf to its RTS.
This declared diagnostic is not a game image or gameplay qualification.
Native actors, motion, native LPC and static floors remain active.
"""
from contextlib import redirect_stdout
import io
import json
import sys
from unittest.mock import patch

import replay_dkjr_final_handoff_1114 as F

G,T=F.Gate,F.T
Q,P,H,N,W,L=G.Q,G.P,G.H,G.N,G.W,G.L


def view(m):
    s=P.B.state(m);r=m.ram[2]
    s.update(prior=r[0x6c],jump_age=r[0x7e],fraction=r[0x7f],
        acceleration=r[0x82]+256*r[0x83],impulse=r[0x86]+256*r[0x87],
        native_vy=N.get(m,'Player_Y_Speed'),source_rect=list(r[0x3e:0x46]),
        native_box=list(m[0x658:0x65c]),query_kind=r[0x8db])
    for slot in range(6):
        if N.get(m,'Enemy_Flag',slot)and N.get(m,'Enemy_ID',slot)==37 and N.get(m,'Enemy_X_Position',slot)+256*N.get(m,'Enemy_PageLoc',slot)==3040:
            s['helper']=dict(slot=slot,top=N.get(m,'Enemy_Y_Position',slot),
                passenger=N.get(m,'PlatformCollisionFlag',slot),bbox=list(m[0x65c+4*slot:0x660+4*slot]))
    return s


def concise(state):
    keys=('x','y','source_y','source_state','prior','jump_age','fraction','acceleration','impulse',
        'native_vy','source_rect','native_box','query_kind','helper')
    return {key:state[key]for key in keys if key in state}


def concise_record(row):
    return dict(row,state=concise(row['state']))


def main():
    parent,raw=F.load_inputs();text=F.controller(raw);e73=T.Old.reverse(parent)
    _,seed=H.cold(e73,e73[P.B.COOKIE_AT:P.B.COOKIE_AT+16]);m=Q.mounted(seed,raw)
    ticks=0;branch=None;output=sys.stdout
    class AtJump(Exception):pass
    def after(mem):
        nonlocal ticks,branch
        ticks+=1;s=P.B.state(mem)
        if ticks%1500==0:print('DKJR_ONEWAY_PREFIX '+json.dumps(dict(Main=ticks,x=s['x'],y=s['y']),separators=(',',':')),file=output,flush=True)
        if s['x']>3000 and s['source_state']==3 and mem.ram[2][0x7e]==1:
            branch=L.clone(mem);raise AtJump
    with redirect_stdout(io.StringIO()):
        try:P.B.route(m,raw,8200,controller_text=text,after_frame=after)
        except AtJump:pass
    assert branch is not None
    labels=P.frozen_labels();platforms=labels['Platforms'];done=labels['ObjectsDone']
    body=T.P.T.payload(raw)
    assert body[done-0xa000]==0x60 and body[platforms-0xa000:platforms-0xa000+2]==bytes.fromhex('a205')
    print('DKJR_ONEWAY_START '+json.dumps(dict(Main=ticks,state=view(branch),
        diagnostic_skip_leaf=platforms,diagnostic_RTS=done),separators=(',',':')),flush=True)
    cases=[];CPU=N.NesMPU
    for enabled in(True,False):
        q=L.clone(branch);rows=[];writers=[];queries=[];native_contacts=[];lpc=[];skipped=0;step=0
        class Probe(CPU):
            def step(self):
                nonlocal skipped
                tag=q.rawtags[(self.pc-32768)//8192]if self.pc>=32768 else-1
                pc=self.pc;before=q.ram[2][0x6b]
                if(tag,pc)==(3,platforms):
                    query=dict(step=step,kind=q.ram[2][0x8db],state=view(q))
                    if len(queries)>=32:del queries[4]
                    queries.append(query)
                    if not enabled:skipped+=1;self.pc=done
                if(tag,pc)==(128,0xb453):
                    if len(lpc)>=32:del lpc[4]
                    lpc.append(dict(step=step,state=view(q)))
                if(tag,pc)==(199,0xac18):
                    if len(native_contacts)>=32:del native_contacts[4]
                    native_contacts.append(dict(step=step,slot=self.x,pending_y=self.a,state=view(q)))
                result=super().step();new=q.ram[2][0x6b]
                if before!=new:writers.append(dict(step=step,PC=pc,bank=tag,before=before,after=new,state=view(q)))
                return result
        with patch.object(N,'NesMPU',Probe):
            for step in range(1,65):
                Q.frame(q,129 if step<8 else 1);rows.append(dict(step=step,state=view(q)))
                if q.ram[2][0x6b]==5 or N.get(q,'NumberofLives')!=2:break
        cases.append(dict(platform_floor_contribution=enabled,diagnostic_skipped_queries=skipped,
            source_state_writers=[concise_record(row)for row in writers],
            rows=[concise_record(row)for row in rows[:12]+rows[-2:]],
            queries=[concise_record(row)for row in queries[:8]+queries[-2:]],
            actual_native_LPC_entries=[concise_record(row)for row in lpc[:10]],
            actual_native_passengers=[concise_record(row)for row in native_contacts[:4]],
            minimum_native_y=min(row['state']['y']for row in rows),final=view(q)))
    print('DKJR_ONEWAY_GENUINE_DIAGNOSTIC '+json.dumps(dict(candidate_SHA256=T.PIN,
        prefix_Lua_SHA256=F.LUA_PIN,genuine_prefix_Main=ticks,cases=cases,
        outputs_written=0,source_actor_state_or_geometry_writes=False,
        scope='Identical genuine source cap-jump prefix; disabled arm substitutes one declared query leaf RTS only. Native actor/LPC/static floor active. Diagnostic only, not a repaired image or native proof.'),separators=(',',':')),flush=True)


if __name__=='__main__':main()
