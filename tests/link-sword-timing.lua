-- Link.checkState enables the sword during attackStart; atkTmrLsr switches
-- to attack-2 after 150ms. A new target arriving after that must be safe.
local frame=0
local ages={}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug)end
-- GUEST and music share CPU addresses. Observe the actual PRG bank, then
-- check the linked entry bytes before treating an execution as MeleeBridge.
local selector,prgBank=0,-1
emu.addMemoryCallback(function(_,v)selector=v&7 end,emu.callbackType.write,0x8000)
emu.addMemoryCallback(function(_,v)if selector==7 then prgBank=v&63 end end,emu.callbackType.write,0x8001)
emu.addMemoryCallback(function(_,v)prgBank=v&127 end,emu.callbackType.write,0x5115)
local entry={0xa5,L.Player_X_Position,0x18,0x69,8,0x8d,L.MmBulletX&255,L.MmBulletX>>8}
local function enemy(slot)
 w('Enemy_Flag',1,slot);w('Enemy_ID',6,slot);w('Enemy_State',0,slot);w('Enemy_BoundBoxCtrl',9,slot)
 w('Enemy_PageLoc',0,slot);w('Enemy_X_Position',68,slot);w('Enemy_Y_Position',168,slot);w('Enemy_Y_HighPos',1,slot)
 w('Enemy_X_Speed',0,slot);w('MmEnemyHealthLo',100,slot);w('MmEnemyHealthHi',0,slot)
end
emu.addEventCallback(function()
 emu.setInput({right=frame>=80 and frame<160 and (frame-80)%20==0,start=frame==200,b=frame==560},0)
end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()
 if prgBank~=8 then return end
 for i,v in ipairs(entry)do assert(emu.read(L.MeleeBridge+i-1,emu.memType.nesDebug)==v,'Actual GUEST MeleeBridge entry')end
 if frame>=560 and frame<=580 and r('RgThrust')==0 then
  local age=r('RgAttackAge');assert(age<9,'The initial sword pose carries the hit rectangle')
  ages[age]=(ages[age] or 0)+1
 end
end,emu.callbackType.exec,L.MeleeBridge)
emu.addEventCallback(function()
 frame=frame+1
 if frame==550 then
  for i=0,5 do w('Enemy_Flag',0,i) end
  w('Player_X_Position',40);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_State',0);w('PlayerFacingDir',1);w('PlayerStatus',0)
  enemy(0)
 end
 if frame>=550 and frame<580 then
  for slot=0,1 do w('Enemy_X_Position',68,slot);w('Enemy_Y_Position',168,slot);w('Enemy_X_Speed',0,slot) end
 end
 if frame==562 then assert(r('MmEnemyHealthLo')==50,'The first sword frame hits immediately') end
 if frame==570 then enemy(1) end
 if frame==582 then
  for age=0,8 do assert(ages[age]==1,'Each active source update is sampled once, age '..age) end
  assert(r('MmEnemyHealthLo')==50,'Continuous contact damages once per attack')
  assert(r('MmEnemyHealthLo',1)==100,'Retraction poses cannot damage a new target')
  print('PASS Link sword source hit window: immediate attackStart, nine active updates, no retraction damage');emu.stop(0)
 end
end,emu.eventType.endFrame)
