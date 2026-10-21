-- Seeded native Mushroom/Flower contact, not a whole-stage route or emergence
-- test. The real collision, inventory fallback and60-update transform execute.
local C=assert(EASY_PICKUP);local A,H=C.ram,C.hooks
local frame,index,phase,age=0,0,'boot',0
local current,receipt,updates=nil,false,0
local out=assert(io.open(C.out..'events.jsonl','w'))
local function r(n,i)return emu.read(assert(A[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(A[n],n)+(i or 0),v&255,emu.memType.nesDebug)end
local function log(s)out:write(s..'\n');out:flush()end
local function hook(n,fn)
 local h=assert(H[n],n)
 emu.addMemoryCallback(function()
  local p=emu.convertAddress(h.address)
  if not p or p.memType~=emu.memType.nesPrgRom or p.address//8192~=h.physical_bank then return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==v,'Physical hook '..n)end
  fn()
 end,emu.callbackType.exec,h.address)
end
local fields={'InvOwnedLo','InvOwnedHi','InvViewedLo','InvViewedHi','InvStoredLo','InvStoredHi','InvSelected'}
local inventory={};local ammo={}
local function seed(c)
 current=c;receipt=false;updates=0;age=0
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
 for i=0,5 do w('Enemy_Flag',0,i);w('Enemy_CollisionBits',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 for i=0,3 do w('MmBulletType',0,i)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i);w('SmShotType',0,i);w('SmBombAge',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 local zero={'TimerControl','InjuryTimer','StarInvincibleTimer','GuestPowerupActive','GuestLegacyHurt','GuestHurtKind','GuestHurtTicks','GuestInvulTicks','MmDeathFlag','MmDeathAge','DisableCollisionDet','Player_X_Speed','Player_Y_Speed','Player_X_MoveForce','Player_Y_MoveForce','SmBall','SmCrouch','RgCrouch','RgAttack','MmSliding','MmLastXSpeed','MmFrictionYActive','GamePauseStatus','ScrollAmount','AreaParserTaskNum','ScrollThirtyTwo','EnemyFrenzyBuffer','EnemyFrenzyQueue','PlayerChangeSizeFlag','InvRefill'}
 for _,n in ipairs(zero)do w(n,0)end
 w('SelectedCharacter',c.char);w('BillVariant',c.variant);w('CrossoverBehaviorVersion',0);w('PlayerStatus',c.power);w('PlayerSize',0)
 w('GameEngineSubroutine',8);w('Player_State',0);w('SwimmingFlag',0);w('AreaType',1)
 w('Player_X_Position',128);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_CollisionBits',3)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0);w('ScrollLock',1)
 -- Deliberately staleHard inventory must neither grant nor consume anything.
 for _,n in ipairs(fields)do w(n,n=='InvSelected'and 5 or 255,c.char);inventory[n]=r(n,c.char)end
 for i=0,191 do w('InvAmmo',(i*7+3)%113,i);ammo[i]=r('InvAmmo',i)end
 w('Enemy_Flag',1,5);w('Enemy_ID',0x2e,5);w('Enemy_State',0x80,5);w('PowerUpType',c.kind,5);w('Enemy_BoundBoxCtrl',3,5)
 w('Enemy_X_Position',128,5);w('Enemy_PageLoc',0,5);w('Enemy_Y_Position',184,5);w('Enemy_Y_HighPos',1,5);w('Enemy_X_Speed',0,5);w('Enemy_Y_Speed',0,5)
 w('InvPickupOwner',c.char,5);w('InvPickup',5,5)
 phase='collect'
 log(string.format('{"event":"seed","case":%d,"char":%d,"variant":%d,"power":%d,"kind":%d}',index,c.char,c.variant,c.power,c.kind))
end
hook('Collect',function()
 if not current then return end
 assert(not receipt,'One actual native pickup per arena');receipt=true
 assert(emu.getState()['cpu.x']==5 and r('PowerUpType',5)==current.kind,'Actual authored power-up reaches native collision')
end)
hook('Update',function()
 if not current or not receipt then return end
 assert(current.power<2,'Max tier does not enter a transform')
 assert(r('GuestPowerupAge')==updates,'Sequential native transform updates')
 assert(r('GuestLegacyHurt')==0,'Pickup never enters injury lifecycle')
 updates=updates+1
end)
emu.addEventCallback(function()emu.setInput({start=frame==60 or frame==240},0)end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1;if frame<600 then return end
 if phase=='boot'or phase=='next'then
  assert(r('OperMode')==1 and r('OperMode_Task')==3,'Ordinary boot reached gameplay')
  index=index+1
  if not C.cases[index]then
   out:close();local f=assert(io.open(C.out..'result.json','w'));f:write(string.format('{"status":"PASS_NATIVE_EASY_PICKUP_TIERS","cases":%d,"frames":%d,"route_proof":false}',index-1,frame));f:close()
   print('PASS_NATIVE_EASY_PICKUP_TIERS '..index-1);emu.stop(0);return
  end
  seed(C.cases[index]);return
 end
 age=age+1
 if receipt then
  for _,n in ipairs(fields)do assert(r(n,current.char)==inventory[n],'Easy ignores staleHard inventory '..n)end
  for i=0,191 do assert(r('InvAmmo',i)==ammo[i],'No ammo change during Easy pickup '..i)end
  assert(r('InvHudActive')==0,'Easy classic hides2.02 weapon HUD')
  if current.power==2 or(r('GuestPowerupActive')==0 and updates>0)then
   assert(r('PlayerStatus')==math.min(2,current.power+1),'Either Mushroom or Flower increments exactly one original tier')
   assert(updates==(current.power==2 and 0 or 60),'Exactly60 transform updates below cap; none at cap')
   assert(r('GameEngineSubroutine')==8 and r('TimerControl')==0,'Native pickup resumes normal control')
   log(string.format('{"event":"pass","case":%d,"updates":%d,"status":%d}',index,updates,r('PlayerStatus')))
   phase='next';current=nil
  end
 end
 assert(age<100,'Bounded actual pickup and transform case '..index)
end,emu.eventType.endFrame)
