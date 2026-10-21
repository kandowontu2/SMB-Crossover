-- Real attacks against native armored enemies. No HP or projectile state
-- is injected: ordinary shots reflect, while Knuckle's source pierce=10
-- overcomes Beetle/Bullet Bill armor=5.
local frame,age,phase=0,0,1
local reflected,defeated,deflectSound=false,false,false
local cases={{weapon=0,enemy=2},{weapon=2,enemy=2},{weapon=4,enemy=2},
 {weapon=3,enemy=2},{weapon=0,enemy=8},{weapon=3,enemy=8}}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function setup()
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
 for i=0,5 do w('Enemy_Flag',0,i);w('MmEnemyHealthLo',0,i);w('MmEnemyHealthHi',0,i);w('RgEnemyStun',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 w('Player_X_Position',64);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',1)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('PlayerStatus',1);w('InvOwnedLo',255,9);w('InvSelected',cases[phase].weapon,9);w('InvDirty',1)
 for i=1,7 do w('InvAmmo',112,144+i)end
 w('RgCooldown',0);w('SsBodyStop',0);w('SsFreeze',0);w('XgDash',0)
 w('Enemy_Flag',1);w('Enemy_ID',cases[phase].enemy);w('Enemy_State',0);w('Enemy_BoundBoxCtrl',9)
 w('Enemy_X_Position',136);w('Enemy_PageLoc',0);w('Enemy_Y_Position',176);w('Enemy_Y_HighPos',1);w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0)
 age=0;reflected=false;defeated=false;deflectSound=false
end
emu.addEventCallback(function()
 emu.setInput({down=frame==80,right=frame==100 or frame==120 or frame==140,start=frame==200,b=frame>=550 and age>=10 and age<14},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<550 then return end
 if frame==550 then setup();return end
 age=age+1
 if r('BassAudioRequest')==25 then deflectSound=true end
 if r('Enemy_Flag')==0 or r('Enemy_State')&32~=0 then defeated=true end
 for i=0,9 do
  if r('RgShotType',i)~=0 and r('RgShotImpact',i)&128~=0 then
   if not reflected then
    assert(r('RgShotVXHi',i)>=128,'An ordinary shot reverses horizontal velocity on armor')
    assert(r('RgShotVYHi',i)==0xfd and r('RgShotVYLo',i)==0x15,'Armor deflection uses source -350/120 vertical speed')
   end
   reflected=true
  end
 end
 if age==120 then
  if cases[phase].weapon==3 then
   assert(defeated and not reflected,'Knuckle pierces the native armored enemy')
  else
   assert(reflected and deflectSound and not defeated,'Normal weapon visibly deflects with its source cue, preserving armor: case '..phase)
   for i=0,9 do assert(r('RgShotType',i)==0,'Reflected/upward shots leave the live projectile pool')end
  end
  phase=phase+1
  if phase>#cases then print('PASS Bass buster/Metal/Pharaoh armor reflection, source deflection sound, upward cleanup and Knuckle armor piercing');emu.stop(0)
  else setup()end
 end
end,emu.eventType.endFrame)
