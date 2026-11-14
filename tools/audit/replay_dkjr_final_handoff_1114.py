"""Acknowledged cap jump and early native-descender exit; strict private769."""
from contextlib import redirect_stdout
from hashlib import sha256
import argparse
import io
import json
from pathlib import Path
import sys

import replay_dkjr_final_board_1113 as Prior

T,Gate=Prior.T,Prior.Gate
LUA_PIN='5110d0244f3605d9f844bee3783703540a5c745db3874a5267b4eaa2394c182e'


def load_inputs():
    # The retained private image is a typed input. Future public nightlies
    # do not become implicit parents of this frozen769 controller.
    raw=(Path(__file__).resolve().parents[2]/'build/metal-flower-native-1112/candidate.nes').read_bytes()
    assert sha256(raw).hexdigest()==T.PIN
    parent=T.reverse(raw)
    assert T.transform(parent)[0]==raw
    return parent,raw


def controller(raw):
    text=Prior.early_controller(raw)
    assert sha256(text.encode()).hexdigest()==Prior.EARLY_LUA_PIN
    text=T.P.once(text,'local finalCapCleared','local finalJumpPrep\nlocal finalCapCleared')
    start=text.index(" if (phase=='final-cap'or phase=='final-board')and not finalCapCleared then\n")
    end=text.index(" if phase=='final-board'and stairTop then\n",start)
    safety=text[start:end].replace("(phase=='final-cap'or phase=='final-board')",
        "(phase=='final-cap'or phase=='final-turn'or phase=='final-jump')")
    #5 is the original backward-left body extent; using it throughout also
    # conservatively covers the standing extent7 after actual boarding.
    body=T.P.T.payload(raw)
    assert body[0xb019-0xa000:0xb019-0xa000+4]==bytes((5,0,24,15))
    safety=T.P.once(safety,'local bodyLeft=camera()+ram(2,0x213)+7',
        'local bodyLeft=camera()+ram(2,0x213)+5')
    start=text.index(" if phase=='final-cap'then\n")
    end=text.index(" if phase=='final-depart'then\n",start)
    new=''' if phase=='final-cap'then
  right=player<stairDown-13
  local donorGround=ram(2,0x6b)==1 and ram(2,0x6c)==1 and ram(2,0x210)==y+15
  if player>=stairDown-13 and donorGround and stairTop and priorTop[stairDown]and
   stairTop>=64 and stairTop<=68 and stairTop>=priorTop[stairDown]then
   hold=0;right,left=false,true;finalJumpPrep={start=updates};setPhase('final-turn',stairTop)
  end
 end
 if phase=='final-turn'then
  assert(updates-finalJumpPrep.start<120,'Bounded final cap backward preparation')
  hold=0;right,left=false,true
  local donorGround=ram(2,0x6b)==1 and ram(2,0x6c)==1 and ram(2,0x210)==y+15
  if donorGround and ram(2,0x6d)==0 and ram(2,0x54)==3 and ram(2,0x14)&130==2 then
   assert(player>=stairDown-15 and player<=stairDown-12,'Final cap preparation left supported anchor')
   finalJumpPrep.request=updates;hold=updates+8;right,left=true,false
   setPhase('final-jump',stairTop)
  end
 end
 if phase=='final-jump'then
  right,left=player<stairDown+8,false
  if not finalJumpPrep.ack then
   if ram(2,0x6b)==3 and ram(2,0x6d)==0 and ram(2,0x54)==4 and ram(2,0x14)&129==129 then
    finalJumpPrep.ack=updates;remember('final-backward-jump-ack',stairTop)
   else
    assert(updates-finalJumpPrep.request<16,'Original final backward jump was not acknowledged')
    hold=math.max(hold,updates+2)
   end
  end
 end
'''+safety+''' if phase=='final-jump'and stairTop then
  if player>=stairDown+8 and player<=stairDown+9 and finalSupport(stairTop)and finalCapCleared then
   right,left=false,false;setPhase('final-lower',stairTop)
   events[#events].native_passenger=finalNativePassenger
  end
 end
 if phase=='final-lower'and stairTop then
  local centerSafe=stairDown+8
  right,left=player<centerSafe,player>centerSafe+1
  if finalSupport(stairTop)and stairTop>=160 and stairTop<=170 and
   priorTop[stairDown]and stairTop>=priorTop[stairDown]then
   right,left=true,false;setPhase('final-depart',stairTop)
  end
 end
'''
    text=text[:start]+new+text[end:]
    Prior.LuaRuntime().compile(text)
    if LUA_PIN is not None:assert sha256(text.encode()).hexdigest()==LUA_PIN
    return text


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--route',action='store_true');args=ap.parse_args()
    parent,raw=load_inputs();text=controller(raw)
    info=dict(candidate_SHA256=T.PIN,Lua_SHA256=sha256(text.encode()).hexdigest(),compiled=True,
        frozen_stair_prefix_Lua_SHA256=Prior.Previous.LUA_PIN,
        original_backward_jump_acknowledgement=True,actual_native_passenger_required=True,
        helper_left=3040,helper_center=3056,helper_initial_top=192,
        centered_nativeX=3048,departure_top=[160,170],source_or_native_writes=False,outputs_written=0)
    if args.route:
        Q,P,H=Gate.Q,Gate.P,Gate.H;e73=T.Old.reverse(parent)
        _,seed=H.cold(e73,e73[P.B.COOKIE_AT:P.B.COOKIE_AT+16]);m=Q.mounted(seed,raw)
        updates=0;output=sys.stdout
        def after(mem):
            nonlocal updates
            updates+=1
            if updates%1500==0:print('DKJR_FINAL_HANDOFF_PROGRESS '+json.dumps(dict(Main=updates,final=P.B.state(mem)),separators=(',',':')),file=output,flush=True)
        with redirect_stdout(io.StringIO()):result=P.B.route(m,raw,12000,controller_text=text,after_frame=after)
        receipt=result.get('receipt')or{}
        info.update(passed=result['passed'],logical_updates=result['logical_updates'],final=result['final'],
            reason=receipt.get('reason'),last_events=receipt.get('events',[])[-20:],
            receipt_SHA256=sha256(json.dumps(receipt,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            physical_cadence_claim=False)
    print('DKJR_FINAL_HANDOFF '+json.dumps(info,separators=(',',':')),flush=True)
    if args.route:assert info['passed'],info


if __name__=='__main__':main()
