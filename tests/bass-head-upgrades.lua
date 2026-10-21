-- Initial powered-Bass/map fixtures, then real A presses. Test every upgrade
-- at four camera/page positions and differing head contacts/block heights.
local frame,age,phase=0,0,0
local cases={}
for item=1,8 do for world=1,4 do
 cases[#cases+1]={item=item,x=({112,240,256,368})[world],offset=({-7,0,7,0})[world],y=world%2==0 and 160 or 144}
end end
local c,slot,owned,heads=nil,nil,0,0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
emu.addMemoryCallback(function()
 if frame>=550 and c and r('CurrentBank')%128==59 then
  assert(r('MmBlockAttack')==0,'Upgrade is revealed by an actual player head bump')
  w('PseudoRandomBitReg',c.item==8 and 6 or c.item-1,1)
  heads=heads+1
 end
end,emu.callbackType.exec,L.InventoryPreparePickup)
emu.addMemoryCallback(function()
 if frame>=550 and r('CurrentBank')%128==59 then
  local s=emu.getState()['cpu.x']
  print('HEAD COLLECT case '..phase..' age '..age..' p '..r('Player_X_Position')..','..r('Player_Y_Position')..' item '..r('InvPickup',s)..' enemy '..r('Enemy_X_Position',s)..','..r('Enemy_Y_Position',s)..' state '..r('Enemy_State',s))
 end
end,emu.callbackType.exec,L.InventoryCollect)
local function setup()
 phase=phase+1;c=cases[phase];slot=nil;age=0
 if not c then
  assert(heads==32,'Every controller jump reached its native question block')
  print('PASS 32 Bass head-bumped upgrades: all eight icons, block edges, native heights and camera/page seams; no automatic collection');emu.stop(0);return
 end
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
 w('Block_Buffer_1',0xc1,math.floor(c.x/256)%2*208+c.y-32+math.floor(c.x%256/16))
 for i=0,5 do w('Enemy_Flag',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 for i=0,3 do w('Block_State',0,i);w('BlockMetasprite',0,i);w('MmBulletType',0,i)end
 for i=0,1 do w('Block_RepFlag',0,i)end
 w('BlockBounceTimer',0);w('SsFreeze',0);w('SsBodyStop',0);w('XgDash',0);w('XgJumpUsed',0)
 w('Player_X_Position',c.x+c.offset);w('Player_PageLoc',math.floor((c.x+c.offset)/256));w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',1)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 local left=math.max(0,c.x-112)
 w('ScreenLeft_X_Pos',left);w('ScreenLeft_PageLoc',math.floor(left/256));w('ScreenRight_X_Pos',left+255);w('ScreenRight_PageLoc',math.floor((left+255)/256))
 owned=c.item==8 and 3 or 1
 w('PlayerStatus',1);w('InvOwnedLo',owned,9);w('InvOwnedHi',0,9);w('InvViewedLo',0,9);w('InvViewedHi',0,9)
 w('InvStoredLo',0,9);w('InvStoredHi',0,9);w('InvSelected',0,9)
end
emu.addEventCallback(function()
 emu.setInput({down=frame==80,right=frame==100 or frame==120 or frame==140,start=frame==200,
  a=frame>=550 and age>=10 and age<30},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<550 then return end
 if frame==550 then setup();return end
 age=age+1
 for i=0,5 do if r('Enemy_Flag',i)~=0 and r('Enemy_ID',i)==0x2e then
  slot=i;assert(r('InvPickup',i)==c.item,'Head bump reveals its independent source icon')
 end end
 assert(r('InvOwnedLo',9)==owned and r('InvOwnedHi',9)==0,'Head bump cannot collect through the question block, case '..phase..' age '..age..' status '..r('PlayerStatus')..' owned '..r('InvOwnedLo',9)..'/'..r('InvOwnedHi',9)..' p '..r('Player_X_Position')..','..r('Player_Y_Position'))
 if age==140 then
  assert(slot and r('Enemy_Flag',slot)~=0 and r('Enemy_State',slot)==128,'Head-bumped item fully emerges and remains in the world, case '..phase)
  assert(r('Enemy_X_Position',slot)+256*r('Enemy_PageLoc',slot)==c.x,'Power-up stays on its head-bumped block across page seams')
  setup()
 end
end,emu.eventType.endFrame)
