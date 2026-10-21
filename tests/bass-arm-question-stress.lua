-- Explicit map/actor fixtures. Real B presses lift and throw every brick.
-- Vary direction, world-page parity, question reward and interrupt phase.
local frame,age,trial=0,0,0
local startTick,questionCell,neighborCell
local used,reward,fragments=false,false,0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function setup()
 for i=0,5 do w('Enemy_Flag',0,i)end
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i);w('MmBrickHealth',0,i)end
 for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
 for i=0,9 do w('RgShotType',0,i);w('SsMode',0,i)end
 for i=0,3 do w('MmBulletType',0,i);w('Block_State',0,i);w('BlockMetasprite',0,i)end
 for i=0,1 do w('Block_RepFlag',0,i)end
 local left=trial%2==1;local page=math.floor(trial/2)%2
 local base=page*208;local col=left and 9 or 4
 questionCell=base+112+col;neighborCell=questionCell+(left and -1 or 1)
 w('Block_Buffer_1',0x51,base+160+(left and 10 or 3))
 w('Block_Buffer_1',math.floor(trial/4)%2==0 and 0xc1 or 0xc0,questionCell)
 w('Block_Buffer_1',0x51,neighborCell)
 w('BlockBounceTimer',0);w('InjuryTimer',255);w('StarInvincibleTimer',0)
 w('Player_X_Position',left and 176 or 32);w('Player_PageLoc',page)
 w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0)
 w('PlayerFacingDir',left and 2 or 1);w('Player_X_Speed',0);w('Player_Y_Speed',0)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',page);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',page)
 w('PlayerStatus',1);w('InvOwnedLo',255,9);w('InvOwnedHi',1,9)
 w('InvSelected',1,9);w('InvAmmo',112,145);w('InvDirty',1)
 w('SsHeld',0);w('SsFreeze',0);w('SsBodyStop',0);w('RgCooldown',0);w('RgShootPose',0)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 -- A Koopa adds enemy/OAM work during the throw. Invulnerability keeps
 -- this rendering fixture separate from player-damage verification.
 w('Enemy_Flag',1,4);w('Enemy_ID',0,4);w('Enemy_State',0,4)
 w('Enemy_X_Position',left and 112 or 96,4);w('Enemy_PageLoc',page,4)
 w('Enemy_Y_Position',176,4);w('Enemy_Y_HighPos',1,4);w('Enemy_BoundBoxCtrl',3,4)
 used=false;reward=false;fragments=0;startTick=r('FrameCounter');age=0
end
emu.addEventCallback(function()
 emu.setInput({down=frame==80,right=frame==100 or frame==120 or frame==140,start=frame==200,
  b=frame>=550 and ((age>=10 and age<16)or(age>=40 and age<46))},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<550 then return end
 if frame==550 then setup();return end
 age=age+1
 if age==30 then assert(r('SsHeld')>0,'Super Arm lifted masonry, trial '..trial)end
 if age>=40 then
  if r('Block_Buffer_1',questionCell)==0xc4 then used=true end
  local n=0;for i=0,9 do if r('RgShotType',i)==21 then n=n+1 end end
  fragments=math.max(fragments,n)
  for i=0,5 do if r('Enemy_Flag',i)>0 and r('Enemy_ID',i)==0x2e then reward=true end end
 end
 if age==180+trial%7 then
  assert(r('GameEngineSubroutine')==8 and (r('FrameCounter')-startTick)%256>=100,
   'Thrown brick keeps the main loop alive, trial '..trial)
  assert(used,'Question block becomes its used cell, trial '..trial)
  if math.floor(trial/4)%2==0 then assert(reward,'Native upgrade emerges, trial '..trial)end
  assert(fragments==4,'Thrown brick makes four fragments, trial '..trial)
  assert(r('Block_Buffer_1',neighborCell)==0x51,'Adjacent brick is preserved, trial '..trial)
  trial=trial+1
  if trial==16 then
   print('PASS 16 Bass Super Arm question-block throws: both directions/pages, coin and upgrade rewards, adjacent masonry, nearby Koopa, four fragments and live main loop')
   emu.stop(0)
  else setup()end
 end
end,emu.eventType.endFrame)
