"""Exactf11 DK jump request survives catch-up Main until native admission."""
from functools import lru_cache
from hashlib import sha256

import replay_dk_full11_near_current_1114 as Previous
import replay_dk_full11_current_1114 as Base

R,ROM,W,N,PIN=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.PIN
Frozen,IDENTITIES,normalize,bindings=Previous.Frozen,Previous.IDENTITIES,Previous.normalize,Previous.bindings
OLD_LUA_SHA='f875e53023f1cdbbd75b55b6a823256d80afd2983bfe2eaa8c8f02968ae6016f'


@lru_cache(maxsize=1)
def controller(raw,key='donkey_kong'):
    text=Previous.controller(raw,key);assert sha256(text.encode()).hexdigest()==OLD_LUA_SHA
    text=Base.once(text,'local choose=(function()',"""local dkLaunchTrace,dkLaunchInfo={},{}
local function keepLaunch(row)
 dkLaunchTrace[#dkLaunchTrace+1]=row
 if #dkLaunchTrace>32 then table.remove(dkLaunchTrace,17)end
end
local choose=(function()""")
    marker='local pairPhase,pairAge="approach",0'
    text=Base.once(text,marker,marker+"""
local function launchState(c,event)
 local row={event=event,phase=dkLaunchInfo.phase,Main=c.completed_main,frame=c.physical_frame,poll=c.physical_poll,
  movement=c.poll,x=c.x,y=c.y,state=c.state,vy=c.vy,pendingMain=c.pending_Main,
  SavedJoypadBits=c.r('SavedJoypadBits'),A_B_Buttons=c.r('A_B_Buttons'),
  PreviousA_B_Buttons=c.r('PreviousA_B_Buttons'),DkPrevious=c.r('DkPrevious')}
 keepLaunch(row);return row
end""")
    old="""  pairPhase='rise';pairAge=0;jumpAge=0
  return{right=true,b=true,a=true}
 elseif pairPhase=='rise'then"""
    new="""  pairPhase='requested';pairAge=0;jumpAge=0;dkLaunchInfo.phase='requested'
  dkLaunchInfo.requested=launchState(c,'request-A')
  return{right=true,b=true,a=true}
 elseif pairPhase=='requested'then
  pairAge=pairAge+1
  launchState(c,'await-native-admission')
  assert(pairAge<32,'Bounded actual native jump admission after requested A')
  if c.state==1 and c.vy>=128 then
   assert((c.r('SavedJoypadBits')&128)~=0 and(c.r('A_B_Buttons')&128)~=0
    and(c.r('PreviousA_B_Buttons')&128)~=0 and(c.r('DkPrevious')&128)~=0,'Actual A consumed by native DK movement')
   assert(c.y<dkLaunchInfo.requested.y,'Actual upward displacement after grounded request')
   pairPhase='rise';pairAge=1;dkLaunchInfo.phase='admitted'
   dkLaunchInfo.admission=launchState(c,'native-jump-admitted')
  end
  return{right=true,b=true,a=true}
 elseif pairPhase=='rise'then"""
    text=Base.once(text,old,new)
    text=Base.once(text,"   pairPhase='done'", "   pairPhase='done';dkLaunchInfo.phase='landed';dkLaunchInfo.landing=launchState(c,'actual-roof-landing')")
    text=Base.once(text,'local c={frame=dkMoves,poll=dkMoves,char=28',
        'local c={physical_frame=frame,physical_poll=polls,completed_main=updates,pending_Main=pendingReturn~=nil,frame=dkMoves,poll=dkMoves,char=28')
    marker="hook('DkMovement',function()"
    body="""local function launchNative(event,wantedA)
 if not dkLaunchInfo.requested or dkLaunchInfo.landing then return end
 keepLaunch({event=event,phase=dkLaunchInfo.phase,Main=updates,frame=frame,poll=polls,movement=dkMoves,
  pendingMain=pendingReturn~=nil,requestedA=wantedA,x=pos('Player_X_Position','Player_PageLoc'),
  y=r('Player_Y_Position'),state=r('Player_State'),vy=r('Player_Y_Speed'),
  SavedJoypadBits=r('SavedJoypadBits'),A_B_Buttons=r('A_B_Buttons'),
  PreviousA_B_Buttons=r('PreviousA_B_Buttons'),DkPrevious=r('DkPrevious')})
end
"""
    text=Base.once(text,marker,body+marker+"\n launchNative('DK-movement-entry',nil)")
    text=Base.once(text,'  if dkDecide then dkDecide()end',"  launchNative('completed-Main',nil)\n  if dkDecide then dkDecide()end")
    text=Base.once(text,' lastA=not not b.a;emu.setInput(b,0)'," launchNative('input-poll',not not b.a)\n lastA=not not b.a;emu.setInput(b,0)")
    text=Base.once(text,'actual_DkMovement_calls=dkMoves,',
        'jump_launch=dkLaunchInfo,jump_launch_trace=dkLaunchTrace,actual_DkMovement_calls=dkMoves,')
    Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text


def metadata(raw,key='donkey_kong'):
    q=Previous.metadata(raw,key)
    q.update(controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        native_negative_controller_SHA256=OLD_LUA_SHA,
        jump_admission='latch requested A until actual state1, negative native VY, upward displacement and all four input witnesses',
        all_floor_head_and_actual_roof_landing_guards_preserved=True,maximum_launch_trace_rows=32)
    return q
