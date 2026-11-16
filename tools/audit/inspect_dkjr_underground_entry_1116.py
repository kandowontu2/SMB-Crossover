"""Direct passive source1-2 first-writer check over unchanged F8716 inputs."""
from collections import Counter
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
import sys

import replay_dkjr_pipe5_depart_defense_1116 as F
import check_dkjr_carry_camera_route_1116 as R

C,N=F.C,R.N
H=lambda value:sha256(value).hexdigest()
SOURCE_SHA='3fa55eccc6205a72f4d0670c4d72e7ad15fb8d8bbed36c6c247038919995b108'
NATIVE_SHA='da23374911949adc34af173f8bd351f4980a59ef1e5d6546e1e7f41f3797e936'


def snapshot(m,tick,previous,c=None):
    r=m.ram[2];row=dict(R.B.state(m))
    row.update(host_update=tick,ready=r[0x8fe],phase=r[0x6b],prior=r[0x6c],
        origin=r[0x76],limit=r[0x7b],facing=r[0x6d],age=r[0x7e],source_y=r[0x210],
        source_x=r[0x213],source_held=r[0x14],source_fresh=r[0x15],pad=m.controller_pad,
        nativeVY=N.get(m,'Player_Y_Speed'),query_kind=r[0x8db],query=list(r[0x3e:0x42]),
        contact=list(r[0x42:0x46]),window=list(r[0x8e8:0x8ec]),native_body=list(m[0x658:0x65c]),
        area_type=N.get(m,'AreaType'),level=N.get(m,'LevelNumber'),world=N.get(m,'WorldNumber'))
    if c is not None:row.update(PC=c.pc,SP=c.sp,A=c.a,X=c.x,Y=c.y,P=c.p,writer=previous)
    return row


def main(*,binding_only=False):
    parent=C.BT.ROM.read_bytes();raw,composition=C.proposal(parent);assert C.inverse(raw)==parent
    text=F.controller(raw,source=True);assert H(text.encode())==SOURCE_SHA
    opening,m=R.cold(raw)
    tick=0;watching=False;ready=None;previous=None;pending=None;observer_seen=False
    events={};counts=Counter();body=C.Camera.payload(raw);stdout=sys.stdout
    origin_writers={0xa000+i for i in range(0x1fde)if body[i:i+3]==bytes.fromhex('8d76c0')}
    phase_writers={0xa000+i for i in range(0x1fde)if body[i:i+3]==bytes.fromhex('8d6bc0')}
    area=N.address(m.bundle,'AreaType');level=N.address(m.bundle,'LevelNumber');world=N.address(m.bundle,'WorldNumber')
    class BindingReached(Exception):pass
    def first(name,memory,c=None):
        if name not in events:
            assert len(events)<8
            events[name]=snapshot(memory,tick,previous,c)
    def observe(memory,c):
        nonlocal ready,previous,pending,observer_seen
        observer_seen=True
        if not watching:return
        r=memory.ram[2];tag=memory.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
        if r[0x8fe]==2 and ready!=2:first('first-anchored-ready2',memory,c)
        ready=r[0x8fe]
        if(tag,c.pc)==(2,0xd65e):
            counts['actual_motor_entries']+=1;first('first-1-2-motor-entry',memory,c)
            assert pending is None
            ret=(memory[0x100+((c.sp+1)&255)]+256*memory[0x100+((c.sp+2)&255)]+1)&65535
            pending=(ret,(c.sp+2)&255)
        if pending==(c.pc,c.sp):
            counts['actual_motor_returns']+=1;pending=None
            if r[0x6b]==5:first('first-phase5-motor-return',memory,c)
        if(tag,c.pc)==(3,0xbd93):counts['native_injury_BD93']+=1
        if(tag,c.pc)==(3,0xbd9f):counts['native_deathstart_BD9F']+=1
        if tag==3 and c.pc in origin_writers:first('first-original-origin-store',memory,c)
        if(tag,c.pc)==(3,0xa8ce):first('first-original-landing-decision',memory,c)
        if tag==3 and c.pc in phase_writers and c.a==5:first('first-original-phase5-store',memory,c)
        previous=dict(PC=c.pc,tag=tag,A=c.a,X=c.x,Y=c.y,P=c.p,SP=c.sp,
            bytes=bytes(memory[(c.pc+i)&65535]for i in range(3)).hex())
    def after(memory):
        nonlocal tick,watching,ready
        tick+=1
        if binding_only:
            assert observer_seen
            json.dumps(snapshot(memory,tick,None));json.dumps(snapshot(memory,tick,None,N.NesMPU(memory=memory)))
            raise BindingReached()
        if tick%1000==0:print('DKJR_ENTRY_PROGRESS '+json.dumps(dict(tick=tick,**R.B.state(memory)),separators=(',',':')),file=stdout,flush=True)
        active=memory[area]==2 and memory[level]==1 and memory[world]==0
        if active and not watching:
            watching=True;ready=memory.ram[2][0x8fe];first('first-completed-1-2-entry-frame',memory)
        if watching:
            counts['completed_1-2_host_updates']+=1
            counts['engine_'+str(N.get(memory,'GameEngineSubroutine'))]+=1
    try:
        with redirect_stdout(io.StringIO()):
            result=R.B.route(m,raw,15000,controller_text=text,observe_extra=observe,after_frame=after)
    except BindingReached:
        assert binding_only and tick==1 and observer_seen
        print('DKJR_ENTRY_BINDING '+json.dumps(dict(passed=True,source_ROM_SHA256=H(raw),source_Lua_SHA256=H(text.encode()),
            actual_observer_reached=True,actual_host_frames=1,executed_schema_branches=2,
            direct_route_call=True,no_AST_or_monkeypatch=True,outputs=0),separators=(',',':')),flush=True)
        return
    assert observer_seen
    q=result.get('receipt')or{}
    report=dict(diagnostic_complete=bool(events),original_strong_gameplay_passed=bool(result['passed']),
        composition_receipt_SHA256=H(json.dumps(composition,sort_keys=True,separators=(',',':')).encode()),
        source_ROM_SHA256=H(raw),source_Lua_SHA256=H(text.encode()),
        native_Lua_reference_SHA256=NATIVE_SHA,source_updates=tick,
        counts=dict(counts),events=events,reason=q.get('reason'),terminal=R.B.state(m),
        actual_12_returns=q.get('actual_12_returns'),grounded_12_returns=q.get('grounded_12_return_count'),
        witness_bound=8,source_controls_unchanged=True,direct_route_call=True,new_game_bytes=0,outputs=0,
        scope='Actuala3fb source first completed1-2 entry frame onward, motor tokens and first real writers; no native or full-route positive.')
    encoded=json.dumps(report,sort_keys=True,separators=(',',':'))
    print('DKJR_UNDERGROUND_ENTRY '+encoded,flush=True);print('DKJR_UNDERGROUND_ENTRY_SHA256 '+H(encoded.encode()),flush=True)
    assert result['passed'],report['reason']


if __name__=='__main__':main(binding_only='--binding-only'in sys.argv)
