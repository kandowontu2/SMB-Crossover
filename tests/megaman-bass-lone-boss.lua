-- Explicit arenas isolate the zero-enemy shortcut. Native B input must hit a
-- lone Bowser or cannon Bullet Bill; no auxiliary Goomba makes the precheck pass.
local frame,age,case=0,0,1
local cases={{c=1,id=0x2d,w=2},{c=1,id=0x2d,w=3},{c=1,id=0x33,w=3},
 {c=9,id=0x2d,w=2},{c=9,id=0x2d,w=3},{c=9,id=0x33,w=3}}
local hit=false
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function setup()
 local s=cases[case]
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
 for i=0,5 do w('Enemy_Flag',0,i);w('Enemy_State',0,i);w('MmEnemyHealthLo',0,i);w('MmEnemyHealthHi',0,i);w('RgEnemyStun',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 for i=0,3 do w('MmBulletType',0,i)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 w('SelectedCharacter',s.c);w('Player_X_Position',32);w('Player_PageLoc',0)
 w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',1)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('PlayerStatus',1);w('InvOwnedLo',255,s.c);w('InvOwnedHi',7,s.c)
 w('InvSelected',s.w,s.c);w('InvAmmo',112,s.c*16+s.w);w('InvDirty',1)
 w('RgCooldown',0);w('SsBodyStop',0);w('SsFreeze',0);w('MmSliding',0);w('XgDash',0)
 w('Enemy_Flag',1);w('Enemy_ID',s.id);w('Enemy_State',0);w('Enemy_BoundBoxCtrl',9)
 w('Enemy_X_Position',128);w('Enemy_PageLoc',0);w('Enemy_Y_Position',176)
 w('Enemy_Y_HighPos',1);w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0)
 w('TimerControl',0);w('GameEngineSubroutine',8);w('WorldNumber',0)
 age=0;hit=false
end
emu.addMemoryCallback(function()
 if frame>=550 and r('CurrentBank')%128==7 then hit=true end
end,emu.callbackType.exec,L.MegaManWeapons_DamageEnemy or L.DamageEnemy)
emu.addEventCallback(function()
 emu.setInput({right=frame==80,start=frame==200,b=frame>=550 and age>=10 and age<15},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<550 then return end
 if frame==550 then setup();return end
 age=age+1
 local hp=r('MmEnemyHealthLo')+256*r('MmEnemyHealthHi')
 if hp>0 or r('Enemy_State')&32~=0 then hit=true end
 if r('Enemy_Flag')~=0 and r('Enemy_State')&32==0 then
  w('Enemy_X_Position',128);w('Enemy_PageLoc',0);w('Enemy_Y_Position',176)
  w('Enemy_Y_HighPos',1);w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0)
 end
 if age==140 then
  local s=cases[case]
  assert(hit,'Special weapon reaches lone enemy '..s.c..'/'..s.id..'/'..s.w)
  if s.id==0x2d then assert(hp>0 and hp<600,'Controller shot damages lone Bowser, hp='..hp)
  else assert(r('Enemy_Flag')==0 or r('Enemy_State')&32~=0,'Knuckle pierces lone cannon Bullet Bill')end
  case=case+1
  if case>#cases then print('PASS MM/Bass Metal/Knuckle damage lone Bowser and Knuckle defeats lone cannon Bullet Bill');emu.stop(0)
  else setup()end
 end
end,emu.eventType.endFrame)
