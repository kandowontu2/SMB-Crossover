-- Read-only 2.02 source gives Hard Knuckle pierce strength 10 in the common
-- MegaManProjectile class. These explicit arena/inventory/enemy fixtures use
-- real controller-created shots, never injected projectile or HP outcomes.
local frame,age,case=0,0,1
local cases={{weapon=2,enemy=2},{weapon=4,enemy=2},{weapon=3,enemy=2},
 {weapon=2,enemy=8},{weapon=3,enemy=8}}
local reflected,defeated,deflectSound=false,false,false
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function setup()
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
 for i=0,5 do w('Enemy_Flag',0,i);w('MmEnemyHealthLo',0,i);w('MmEnemyHealthHi',0,i);w('RgEnemyStun',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 for i=0,3 do w('MmBulletType',0,i)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 w('Player_X_Position',64);w('Player_PageLoc',0);w('Player_Y_Position',176)
 w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',1)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('PlayerStatus',1);w('InvOwnedLo',255,1);w('InvOwnedHi',7,1)
 w('InvSelected',cases[case].weapon,1);w('InvDirty',1)
 for i=1,8 do w('InvAmmo',112,16+i)end
 w('RgCooldown',0);w('SsBodyStop',0);w('SsFreeze',0);w('MmSliding',0)
 w('Enemy_Flag',1);w('Enemy_ID',cases[case].enemy);w('Enemy_State',0);w('Enemy_BoundBoxCtrl',9)
 w('Enemy_X_Position',136);w('Enemy_PageLoc',0);w('Enemy_Y_Position',176)
 w('Enemy_Y_HighPos',1);w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0)
 age=0;reflected=false;defeated=false;deflectSound=false
end
emu.addMemoryCallback(function(_,v)if frame>=550 and v==26 then deflectSound=true end end,
 emu.callbackType.write,L.SsAudioRequest)
emu.addEventCallback(function()
 emu.setInput({right=frame==80,start=frame==200,b=frame>=550 and age>=10 and age<14},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<550 then return end
 if frame==550 then
  assert(r('SelectedCharacter')==1,'Native menu selects Mega Man')
  setup();return
 end
 age=age+1
 if r('Enemy_Flag')==0 or r('Enemy_State')&32~=0 then defeated=true end
 for i=0,9 do
  if r('RgShotType',i)~=0 and r('RgShotImpact',i)&128~=0 then
   if not reflected then
    assert(r('RgShotVXHi',i)>=128,'Armored contact reverses horizontal velocity')
    assert(r('RgShotVYHi',i)==0xfd and r('RgShotVYLo',i)==0x15,
     'Armor reflection uses -350/120 vertical speed')
   end
   reflected=true
  end
 end
 if age==120 then
  if cases[case].weapon==3 then
   assert(defeated and not reflected,'Mega Man Knuckle pierces armor in case '..case)
  else
   assert(reflected and deflectSound and not defeated,
    'Mega Man shared weapon reflects with source cue, preserving armor: case '..case)
   for i=0,9 do assert(r('RgShotType',i)==0,'Reflected shot leaves live pool')end
  end
  case=case+1
  if case>#cases then
   print('PASS Mega Man inherited Metal/Pharaoh armor reflection, source cue, cleanup and Hard Knuckle piercing')
   emu.stop(0)
  else setup()end
 end
end,emu.eventType.endFrame)
