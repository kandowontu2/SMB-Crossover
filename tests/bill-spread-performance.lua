-- Explicit performance fixture, not a controller-only level-clear replay.
-- Give Bill spread + invincibility; otherwise use native enemies and gameplay.
local frame,lag=0,0
local entry,entrySp,returnPc
local log=assert(io.open(OUTPUT..ROM_NAME..'-bill-spread-performance.csv','w'))
log:write('frame,cycles,shots,spawned,blocks,enemies,blockCycles,enemyCycles\n')
local blocks,enemies,spawned,blockCycles,enemyCycles=0,0,0,0,0
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function cycles() return emu.getState()['cpu.cycleCount'] end
emu.addMemoryCallback(function()
 if frame>=550 and r('NmiDisable')>=128 then lag=lag+1 end
end,emu.callbackType.exec,L.NonMaskableInterrupt)
emu.addMemoryCallback(function()
 if frame<550 or r('CurrentBank')%128~=8 then return end
 entry=cycles();entrySp=emu.getState()['cpu.sp'];blocks=0;enemies=0;spawned=0;blockCycles=0;enemyCycles=0
 local pc=emu.read(0x100+(entrySp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(entrySp+2)%256,emu.memType.nesDebug)+1
 if not returnPc then
  returnPc=pc
  emu.addMemoryCallback(function()
   if not entry or r('CurrentBank')%128~=8 or emu.getState()['cpu.sp']~=entrySp+2 then return end
   local count=0
   for i=0,9 do if r('RgShotType',i)>0 then count=count+1 end end
   log:write(table.concat({frame,cycles()-entry,count,spawned,blocks,enemies,blockCycles,enemyCycles},',')..'\n');entry=nil
  end,emu.callbackType.exec,returnPc)
 end
 assert(pc==returnPc,'RosterWeapons caller remains stable')
end,emu.callbackType.exec,L.RosterWeapons)
-- Debug labels are scoped; resolve these addresses from the assembled listing
-- through the optional PERF_LABELS supplied by the driver.
PERF_LABELS=PERF_LABELS or L
if PERF_LABELS then
 for name,key in pairs({Blocks='blocks',Enemies='enemies',SpawnBill='spawned'}) do
  local started,sp
  local hooked={}
  emu.addMemoryCallback(function()
   if not entry or r('CurrentBank')%128~=8 then return end
   if key=='blocks' then blocks=blocks+1 elseif key=='enemies' then enemies=enemies+1 else spawned=spawned+1 end
   if key=='spawned' then return end
   started=cycles();sp=emu.getState()['cpu.sp']
   local pc=emu.read(0x100+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+1
   if not hooked[pc] then
    hooked[pc]=true
    emu.addMemoryCallback(function()
     if not started or not entry or r('CurrentBank')%128~=8 or emu.getState()['cpu.sp']~=sp+2 then return end
     if key=='blocks' then blockCycles=blockCycles+cycles()-started else enemyCycles=enemyCycles+cycles()-started end
     started=nil
    end,emu.callbackType.exec,pc)
   end
  end,emu.callbackType.exec,PERF_LABELS[name])
 end
end
emu.addEventCallback(function()
 emu.setInput({right=(frame>=80 and frame<140 and (frame-80)%20==0) or (frame>=550 and frame<950),
 start=frame==200,a=frame>=600 and frame%100<35,b=frame>=550 and frame%20<10},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==540 then
  emu.write(L.PlayerStatus,2,emu.memType.nesDebug)
  emu.write(L.StarInvincibleTimer,255,emu.memType.nesDebug)
 end
 if frame==1200 then
  log:close();print('PASS Bill spread performance: '..lag..' lag frames');emu.stop(0)
 end
end,emu.eventType.endFrame)
