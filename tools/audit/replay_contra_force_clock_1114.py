"""Separate CF bare idle/walk clock: real Main and worker return acknowledgements."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

import replay_contra_force_full11_v2_1114 as Previous

PIN,ROM,R,W,N=Previous.PIN,Previous.ROM,Previous.R,Previous.W,Previous.N
Frozen,POLICY,IDENTITIES=Previous.Frozen,Previous.POLICY,Previous.IDENTITIES
normalize,bindings=Previous.normalize,Previous.bindings
PREVIOUS_SOURCE='8330845efee9e4a7eb800e457f3c3c55a28590159d274b6d7d49b699500a08c4'
LUA_SHA={'burns':'3cd35204a49659efb1a6343e57e782a5427d358b55127718ee8cd78f396e728a',
    'smith':'e392d01822b80722683c3645534d9d27699eac41c21ff83383e37e1c5eb2a793',
    'iron':'64a00b964c81830759eeb79988d5913c19864742a6e0173724fd19743bbcaad0',
    'beans':'bd8ef108637197e4caf8a230015c8b16101c16882c7a1158f16a680523ddc20f'}

TEMPLATE=r'''
local frame,polls,mainEntries,mainReturns,workerEntries,workerReturns=0,0,0,0,0,0
local menuDone=CPU_CONTROLLER_OPENING or false
local buttons,finished={},false
local first,pendingMain,pendingWorker
local phaseIndex,phaseAge=0,0
local phases,returnHooks,workerCallers={}, {}, {}
local phaseDefs={{name='idle',frames=120},{name='right',frames=32},{name='left',frames=32}}
local began,cookieChecks,emptyChecks
cookieChecks,emptyChecks=0,0
local function r(n,i)return emu.read(assert(C.ram[n],n)+(i or 0),emu.memType.nesDebug)end
local function source(at)return emu.read(2*8192+at,emu.memType.nesWorkRam)end
local function pos(lo,hi)return r(lo)+256*r(hi)end
local function active()return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 end
local function identity()return r('SelectedCharacter')==31 and((r('FmGroups')>>3)&3)==C.variant and r('CrossoverBehaviorVersion')==0 and r('CheatInvincible')==0 and r('CheatStartLevel')==0 end
local function state()return{frame=frame,polls=polls,Main_entries=mainEntries,Main_returns=mainReturns,CF_entries=workerEntries,CF_returns=workerReturns,x=pos('Player_X_Position','Player_PageLoc'),y=r('Player_Y_Position'),native_state=r('Player_State'),lives=r('NumberofLives'),power=r('PlayerStatus'),star=r('StarInvincibleTimer'),source_contact=source(0x4d2),source_input=source(0x4aa),source_jump_age=source(0x4b4)}end
local function json(v)
 if v==nil then return'null'elseif type(v)=='string'then return string.format('%q',v)elseif type(v)~='table'then return tostring(v)end
 local a={};if#v>0 then for i,x in ipairs(v)do a[i]=json(x)end;return'['..table.concat(a,',')..']'end
 for k,x in pairs(v)do a[#a+1]=json(k)..':'..json(x)end;table.sort(a);return'{'..table.concat(a,',')..'}'
end
local function finish(reason)
 if finished then return end;finished=true
 local ok=reason=='bare-idle120-right32-left32'and#phases==3 and not pendingMain and not pendingWorker and identity()and r('NumberofLives')==2
 print('SMB_NATIVE_RECEIPT '..json({passed=not not ok,kind='CF-bare-clock',reason=reason,ROM_SHA256=C.sha,identity=C.key,variant=C.variant,physical_frames=frame,input_polls=polls,Main_entries=mainEntries,Main_returned=mainReturns,CF_movement_entries=workerEntries,CF_movement_returns=workerReturns,complete_cookie_checks=cookieChecks,zero_actor_shot_checks=emptyChecks,actual_worker_return_callers=workerCallers,phases=phases,terminal=state(),B_A_inputs_during_measurement=false,game_state_writes=false,outputs=0}))
 emu.stop(ok and 0 or 1)
end
local function guard(fn)return function(...)if finished then return end;local ok,why=pcall(fn,...);if not ok then finish('callback-error:'..tostring(why))end end end
local function hook(h,kind,fn)
 emu.addMemoryCallback(guard(function()
  local a=emu.convertAddress(h.pc)
  if not a or a.memType~=kind or a.address~=(h.offset or h.raw)then return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==v,'Exact compiled clock hook')end
  fn()
 end),emu.callbackType.exec,h.pc)
end
hook(C.hooks.GameLoop,emu.memType.nesPrgRom,function()
 assert(not pendingMain,'Previous full Main must return')
 local sp=emu.getState()['cpu.sp']
 local pc=emu.read(0x100+((sp+1)&255),emu.memType.nesDebug)+256*emu.read(0x100+((sp+2)&255),emu.memType.nesDebug)+1
 assert(pc==C.hooks.GameLoopReturn0.pc or pc==C.hooks.GameLoopReturn1.pc,'Actual full Main caller')
 mainEntries=mainEntries+1;pendingMain={pc=pc,sp=(sp+2)&255}
end)
for i=0,1 do local h=C.hooks['GameLoopReturn'..i];hook(h,emu.memType.nesPrgRom,function()
 assert(pendingMain and pendingMain.pc==h.pc and pendingMain.sp==emu.getState()['cpu.sp'],'Actual full Main return PC/SP')
 assert(not pendingWorker,'Original CF movement must return before full Main')
 pendingMain=nil;mainReturns=mainReturns+1
end)end
hook(C.cf.hooks.CfHostMovement,emu.memType.nesWorkRam,function()
 if not first then return end
 assert(not pendingWorker,'Prior original CF movement must return')
 local sp=emu.getState()['cpu.sp']
 local pc=emu.read(0x100+((sp+1)&255),emu.memType.nesDebug)+256*emu.read(0x100+((sp+2)&255),emu.memType.nesDebug)+1
 local a=emu.convertAddress(pc)
 workerEntries=workerEntries+1;pendingWorker={pc=pc,sp=(sp+2)&255,kind=a and a.memType,address=a and a.address}
 if not returnHooks[pc]then
  returnHooks[pc]=true
  assert(#workerCallers<4,'Bounded actual original CF callers')
  workerCallers[#workerCallers+1]={pc=pc,return_SP=(sp+2)&255,kind=a and a.memType,address=a and a.address}
  emu.addMemoryCallback(guard(function()
   local p=pendingWorker
   if not p or p.pc~=pc or p.sp~=emu.getState()['cpu.sp']then return end
   local z=emu.convertAddress(pc)
   assert((not p.kind and not z)or(z and z.memType==p.kind and z.address==p.address),'Actual original CF return mapping')
   pendingWorker=nil;workerReturns=workerReturns+1
  end),emu.callbackType.exec,pc)
 end
end)
local function empty()
 for i=0,5 do assert(r('Enemy_Flag',i)==0,'Bare clock requires naturally zero native actors')end
 for i=10,21 do assert(source(0x382+i)==0,'Bare clock requires naturally zero source shot slots')end
 emptyChecks=emptyChecks+1
end
local function cookie()
 for i,v in ipairs(C.cf.cookie)do assert(emu.read(2*8192+0x1fe0+i-1,emu.memType.nesWorkRam)==v,'Actual complete CF C2 cookie')end
 for i=0,31 do assert(emu.read(3*8192+0x1fe0+i,emu.memType.nesWorkRam)==0,'Actual zero C3 tail')end
 assert(source(0x2e0)==C.variant,'Actual original CF class')
 cookieChecks=cookieChecks+1
end
local function clockFrame()
 if not first then return end
 assert(identity()and r('NumberofLives')==2 and r('PlayerStatus')==0 and r('StarInvincibleTimer')==0 and active(),'Bare clock retains living initial1-1')
 cookie();empty()
 if phaseIndex==0 then
  if workerReturns>0 and not pendingMain and not pendingWorker and r('Player_State')==0 and source(0x4d2)==1 then
   phaseIndex=1;phaseAge=0;began=state()
  end
  return
 end
 phaseAge=phaseAge+1
 local def=phaseDefs[phaseIndex]
 if phaseAge>=def.frames and not pendingMain and not pendingWorker then
  local ended=state();phases[#phases+1]={phase=def.name,requested_physical_frames=def.frames,physical_frames=ended.frame-began.frame,input_polls=ended.polls-began.polls,Main_entries=ended.Main_entries-began.Main_entries,Main_returns=ended.Main_returns-began.Main_returns,CF_movement_entries=ended.CF_entries-began.CF_entries,CF_movement_returns=ended.CF_returns-began.CF_returns,start=began,finish=ended}
  phaseIndex=phaseIndex+1;phaseAge=0;began=ended
  if phaseIndex==4 then finish('bare-idle120-right32-left32')end
 end
end
local function wait(n)coroutine.yield(n)end
local function press(key)buttons={[key]=true};wait(2);buttons={};wait(8)end
local function ready(fn,limit,name)local began=frame;while not fn()and frame-began<limit do wait(1)end;assert(fn(),'Actual frontend '..name)end
local menu=coroutine.create(function()
 assert(os.getenv('SMB_STDOUT_ROM_SHA')==C.sha,'Exact421 clock ROM pin')
 ready(function()return frame>=70 and r('CrossoverTitleDrawn')==1 and r('DisableScreenFlag')==0 end,250,'title')
 press('start');ready(function()return r('CrossoverMenuState')==2 and r('DisableScreenFlag')==0 end,180,'roster')
 assert(r('CrossoverMenuIndex')==0,'Genuine initial portrait')
 for i=1,3 do press('down')end;for i=1,6 do press('right')end
 assert(r('CrossoverMenuIndex')==30 and r('SelectedCharacter')==31,'Actual compiled CF slot30')
 for i=1,C.cycle do press('select')end;assert(identity(),'Actual CF choice/no cheats')
 press('start');menuDone=true
end)
local age=0
emu.addEventCallback(guard(function()
 polls=polls+1;local b=buttons
 if menuDone then
  b={};if phaseIndex==2 then b.right=true elseif phaseIndex==3 then b.left=true end
  assert(not b.a and not b.b,'Bare clock never presses B or A')
 end
 emu.setInput(b,0)
end),emu.eventType.inputPolled)
emu.addEventCallback(guard(function()
 frame=frame+1
 if not menuDone then if age>0 then age=age-1;return end;local ok,n=coroutine.resume(menu);assert(ok,n);age=n or 0;return end
 if not first and active()then assert(identity()and r('WorldNumber')==0 and r('LevelNumber')==0 and r('AreaType')==1,'Actual initial1-1');first=state()end
 clockFrame()
 if frame>=3000 then finish('bounded-clock-timeout')end
end),emu.eventType.endFrame)
'''


@lru_cache(maxsize=4)
def controller(raw,key='burns'):
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==PREVIOUS_SOURCE
    config=bindings(raw,key)
    text='local C='+Frozen.lua(config)+'\n'+TEMPLATE
    Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    assert sha256(text.encode()).hexdigest()==LUA_SHA[key]
    return text


def metadata(raw,key='burns'):
    q=Previous.metadata(raw,key)
    q.update(controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        scope='Separate requested physical idle120/right32/left32, finishing each full Main before phase boundary',
        actual_CF_worker_return_PC_SP_mapping_acknowledgements=True,
        naturally_zero_native_actors_and_source_shots_required=True,
        no_B_A_during_measurement=True,no_lag_or_optimization_result_presumed=True,
        previous_gameplay_controls_identical=False,
        full_nonshortcut1_1_then25living_grounded1_2_required=False)
    return q
