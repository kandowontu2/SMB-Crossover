-- Decisions use fully returned Main state. Input polls only apply this cache.
local returnHooks,returnHookCount={},0
local lastGroundState=0
local probeTicks=0
local function clockMask(b)
 local n=0
 for k,v in pairs({right=1,left=2,down=4,up=8,start=16,select=32,b=64,a=128})do if b[k]then n=n+v end end
 return n
end
local function gapState(kind)
 local s=state()
 s.kind=kind;s.movement_returns=moveReturns;s.form=r('M3Form')
 s.vx=r('Player_X_Speed');s.vy=r('Player_Y_Speed')
 s.held=r('SavedJoypadBits');s.previous=r('M3Previous');s.requested=clockMask(clockInput)
 s.a_held=(s.previous&128)~=0;s.growth=r('M3Growth')
 return s
end
local function gapRecord(kind,extra)
 local x=pos('Player_X_Position','Player_PageLoc')
 if not first or r('WorldNumber')~=0 or r('LevelNumber')~=0 or x<1320 or x>1456 then return end
 local s=gapState(kind);gapEvents=gapEvents+1
 if extra then for k,v in pairs(extra)do s[k]=v end end
 if #gapFirst<32 then gapFirst[#gapFirst+1]=s
 else gapTail[#gapTail+1]=s;if #gapTail>64 then table.remove(gapTail,1)end end
end
hook('M3Movement',function()
 if not first then return end
 assert(not moveToken,'Previous real M3Movement must return')
 local s=emu.getState();local sp=s['cpu.sp']
 local pc=emu.read(0x100+((sp+1)&255),emu.memType.nesDebug)+256*emu.read(0x100+((sp+2)&255),emu.memType.nesDebug)+1
 local at=emu.convertAddress(pc)
 if pc<0x8000 then
  assert(pc==C.smc_return_pc,'Typed CPU-RAM FarCallCommon return')
  at={memType=-1,address=pc}
 end
 assert(at,'Mapped real movement return')
 moveEntries=moveEntries+1
 moveToken={pc=pc,sp=(sp+2)&255,kind=at.memType,offset=at.address,Main=updates}
 if not returnHooks[pc]then
  assert(returnHookCount<8,'Bounded movement-return PCs')
  returnHookCount=returnHookCount+1;returnHooks[pc]=true
  emu.addMemoryCallback(guard(function()
   local t=moveToken
   if not t or t.pc~=pc or emu.getState()['cpu.sp']~=t.sp then return end
   local a=pc<0x8000 and {memType=-1,address=pc}or emu.convertAddress(pc)
   if not a or a.memType~=t.kind then return end
   local exact=a.address==t.offset
   local aliases={[119]=true,[120]=true,[125]=true,[127]=true}
   local alias=a.memType==emu.memType.nesPrgRom and aliases[math.floor(a.address/8192)]and aliases[math.floor(t.offset/8192)]and a.address%8192==t.offset%8192
   assert(exact or alias,'Actual authenticated resident return mapping')
   moveReturns=moveReturns+1;moveToken=nil
   gapRecord('M3Movement_return',{caller_return_pc=pc,caller_return_sp=t.sp,caller_kind=t.kind,caller_offset=a.address})
  end),emu.callbackType.exec,pc)
 end
end)
hook('M3Injury',function()
 if first and r('M3Form')==1 and not injury then
  injury=gapState('actual_M3Injury_entry');injury.actor_slot=emu.getState()['cpu.x']
  injury.actor_id=r('Enemy_ID',injury.actor_slot)
 end
end)
clockDecide=function()
 if not menuDone or not(active()and identity())then clockInput={};return end
 local c=context();local form=r('M3Form')
 if form==1 then grew=true end
 if grew and form==0 then damaged=true end
 if damaged and form==0 and c.level==0 and c.x>=1440 and c.x<1600 and c.grounded then smallFar=smallFar or gapState('post_damage_far_bank')end
 local b=c.level==0 and controls(c)or{}
 -- Optional source coverage uses a real, approaching grounded Goomba.
 -- It never writes a power/health/actor/player field.
 if C.damage_probe and grew and not damaged and form==1 and c.level==0 and c.x>420 and c.x<1320 and c.grounded and r('M3Growth')==0 then
  local e=c.enemy()
  if e and e.id==6 and math.abs(e.y-c.y)<25 and math.abs(e.dx)<100 then
   probeTicks=probeTicks+1
   assert(probeTicks<=240,'Bounded natural injury encounter')
   b={right=e.dx>8,left=e.dx< -8,b=false,a=false}
  end
 end
 clockInput=b
 gapRecord('Main_return_decision')
 if c.level==0 and c.x>=1320 and c.x<=1456 and lastGroundState==0 and c.state~=0 and(r('M3Previous')&128)~=0 and #gapTakeoffs<8 then gapTakeoffs[#gapTakeoffs+1]=gapState('takeoff')end
 lastGroundState=c.state
end
