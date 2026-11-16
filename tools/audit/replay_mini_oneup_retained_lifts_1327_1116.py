"""Exact retained d20 pure lift inputs, current real M→L and all item gates.

The small input fragment is source-retained here. No old build/runtime is
called by this factory; the optional source checker authenticates its origin.
"""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_mini_oneup_1327_1116 as Previous
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,H,Current=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.H,Previous.Current
BASE_SHA='12274f44fbc40de6a2f336627133d26977e49194dc2bf102bb8abc28f7c4fe16'
RETAINED_SHA='d20ec6a9c7481b902a5b45033e1a2e4448df4555ba31d4e0981d1a371e920677'
LIFT_POLICY='''local mini_lift_left = {[608]=560,[736]=688,[912]=864}
local mini_lift_runs, camera_lift_spawns = {}, {}
local function mini_lift_inputs(s, obstacle, x)
 local left = obstacle and mini_lift_left[obstacle.left]
 if not left then return end
 local row = mini_lift_runs[left]
 if not row then
  row = {left=left,center=left+16,initial_top=192,width=32,stage='1-1',pipe=obstacle.left}
  mini_lift_runs[left] = row
  phases.fullstage.lifts = phases.fullstage.lifts or {}
  phases.fullstage.lifts[#phases.fullstage.lifts+1] = row
 end
 if row.departed then return end
 -- A faster game can put the lift above the first boarding jump. Return to
 -- its edge and release A, then retry with ordinary controller inputs.
 if not row.boarded and x>left+26 and x<obstacle.left then
  return {left=true,b=true}
 end
 local slot = -1
 for candidate=0,5 do
  if read(L.Enemy_Flag+candidate)==1 and read(L.Enemy_ID+candidate)==0x25
   and read(L.Enemy_X_Position+candidate)+256*read(L.Enemy_PageLoc+candidate)==left then
   slot=candidate;break
  end
 end
 local target = slot>=0 and slot<6 and read(L.Enemy_Flag+slot)==1 and read(L.Enemy_ID+slot)==0x25
  and read(L.Enemy_X_Position+slot)+256*read(L.Enemy_PageLoc+slot)==left
 local floor = supported(s)
 if target then
  local top = read(L.Enemy_Y_Position+slot)
  if not row.spawn_top then
   local spawn=camera_lift_spawns[left]
   check(spawn~=nil,'Camera lift has an observed native constructor')
   row.spawn_top=spawn.top;row.spawn_frame=spawn.frame;row.spawn_relative_x=spawn.relative_x;row.slot=slot
  end
  if ram(0xc30d)==slot+1 then
   if not row.boarded then
    row.boarded=true;row.board_frame=frame;row.board_top=top;row.board_x=x
   end
   row.minimum_top=math.min(row.minimum_top or top,top)
   if row.departure_press and s.queued==12 then return {right=true,b=true,a=true} end
   -- Release A and build a little speed on the platform before taking off.
   if floor and top<=obstacle.top+10 then
    if x<left+19 then return {right=true,b=true} end
    if s.held&128==0 then
     row.departure_press=true
     return {right=true,b=true,a=true}
    end
   end
   return {}
  end
  if row.departure_press then
   if s.queued==12 or s.current==12 or s.current==13 or s.vy<0 then
    row.departed=true;row.departure_frame=frame;row.departure_x=x;row.departure_top=top
    return {right=true,b=true,a=true}
   end
  end
  if x>=left-23 and x<=left+26 then
   -- Keep the initial press through the donor's queued jump entry, just as
   -- departure does; releasing during its windup can cancel boarding.
   if row.boarding_press and s.queued==12 then return {right=x<left+5,b=true,a=true} end
   if floor then
    if top>=166 and s.held&128==0 then row.boarding_press=true; return {right=true,b=true,a=true} end
    if top<166 then return {} end
    return {right=true,b=true}
   end
   return {right=x<left+5,b=true,a=true}
  end
 end
 if x>=left-12 and x<=left+29 and not row.boarded then return {} end
end
'''


@lru_cache(maxsize=1)
def bindings(raw):
    c=deepcopy(Previous.bindings(raw));b=Current.bindings(raw)['bundle']
    for n in('ScreenLeft_X_Pos','ScreenLeft_PageLoc'):c['ram'][n]=W.address(b,n)
    return c


@lru_cache(maxsize=1)
def controller(raw,key='oneup'):
    assert key=='oneup'and H(Path(Previous.__file__).read_bytes())==BASE_SHA
    _,body=Previous.controller(raw).split('\n',1);old=Previous.LIFT.read_text()
    assert body.count(old)==1;body=body.replace(old,'local function check(ok,why)assert(ok,why)end\n'+LIFT_POLICY,1)
    old='route.births[#route.births+1]=row\n'
    new="route.births[#route.births+1]=row;camera_lift_spawns[a.x]={top=a.y,frame=frame,relative_x=a.x-pos('ScreenLeft_X_Pos','ScreenLeft_PageLoc')}\n"
    assert body.count(old)==1;body=body.replace(old,new,1)
    body=Previous.once(body,'route=route,readback=readback','route=route,lift_inputs=phases.fullstage.lifts,readback=readback')
    text='local C='+Text.lua(bindings(raw))+'\n'+body;LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','takeScreenshot','loadState','saveState'));return text


def metadata(raw,key='oneup'):
    q=Previous.metadata(raw);q.update(factory_SHA256=H(Path(__file__).read_bytes()),controller_SHA256=H(controller(raw).encode()),parent_L_factory_SHA256=BASE_SHA,
        retained_full_input_reference_SHA256=RETAINED_SHA,retained_pure_lift_fragment_SHA256=H(LIFT_POLICY.encode()),old_build_runtime_calls=0,
        scope='Same current genuine M/hiddenL transaction gates, exact source-retained d20 pure lift retries/queued-A inputs with actual native constructor observer; no old runtime/build invocation')
    return q


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
