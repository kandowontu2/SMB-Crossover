-- Native reveals with pinned random samples. Ownership and viewed history are
-- separate fixtures: a saved/recovered weapon must never become a duplicate.
local frame,age,phase=0,0,0
local cases={
 {lo=9,hi=0,view=0,viewhi=0,roll=2,forbidden=3},
 {lo=247,hi=1,view=255,viewhi=1,roll=0,expected=3},
 {lo=255,hi=1,view=255,viewhi=1,roll=0,expected=254},
}
for sample=0,31 do cases[#cases+1]={lo=9,hi=0,view=0,viewhi=0,roll=sample,forbidden=3}end
local current,revealed,seen={},{},{}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
emu.addMemoryCallback(function()
 if frame>=550 and r('CurrentBank')%128==59 then w('PseudoRandomBitReg',current.roll,1)end
end,emu.callbackType.exec,L.InventoryPreparePickup)
local function setup()
 phase=phase+1;current=cases[phase];revealed=nil;age=0
 if not current then
  local n=0;for _ in pairs(seen)do n=n+1 end
  assert(n>=4,'Pinned random samples exercise multiple available upgrades')
  print('PASS '..#cases..' native Bass random-upgrade reveals: owned Knuckle excluded, missed Knuckle returns next pass, completed inventory gives energy');emu.stop(0);return
 end
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
 w('Block_Buffer_1',0xc1,160+7)
 for i=0,5 do w('Enemy_Flag',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 for i=0,3 do w('Block_State',0,i);w('BlockMetasprite',0,i);w('MmBulletType',0,i)end
 for i=0,1 do w('Block_RepFlag',0,i)end
 w('BlockBounceTimer',0);w('RgCooldown',0);w('SsFreeze',0);w('SsBodyStop',0)
 w('Player_X_Position',32);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',1)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 w('PlayerStatus',1);w('InvOwnedLo',current.lo,9);w('InvOwnedHi',current.hi,9)
 w('InvViewedLo',current.view,9);w('InvViewedHi',current.viewhi,9);w('InvStoredLo',0,9);w('InvStoredHi',0,9);w('InvSelected',0,9)
end
emu.addEventCallback(function()
 emu.setInput({down=frame==80,right=frame==100 or frame==120 or frame==140,start=frame==200,b=frame>=550 and age>=10 and age<16},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<550 then return end
 if frame==550 then setup();return end
 age=age+1
 for i=0,5 do if r('Enemy_Flag',i)~=0 and r('Enemy_ID',i)==0x2e and not revealed then
  revealed=r('InvPickup',i)
  if current.expected then assert(revealed==current.expected,'Expected '..current.expected..' from native reveal, got '..revealed..' phase '..phase)end
  if current.forbidden then assert(revealed~=current.forbidden,'Already owned Hard Knuckle cannot be rolled again')end
  seen[revealed]=true
 end end
 if age==110 then assert(revealed,'Controller buster reveals a native question-block reward');setup()end
end,emu.eventType.endFrame)
