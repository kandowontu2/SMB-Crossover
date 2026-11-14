"""Strict769 ordinary early backward-facing jumps for final risers3/5."""
import argparse
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
import sys

import compose_dkjr_direct_platform_1113 as T
import check_dkjr_direct_platform_1113 as Gate
from check_ff_stdout_controller_source_1110 import LuaRuntime

BASE_LUA='6c6aac8a3d0fdfe334beebcf62b4514014e45d9e044f43926b3ee38e261c8d73'
LUA_PIN='aa926b0cbb63f880652c8dc8ea3d09bfd8a766a36b014934ec8623f4246e8f48'
DONOR_GROUND_LUA_PIN='cd3004a7ffa3cdd4926dff58ab9d501c10339cdc0fae7daa81a17fa214b53487'


def controller(raw):
    assert sha256(raw).hexdigest()==T.PIN
    text=T.controller(raw,full=True,departure_enemy_guard=True,approach_enemy_guard=True)
    assert sha256(text.encode()).hexdigest()==BASE_LUA
    text=T.P.once(text,'local finalRiser,finalRiserStart,finalRiserAttempts=1,nil,0',
        'local finalRiser,finalRiserStart,finalRiserAttempts=1,nil,0\nlocal oddStairPrep')
    text=T.P.once(text,'finalRiser=finalRiser+1;finalRiserStart,finalRiserAttempts,finalWaitX,finalLandAt=nil,0,nil,nil',
        'finalRiser=finalRiser+1;finalRiserStart,finalRiserAttempts,finalWaitX,finalLandAt=nil,0,nil,nil;oddStairPrep=nil')
    text=T.P.once(text," if phase=='final-stairs'then\n",''' if phase=='final-stairs'and oddStairPrep and oddStairPrep.request and not oddStairPrep.ack then
  if ram(2,0x6b)==3 and ram(2,0x6d)==0 and ram(2,0x54)==4 and ram(2,0x14)&129==129 then
   oddStairPrep.ack=true;remember('odd-backward-ack-'..finalRiser)
   events[#events].original_facing=ram(2,0x6d);events[#events].original_direction=ram(2,0x54)
   events[#events].original_held=ram(2,0x14);events[#events].original_sample=ram(2,0x15)
  else
   assert(updates-oddStairPrep.request<16,'Original backward jump was not acknowledged')
   hold=math.max(hold,updates+2)
  end
 end
 if phase=='final-stairs'then
''')
    marker='  elseif settled and y==144-16*(finalRiser-1)then\n'
    text=T.P.once(text,marker,marker+'''   if finalRiser==3 or finalRiser==5 then
    local stage=2912+16*(finalRiser-1)-12
    if not oddStairPrep then oddStairPrep={riser=finalRiser,start=updates,phase='align'}end
    assert(updates-oddStairPrep.start<120,'Bounded original odd-riser preparation')
    if not finalRiserStart or updates-finalRiserStart>=47 then
     assert(finalRiserAttempts<4,'Repeated original odd-riser jump')
     if oddStairPrep.phase=='requested'then oddStairPrep.phase='align'end
     if oddStairPrep.phase=='align'then
      hold=0;right,left=player<stage,player>stage+1
      if player>=stage and player<=stage+1 then oddStairPrep.phase='left';right,left=false,true end
     elseif oddStairPrep.phase=='left'then
      hold=0;right,left=false,true
      local originalLeft=ram(2,0x6d)==0 and ram(2,0x54)==3 and ram(2,0x14)&130==2
      if originalLeft and player>=stage-1 and player<=stage+1 then
       oddStairPrep.phase='requested';oddStairPrep.request=updates;oddStairPrep.ack=false
       hold=updates+8;finalRiserStart=updates;finalRiserAttempts=finalRiserAttempts+1
       right,left=true,false;remember('odd-backward-jump-'..finalRiser)
       events[#events].original_facing=ram(2,0x6d);events[#events].original_direction=ram(2,0x54)
       events[#events].original_held=ram(2,0x14);events[#events].original_sample=ram(2,0x15)
      elseif player<stage-1 then oddStairPrep.phase='align';right,left=true,false end
     end
    end
   else
''')
    start=text.index(" if phase=='final-stairs'then\n")
    end=text.index(" if phase=='final-cap'then\n",start)
    fragment=text[start:end]
    closing='  end\n end\n'
    assert fragment.endswith(closing)
    fragment=fragment[:-len(closing)]+'   end\n'+closing
    text=text[:start]+fragment+text[end:]
    LuaRuntime().compile(text)
    if LUA_PIN is not None:assert sha256(text.encode()).hexdigest()==LUA_PIN
    return text


def donor_ground_controller(raw):
    """The donor's ground acknowledgement admits the preparation, including
    native inset-foot state2; all original settled landing gates stay exact.
    """
    text=controller(raw)
    text=T.P.once(text,'  elseif settled and y==144-16*(finalRiser-1)then',
        '  elseif (settled or ((finalRiser==3 or finalRiser==5)and ram(2,0x6b)==1 and ram(2,0x6c)==1 and ram(2,0x210)==y+15))and y==144-16*(finalRiser-1)then')
    text=T.P.once(text,"right,left=true,false;remember('odd-backward-jump-'..finalRiser)",
        "right,left=true,false;remember('odd-backward-jump-'..finalRiser)\n       events[#events].native_state_at_request=read(0x1e)")
    LuaRuntime().compile(text)
    if DONOR_GROUND_LUA_PIN is not None:assert sha256(text.encode()).hexdigest()==DONOR_GROUND_LUA_PIN
    return text


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--route',action='store_true')
    ap.add_argument('--donor-ground',action='store_true')
    a=ap.parse_args();parent,raw=T.load_inputs();text=donor_ground_controller(raw)if a.donor_ground else controller(raw)
    result=dict(candidate_SHA256=T.PIN,base_Lua_SHA256=BASE_LUA,
        Lua_SHA256=sha256(text.encode()).hexdigest(),Lua_compiled=True,
        odd_risers=[3,5],runup_before_anchor=12,
        acknowledged_donor_ground_for_preparation=a.donor_ground,
        donor_Left_and_jump_acknowledgement=True,ROM_or_game_writes=False,outputs_written=0)
    if a.route:
        Q,P,H=Gate.Q,Gate.P,Gate.H
        e73=T.Old.reverse(parent);_,seed=H.cold(e73,e73[P.B.COOKIE_AT:P.B.COOKIE_AT+16])
        model=Q.mounted(seed,raw);updates=0;output=sys.stdout
        def after(mem):
            nonlocal updates
            updates+=1
            if updates%1500==0:print('DKJR_ODD_TURN_PROGRESS '+json.dumps(dict(Main=updates,final=P.B.state(mem)),separators=(',',':')),file=output,flush=True)
        with redirect_stdout(io.StringIO()):route=P.B.route(model,raw,12000,controller_text=text,after_frame=after)
        receipt=route.get('receipt')or{}
        result.update(passed=route['passed'],logical_updates=route['logical_updates'],
            reason=receipt.get('reason'),final=route['final'],last_events=receipt.get('events',[])[-25:],
            receipt_SHA256=sha256(json.dumps(receipt,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            physical_cadence_claim=False,endpoint='Existing active falling1-2 endpoint; not25 grounded updates.')
    print('DKJR_ODD_TURN '+json.dumps(result,separators=(',',':')),flush=True)
    if a.route:assert result['passed'],result


if __name__=='__main__':main()
