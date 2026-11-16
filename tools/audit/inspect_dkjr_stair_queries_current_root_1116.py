"""Actual current-join support lists and camera epochs at a natural stair landing."""
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
from pathlib import Path

import compose_dkjr_footer_bt91dc_current_1116 as C
import check_dkjr_stair_query_contract_1116 as Contract
import replay_dkjr_clear_stair_head_root_1116 as Controls
import check_dkjr_carry_camera_route_1116 as Route

H=lambda value:sha256(value).hexdigest()
CONTRACT_SHA='c6acf234c17271c609fdc8ef7dd993a83de4f68ee7ea2e4489badc1a49580fce'
CONTROL_SHA='285fb570ca6ca79632b326b4b702a0cda82dc5890f15cb84f9be62ad5c196e41'


def controller(raw,*,source=False):
    assert H(raw)==C.CANDIDATE and H(Path(Controls.__file__).read_bytes())==CONTROL_SHA
    historical=C.historical_reference(raw)
    assert C.Camera.payload(historical)==C.Camera.payload(raw)
    before=Controls.controller(historical,source=source)
    assert before.count(C.Footer.CANDIDATE)==(2 if source else 1)
    after=before.replace(C.Footer.CANDIDATE,C.CANDIDATE)
    assert after.replace(C.CANDIDATE,C.Footer.CANDIDATE)==before
    Controls.Previous.Frozen.Frozen.Frozen.Prior.Ground.LuaRuntime().compile(after)
    return after


def main():
    public=C.BT.ROM.read_bytes();raw,composition=C.proposal(public)
    assert C.inverse(raw)==public
    assert H(Path(Contract.__file__).read_bytes())==CONTRACT_SHA
    contract=Contract.contract(raw);body=C.Camera.payload(raw)
    text=controller(raw,source=True);opening,m=Route.cold(raw)
    assert m.bundle['raw']==raw
    support=contract['entries']['DkjrSupportProbe']['PC']
    world=contract['entries']['DkjrNativeWorldBuild']['PC']
    hook=contract['entries']['DkjrNativeTerrainHook']['PC']
    # These are real JSR/return bytes within the authenticated full hook.
    assert body[0xb304-0xa000:0xb307-0xa000]==b'\x20'+world.to_bytes(2,'little')
    tick=0;events=[];seen=0;pending=None;landed=None;last_phase=None
    class Enough(Exception):pass
    def snapshot(memory,cpu,event,**extra):
        nonlocal seen
        seen+=1
        if len(events)>=128:return
        r=memory.ram[2];n=r[0x8dd]
        q=dict(event=event,tick=tick,PC=cpu.pc,SP=cpu.sp,A=cpu.a,X=cpu.x,Y=cpu.y,P=cpu.p,
            nativeX=memory[0x75]+256*memory[0x5c],nativeY=memory[0xbd],nativeState=memory[0x1e],
            camera=memory[0x71f]+256*memory[0x71d],cached_camera=r[0x435]+256*r[0x436],
            camera_ready=r[0x437],camera_delta=r[0x438],sourceX=r[0x213],sourceY=r[0x210],sourceState=r[0x6b],
            body=list(r[0x3e:0x42]),prior_contact=list(r[0x42:0x46]),nativeBox=list(memory[0x658:0x65c]),
            kind=r[0x8db],window=list(r[0x8e8:0x8ec]),count=n,pad=memory.controller_pad,
            maps=list(memory.rawtags),**extra)
        if event=='world-return':
            assert n<=60 and n%4==0 and r[0x800+n]==255
            q['fresh_support_list']=[list(r[0x800+i:0x804+i])for i in range(0,n,4)]
        events.append(q)
    def observe(memory,cpu):
        nonlocal pending,landed,last_phase
        x=memory[0x75]+256*memory[0x5c]
        if tick<5000 or not 2110<=x<=2144:return
        tag=memory.rawtags[(cpu.pc-0x8000)//8192]if cpu.pc>=0x8000 else-1
        phase=memory.ram[2][0x6b]
        if phase!=last_phase:
            if phase==1 and last_phase==3 and memory.ram[2][0x210]<191:
                landed=tick
            snapshot(memory,cpu,'source-phase',previous_source_state=last_phase)
            last_phase=phase
        if phase!=3 and landed is None:return
        if tag==3 and cpu.pc==support:
            assert pending is None
            ret=(memory[0x100+((cpu.sp+1)&255)]+256*memory[0x100+((cpu.sp+2)&255)]+1)&65535
            ret_tag=memory.rawtags[(ret-0x8000)//8192]if ret>=0x8000 else-1
            pending=(ret,(cpu.sp+2)&255,ret_tag)
            snapshot(memory,cpu,'support-entry',actual_return=list(pending))
        if pending is not None and(cpu.pc,cpu.sp,tag)==pending:
            snapshot(memory,cpu,'support-return')
            pending=None
        if tag==3 and cpu.pc==world and memory.ram[2][0x8db]in(3,4):
            snapshot(memory,cpu,'world-entry')
        if tag==3 and cpu.pc==0xb307 and memory.ram[2][0x8db]in(3,4):
            snapshot(memory,cpu,'world-return')
    def after(memory):
        nonlocal tick
        tick+=1
        if landed is not None and tick>=landed+4:raise Enough()
    with redirect_stdout(io.StringIO()):
        try:result=Route.B.route(m,raw,6500,controller_text=text,observe_extra=observe,after_frame=after)
        except Enough:result=None
    report=dict(actual_candidate_SHA256=H(raw),composition=composition,contract_SHA256=CONTRACT_SHA,
        controller_source_SHA256=H(text.encode()),control_factory_SHA256=CONTROL_SHA,opening=opening,
        events=events,events_seen=seen,dropped_events=max(0,seen-len(events)),landed_tick=landed,
        source_updates=tick,terminal=Route.B.state(m),scope='Actual a3fb natural menu/input prefix, fresh support-list and per-query camera witness; not a native/full clear or new patch.',
        gameplay_seeds=0,outputs=0)
    encoded=json.dumps(report,sort_keys=True,separators=(',',':'))
    print('DKJR_CURRENT_STAIR_QUERIES '+encoded,flush=True)
    print('DKJR_CURRENT_STAIR_QUERIES_SHA256 '+H(encoded.encode()),flush=True)
    assert landed is not None and report['dropped_events']==0


if __name__=='__main__':main()
