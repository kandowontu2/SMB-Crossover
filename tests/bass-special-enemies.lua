-- Source passthrough-defeat properties, with real controller-created shots.
-- Health/flat-world setup is explicit; this is not a controller-only clear.
local frame,age,case=0,0,1
local items={2,3,4}
local defeated={}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function enemies()
 for i=0,1 do
  w('Enemy_Flag',1,i);w('Enemy_ID',6,i);w('Enemy_State',0,i)
  w('Enemy_BoundBoxCtrl',9,i);w('Enemy_X_Position',92+40*i,i)
  w('Enemy_PageLoc',0,i);w('Enemy_Y_Position',176,i);w('Enemy_Y_HighPos',1,i)
  w('Enemy_X_Speed',0,i);w('Enemy_Y_Speed',0,i)
  w('MmEnemyHealthLo',case==1 and i==0 and 25 or 0,i);w('MmEnemyHealthHi',0,i)
 end
end
local function setup()
 for i=0,5 do w('Enemy_Flag',0,i);w('MmEnemyHealthLo',0,i);w('MmEnemyHealthHi',0,i)end
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+176+col)end end
 for i=0,9 do w('RgShotType',0,i);w('RgShotHits',0,i);w('SsMode',0,i)end
 for i=0,3 do w('MmBulletType',0,i)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 w('Player_X_Position',32);w('Player_PageLoc',0);w('Player_Y_Position',176)
 w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',1)
 w('PlayerStatus',1);w('InvOwnedLo',255,9);w('InvOwnedHi',1,9)
 w('InvSelected',items[case],9);w('InvAmmo',112,144+items[case]);w('InvDirty',1)
 w('SsHeld',0);w('SsFreeze',0);w('SsBodyStop',0);w('RgShootPose',0);w('RgCooldown',0)
 if case~=3 then enemies()end
 age=0
 defeated={}
end
emu.addEventCallback(function()
 emu.setInput({down=frame==80,right=frame==100 or frame==120 or frame==140,start=frame==200,
  b=frame>=550 and age>=10 and age<(case==3 and 80 or 16)},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<550 then return end
 if frame==550 then setup();return end
 age=age+1
 for i=0,1 do if r('Enemy_State',i)&0x20~=0 then defeated[i]=true end end
 if case==3 and age==80 then enemies()end
 if age==130 then
  assert(defeated[0],'Special weapon defeats the first Goomba in case '..case..' health '..r('MmEnemyHealthLo')..'/'..r('MmEnemyHealthLo',1))
  if case==1 then
   assert(r('MmEnemyHealthLo',1)==25 and not defeated[1],'Metal Blade passes through a defeat then consumes itself on a surviving enemy: '..r('MmEnemyHealthLo',1))
  else assert(defeated[1],'Knuckle/full Pharaoh continues through both defeated enemies')end
  case=case+1
  if case==4 then
   print('PASS Bass Metal Blade passthrough on defeat/consume on survival, Hard Knuckle piercing and full Pharaoh passthrough')
   emu.stop(0)
  else setup()end
 end
end,emu.eventType.endFrame)
