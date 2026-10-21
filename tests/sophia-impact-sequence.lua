-- Explicit arenas, actual B/Select shots. Verify source impact lifetime,
-- no repeated hit tests during an effect, and distinct source sound requests.
local frame=0
local cases={'cannon-wall','missile-wall','enemy-hit','enemy-kill'}
local slot,origin
local seen,sounds={},{}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end

local function phase()return math.floor((frame-550)/160),(frame-550)%160 end
local function fixture(n)
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+176+col)end end
 for i=0,5 do w('Enemy_Flag',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 w('Player_X_Position',64);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',1)
 w('PlayerStatus',1);w('InvOwnedLo',3,11);w('InvSelected',1,11);w('InvAmmo',60,177);w('InvPrevious',0);w('RgPreviousButtons',0);w('RgCooldown',0)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 if n<2 then
  for row=8,10 do w('Block_Buffer_1',0x54,row*16+7)end
 else
  w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_X_Position',112);w('Enemy_PageLoc',0);w('Enemy_Y_Position',176);w('Enemy_Y_HighPos',1)
  w('Enemy_BoundBoxCtrl',9);w('EnemyOffscrBitsMasked',0);w('MmEnemyHealthLo',n==3 and 1 or 232);w('MmEnemyHealthHi',n==3 and 0 or 3)
 end
 w('AvStopwatch',255);slot=nil;origin=nil;seen={};sounds={}
end
emu.addMemoryCallback(function(_,value)
 local n,t=phase()
 if n>=0 and n<#cases and t>0 and value>=18 and value<=20 then sounds[value]=true end
end,emu.callbackType.write,assert(L.AvAudioRequest))
for _,pc in ipairs({assert(L.Blocks),assert(L.Enemies)})do
 emu.addMemoryCallback(function()
  local n,t=phase();if n<0 or n>=#cases or r('CurrentBank')%128~=8 then return end
  assert(r('RgShotImpact',r('RgSlot'))==0,'Source explosion does not repeat terrain/enemy hit tests')
 end,emu.callbackType.exec,pc)
end
emu.addEventCallback(function()
 local n,t=phase()
 emu.setInput({start=frame==240,down=frame==80,right=frame>=100 and frame<200 and(frame-100)%20==0,b=n>=0 and n<#cases and n~=1 and t>=12 and t<16,select=n==1 and t>=12 and t<16},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1;if frame<550 then return end
 local n,t=phase()
 if n==#cases then print('PASS actual Sophia cannon/missile impacts: ten-update source animation, frozen origin, no repeated collisions, source explode/hit/kill sounds');emu.stop(0);return end
 if t==0 then fixture(n)end
 w('AvStopwatch',255)
 if not slot then for i=0,9 do if r('RgShotImpact',i)>0 and r('RgShotImpact',i)<128 then slot=i;break end end end
 if slot and r('RgShotImpact',slot)>0 then
  local impact=r('RgShotImpact',slot);seen[impact]=true
  local xy=r('RgShotX',slot)+256*r('RgShotPage',slot)+65536*(r('RgShotY',slot)+256*r('RgShotYHigh',slot))
  if not origin then origin=xy end
  assert(xy==origin,'Impact stays at source projectile position')
 end
 if t==145 then
  assert(slot,'Actual shot produces source impact in '..cases[n+1])
  for i=1,10 do assert(seen[i],'Full source explosion lifetime '..i..' in '..cases[n+1])end
  assert(r('RgShotType',slot)==0,'Effect expires after source animation')
  assert(sounds[n<2 and 18 or n==2 and 19 or 20],'Source-specific impact/hit/kill SFX request in '..cases[n+1])
 end
end,emu.eventType.endFrame)
