"""Actual current join full-route source check; controller inputs only."""
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
import sys

import replay_dkjr_backward_stairs_current_root_1116 as F

C,Route=F.Previous.C,F.Previous.Route
H=lambda value:sha256(value).hexdigest()


def main():
    actual=C.BT.ROM.read_bytes();raw,composition=C.proposal(actual)
    assert C.inverse(raw)==actual
    source=F.controller(raw,source=True);native=F.controller(raw)
    opening,m=Route.cold(raw)
    tick=0;stdout=sys.stdout;first_source5=None;native_injury=[];previous=None
    def observe(memory,cpu):
        nonlocal first_source5,previous
        tag=memory.rawtags[(cpu.pc-0x8000)//8192]if cpu.pc>=0x8000 else-1
        if memory[0x75]+256*memory[0x5c]>=2600:
            r=memory.ram[2]
            def view():
                actors=[]
                for i in range(6):
                    if Route.N.get(memory,'Enemy_Flag',i):
                        actors.append(dict(slot=i,id=Route.N.get(memory,'Enemy_ID',i),
                            x=Route.N.get(memory,'Enemy_X_Position',i)+256*Route.N.get(memory,'Enemy_PageLoc',i),
                            y=Route.N.get(memory,'Enemy_Y_Position',i),state=Route.N.get(memory,'Enemy_State',i)))
                return dict(tick=tick,PC=cpu.pc,tag=tag,A=cpu.a,X=cpu.x,Y=cpu.y,P=cpu.p,SP=cpu.sp,
                    writer=previous,**Route.B.state(memory),prior=r[0x6c],facing=r[0x6d],
                    fall_origin=r[0x76],fall_limit=r[0x7b],source_hurt=r[0x68],actors=actors)
            if(tag,cpu.pc)==(3,0xbd93) and len(native_injury)<4:native_injury.append(view())
            if r[0x6b]==5 and first_source5 is None:first_source5=view()
            previous=dict(PC=cpu.pc,tag=tag,A=cpu.a,X=cpu.x,Y=cpu.y,P=cpu.p,SP=cpu.sp,
                bytes=bytes(memory[(cpu.pc+i)&65535]for i in range(3)).hex())
    def after(memory):
        nonlocal tick
        tick+=1
        if tick%1000==0:print('DKJR_BACKWARD_PROGRESS '+json.dumps(dict(tick=tick,**Route.B.state(memory)),separators=(',',':')),file=stdout,flush=True)
    with redirect_stdout(io.StringIO()):
        result=Route.B.route(m,raw,15000,controller_text=source,observe_extra=observe,after_frame=after)
    q=result.get('receipt')or{}
    report=dict(passed=bool(result['passed']),composition=composition,opening=opening,
        native_controller_SHA256=H(native.encode()),source_controller_SHA256=H(source.encode()),
        ability_plan_SHA256=F.ABILITY_SHA,original_backward_jump_component_receipt='6e2812c123265f888dfb5e19964ee0d2d0c2b47ac9dc1484faede5f33ab23d3c',
        source_updates=tick,reason=q.get('reason'),terminal=Route.B.state(m),
        injury=q.get('injury'),actual_native_injury_entries=native_injury,first_source5=first_source5,
        original_grounded_12_returns=q.get('grounded_12_return_count'),actual_12_returns=q.get('actual_12_returns'),
        first_grounded_12_return=q.get('first_grounded_12_return'),last_grounded_12_return=q.get('last_grounded_12_return'),
        events=q.get('events',[])[-16:],crossings=q.get('crossings'),
        carries={k:dict(count=v.get('count'),first=v.get('first'),last=v.get('last'))for k,v in q.get('carries',{}).items()},
        scope='Actuala3fb compiled menu/input/source full route; 25 grounded completed originalD65E returns, not hostMain-only. No native claim.',
        source_only=True,game_state_seeds=0,new_game_bytes=0,new_helpers=0,outputs=0)
    encoded=json.dumps(report,sort_keys=True,separators=(',',':'))
    print('DKJR_BACKWARD_FULL '+encoded,flush=True)
    print('DKJR_BACKWARD_FULL_SHA256 '+H(encoded.encode()),flush=True)
    assert result['passed'],report['reason']


if __name__=='__main__':main()
