-- Read-only original-query evidence; no controller/state/ROM edits.
local frame=0
local f=assert(io.open(MAC_OBSERVE_OUT..'invalid-queries.csv','w'))
f:write('frame,cycle,caller,anchorX,anchorY,shiftedX,shiftedY,index,sampleY,row,tile,address\n')
local pending=nil;local returns={}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local rejected=0
if MAC_EXPECT_FIXED then
 for _,name in ipairs({'LmVisibleSideProbe','TnMacVisibleSideProbe'})do
  local n=name
  emu.addMemoryCallback(function()
   if r('SelectedCharacter')~=15 or r('GameEngineSubroutine')~=8 or emu.convertAddress(L[n]).address//8192~=B[n]then return end
   local s=emu.getState();local sy=(r('Player_Y_Position')+r('BlockBuffer_Y_Adder',s['cpu.y']))%256
   if sy<32 or sy>=240 then rejected=rejected+1 end
  end,emu.callbackType.exec,assert(L[n],n))
 end
end
emu.addMemoryCallback(function()
 if r('SelectedCharacter')~=15 or r('GameEngineSubroutine')~=8 then return end
 local s=emu.getState();local y=s['cpu.y'];local sy=(r('Player_Y_Position')+r('BlockBuffer_Y_Adder',y))%256
 if sy>=32 and sy<240 then return end
 assert(not MAC_EXPECT_FIXED,'Fixed Mac side query escaped the terrain domain')
 local sp=s['cpu.sp'];local ret=(emu.read(0x100+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+1)%65536
 pending={frame+1,s['cpu.cycleCount'],ret,r('LmOldX')+256*r('LmOldPage'),r('LmOldY'),r('Player_X_Position'),r('Player_Y_Position'),y,sy,sp=(sp+2)%256}
 if not returns[ret]then
  returns[ret]=true
  emu.addMemoryCallback(function()
   if not pending or emu.getState()['cpu.sp']~=pending.sp then return end
   local q=pending;pending=nil
   q[#q+1]=r('R2');q[#q+1]=r('R3');q[#q+1]=r('R6')+256*r('R7')+r('R2')
   f:write(table.concat(q,',')..'\n');f:flush()
  end,emu.callbackType.exec,ret)
 end
end,emu.callbackType.exec,L.BlockBufferColli_Side)
emu.addEventCallback(function()
 frame=frame+1
 if MAC_EXPECT_FIXED and frame==3200 then
  assert(rejected>0,'Recorded input prefix must exercise the repaired HUD boundary')
  assert(r('NumberofLives')==2,'No death during the bounded reproduction prefix')
  f:close();local q=assert(io.open(MAC_OBSERVE_OUT..'fixed-observer.json','w'))
  q:write('{"passed":true,"frames":3200,"invalid_native_queries":0,"rejected_unmapped_samples":'..rejected..',"read_only":true}');q:close();emu.stop(0)
 end
end,emu.eventType.endFrame)
