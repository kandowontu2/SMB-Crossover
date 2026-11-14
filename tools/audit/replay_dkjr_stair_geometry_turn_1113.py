"""Universal geometry-derived backward staircase jumps, on strict769 only."""
from contextlib import redirect_stdout
from hashlib import sha256
import argparse
import io
import json
import sys

import replay_dkjr_odd_stair_turn_1113 as Previous
from check_ff_stdout_controller_source_1110 import LuaRuntime

T,Gate=Previous.T,Previous.Gate
LUA_PIN='80ef49e799e7d59775cc8a81ae7f5ef14207240e4d78b90c7b54f68105261386'


def controller(raw):
    text=Previous.donor_ground_controller(raw)
    assert sha256(text.encode()).hexdigest()==Previous.DONOR_GROUND_LUA_PIN
    body=T.P.T.payload(raw)
    assert body[0xb019-0xa000:0xb019-0xa000+4]==bytes((5,0,24,15))
    backward_right_extent=body[0xb019-0xa000+2]-8
    assert backward_right_extent==16
    W=Gate.W;b=W.Symbols.bundle();b['raw']=raw
    at=W.location(b,'MTileAttribute');attrs=raw[at:at+256]
    solid=''.join('1'if value&3==1 else'0'for value in attrs)
    buffers=[W.address(b,name)for name in('Block_Buffer_1','Block_Buffer_2')]
    assert text.count('finalRiser==3 or finalRiser==5')==2
    text=text.replace('finalRiser==3 or finalRiser==5','finalRiser>=1 and finalRiser<=6')
    geometry=f'''    local sourceSolids='{solid}'
    local function solidAt(wx,wy)
     assert(wy>=32 and wy<240,'Actual stair query row')
     local base=((wx>>8)&1)==1 and {buffers[1]} or {buffers[0]}
     local tile=read(base+((wy-32)&240)+((wx>>4)&15))
     return sourceSolids:sub(tile+1,tile+1)=='1'
    end
    local top=y+16;local nextCell
    for wx=math.floor((player-16)/16)*16,math.floor((player+80)/16)*16,16 do
     if solidAt(wx,top)and not solidAt(wx,top-16)then nextCell=wx;break end
    end
    assert(nextCell,'Missing authored next stair top')
    local geometryAnchor=nextCell-{backward_right_extent}
    assert(geometryAnchor==2912+16*(finalRiser-1),'Unexpected authored stair column')
    local stage=geometryAnchor-12'''
    text=T.P.once(text,'    local stage=2912+16*(finalRiser-1)-12',geometry)
    text=T.P.once(text,'events[#events].native_state_at_request=read(0x1e)',
        'events[#events].native_state_at_request=read(0x1e);events[#events].next_tile_left=nextCell;events[#events].next_tile_top=top;events[#events].takeoff_stage=stage')
    text=text.replace('odd-backward','stair-backward').replace('odd-riser preparation','staircase preparation')
    LuaRuntime().compile(text)
    if LUA_PIN is not None:assert sha256(text.encode()).hexdigest()==LUA_PIN
    return text


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--route',action='store_true')
    args=ap.parse_args();parent,raw=T.load_inputs();text=controller(raw)
    info=dict(candidate_SHA256=T.PIN,Lua_SHA256=sha256(text.encode()).hexdigest(),Lua_compiled=True,
        all_six_authored_risers=True,next_top_from_live_authored_cells=True,
        original_backward_body_right_extent=16,runup_before_derived_anchor=12,
        original_input_facing_jump_acknowledgements=True,ROM_or_game_writes=False,outputs_written=0)
    if args.route:
        Q,P,H=Gate.Q,Gate.P,Gate.H
        e73=T.Old.reverse(parent);_,seed=H.cold(e73,e73[P.B.COOKIE_AT:P.B.COOKIE_AT+16])
        m=Q.mounted(seed,raw);updates=0;output=sys.stdout
        def after(mem):
            nonlocal updates
            updates+=1
            if updates%1500==0:print('DKJR_GEOMETRY_TURN_PROGRESS '+json.dumps(dict(Main=updates,final=P.B.state(mem)),separators=(',',':')),file=output,flush=True)
        with redirect_stdout(io.StringIO()):result=P.B.route(m,raw,12000,controller_text=text,after_frame=after)
        receipt=result.get('receipt')or{}
        info.update(passed=result['passed'],logical_updates=result['logical_updates'],
            final=result['final'],reason=receipt.get('reason'),
            stair_events=[r for r in receipt.get('events',[])if'stair'in r.get('event','')],
            receipt_SHA256=sha256(json.dumps(receipt,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            physical_cadence_claim=False,endpoint='Existing active falling1-2 endpoint; not25 grounded updates.')
    print('DKJR_GEOMETRY_TURN '+json.dumps(info,separators=(',',':')),flush=True)
    if args.route:assert info['passed'],info


if __name__=='__main__':main()
