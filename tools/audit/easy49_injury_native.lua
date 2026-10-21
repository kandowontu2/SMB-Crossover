-- Explicit contact arenas. Only initial RAM setup and removal of the authored
-- impact actor are scripted. Damage, timers, positions and mode gates execute.
local C=assert(EASY_INJURY);local A,H=C.ram,C.hooks
local frame,index,phase,age=0,0,'boot',0
local current,receipt,freeze,immune,lastImmune,completed=nil,false,0,0,nil,0
local out=assert(io.open(C.out..'events.jsonl','w'))
local function r(n,i)return emu.read(assert(A[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(A[n],n)+(i or 0),v&255,emu.memType.nesDebug)end
local function json(t)local b={};for k,v in pairs(t)do b[#b+1]=string.format('%q',tostring(k))..':'..(type(v)=='string'and string.format('%q',v)or tostring(v))end;table.sort(b);return'{'..table.concat(b,',')..'}'end
local function log(t)out:write(json(t)..'\n');out:flush()end
local depth=0
local function hook(name,fn,interrupt)
 local h=assert(H[name],name)
 emu.addMemoryCallback(function()
  local p=emu.convertAddress(h.address)
  if not p or p.memType~=emu.memType.nesPrgRom or p.address//8192~=h.physical_bank then return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==v,'Physical hook '..name)end
  if interrupt or depth==0 then fn()end
 end,emu.callbackType.exec,h.address)
end
for _,n in ipairs({'NMI','IRQ'})do hook(n,function()depth=depth+1 end,true)end
for _,n in ipairs({'NMIEnd','IRQEnd'})do hook(n,function()depth=depth-1;assert(depth>=0,'Interrupt lineage')end,true)end
local position={'Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','MmVX','MmVY','MmXFraction','MmYFraction'}
local function snap()
 local t={}
 for _,n in ipairs(position)do
  local length=(n=='MmVX'or n=='MmVY')and 3 or(n=='MmXFraction'or n=='MmYFraction')and 2 or 1
  for i=0,length-1 do t[n..i]=r(n,i)end
 end
 t.worldX=r('Enemy_X_Position',1);t.worldY=r('Enemy_Y_Position',1);t.worldTimer=r('EnemyIntervalTimer',1)
 return t
end
local frozenSnapshot
local function seed(c)
 current=c;receipt=false;freeze=0;immune=0;lastImmune=nil;age=0;frozenSnapshot=nil
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
 for i=0,5 do w('Enemy_Flag',0,i);w('Enemy_State',0,i);w('Enemy_CollisionBits',0,i);w('AvFrozen',0,i);w('AvFrozenHi',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 for i=0,3 do w('MmBulletType',0,i)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i);w('SmShotType',0,i);w('SmBombAge',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 local zero={'TimerControl','InjuryTimer','StarInvincibleTimer','GuestPowerupActive','GuestLegacyHurt','GuestHurtKind','GuestHurtTicks','GuestInvulTicks','MmDeathFlag','MmDeathAge','PlayerChangeSizeFlag','DisableCollisionDet','Player_X_Speed','Player_Y_Speed','Player_X_MoveForce','Player_Y_MoveForce','SmBall','SmCrouch','RgCrouch','RgAttack','MmSliding','XgDash','MmOnVine','MmLastXSpeed','MmFrictionYActive','GamePauseStatus','ScrollAmount','AreaParserTaskNum','ScrollThirtyTwo','EnemyFrenzyBuffer','EnemyFrenzyQueue','StompTimer','EnemyOffscrBitsMasked'}
 for _,n in ipairs(zero)do w(n,0)end
 w('SelectedCharacter',c.char);w('BillVariant',c.variant);w('CrossoverBehaviorVersion',c.mode)
 w('PlayerStatus',c.power);w('PlayerSize',0);w('PlayerFacingDir',c.dir)
 w('GameEngineSubroutine',8);w('Player_State',0);w('SwimmingFlag',0);w('AreaType',1)
 w('Player_X_Position',128);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_CollisionBits',3)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0);w('ScrollLock',1)
 w('InvOwnedLo',255,c.char);w('InvOwnedHi',255,c.char);w('InvSelected',0,c.char)
 w('Enemy_Flag',1);w('Enemy_ID',18);w('Enemy_BoundBoxCtrl',9);w('Enemy_Y_HighPos',1)
 w('Enemy_X_Position',136);w('Enemy_PageLoc',0);w('Enemy_Y_Position',184);w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0)
 w('Enemy_Flag',1,1);w('Enemy_ID',6,1);w('Enemy_BoundBoxCtrl',9,1);w('Enemy_Y_HighPos',1,1)
 w('Enemy_X_Position',32,1);w('Enemy_PageLoc',0,1);w('Enemy_Y_Position',184,1);w('Enemy_X_Speed',248,1);w('Enemy_Y_Speed',0,1);w('EnemyIntervalTimer',90,1);w('Enemy_MovingDir',2,1)
 phase='contact';log({event='seed',case=index,char=c.char,mode=c.mode,power=c.power,variant=c.variant,dir=c.dir,frame=frame})
end
hook('Damage',function()
 if not current then return end
 assert(not receipt,'Exactly one actual authored injury per arena')
 assert(phase=='contact','Actual authored contact phase')
 receipt=true;log({event='actual-contact',case=index,frame=frame,status=r('PlayerStatus'),engine=r('GameEngineSubroutine')})
end)
hook('Update',function()
 if not current or current.mode~=0 or current.power==0 or not receipt then return end
 assert(r('GuestLegacyHurt')==1,'Easy contact enters frozen legacy lifecycle')
 assert(r('GuestPowerupAge')==freeze,'One sequential source freeze update')
 if not frozenSnapshot then frozenSnapshot=snap()end
 local actual=snap();for k,v in pairs(frozenSnapshot)do assert(actual[k]==v,'World/position/velocity frozen '..k)end
 freeze=freeze+1;assert(freeze<=60,'Source1000ms freeze bound')
end)
local function nextCase()
 completed=completed+1
 log({event='case-pass',case=index,frame=frame,freeze=freeze,protection=immune,char=current.char,power=current.power,mode=current.mode})
 phase='next';current=nil
end
emu.addEventCallback(function()
 local b={};if frame==60 or frame==240 then b.start=true end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<600 then return end
 if phase=='boot'or phase=='next'then
  assert(r('OperMode')==1 and r('OperMode_Task')==3,'Ordinary power-on reached gameplay')
  index=index+1
  if not C.cases[index]then
   out:close();local f=assert(io.open(C.out..'result.json','w'));f:write(json({status='PASS_NATIVE_LEGACY_DAMAGE',cases=completed,frames=frame,route_proof=false,source='Character.as1000ms freeze then2500ms protection'}));f:close()
   print('PASS_NATIVE_LEGACY_DAMAGE '..completed..' contact arenas');emu.stop(0);return
  end
  seed(C.cases[index]);return
 end
 age=age+1
 if receipt then
  w('Enemy_Flag',0) -- Remove only the explicitly authored impact actor.
  local c=current
  if c.power==0 or(c.mode==1 and c.char==3)then
   if r('GameEngineSubroutine')==11 then assert(r('GuestLegacyHurt')==0,'One-hit death bypasses Easy shrink');nextCase()end
  elseif c.mode==0 then
   if r('GuestPowerupActive')~=0 then
    assert(r('GameEngineSubroutine')==9 and r('TimerControl')>=254,'Frozen source shrink engine')
    assert(r('GuestPowerupTarget')==0 and r('GuestPowerupOld')==c.power,'Shrink targets default tier')
    assert(r('GuestPowerupDisplay')==((math.floor(r('GuestPowerupAge')/6)%2==0)and c.power or 0),'Actual alternating power tier at100ms')
   elseif r('GuestLegacyHurt')==1 then
    assert(freeze==60 and r('PlayerStatus')==0 and r('GameEngineSubroutine')==8,'Exactly60 updates finish shrink without recoil')
   elseif r('GuestLegacyHurt')==2 then
    local n=r('GuestInvulTicks');assert(n==150-immune,'Full2500ms post-freeze protection');immune=immune+1;lastImmune=n
    assert(r('InjuryTimer')~=0 and r('GuestHurtTicks')==0,'Protected live movement without Hard recoil')
    if immune==150 then phase='expiry'end
   elseif phase=='expiry'then
    assert(immune==150 and lastImmune==1 and r('GuestInvulTicks')==0 and r('InjuryTimer')==0,'Protection expires after150 live updates')
    nextCase()
   else error('Unexpected Easy damage lifecycle')end
  else
   assert(r('GuestLegacyHurt')==0 and r('GuestPowerupActive')==0,'Hard keeps live source recoil')
   if age>=110 then assert(r('GuestHurtKind')==0 and r('PlayerStatus')==0 and r('GameEngineSubroutine')==8 and r('MmDeathFlag')==0,'Hard source recoil/protection completes alive');nextCase()end
  end
 end
 assert(age<300,'Bounded actual damage receipt and lifecycle case'..index)
end,emu.eventType.endFrame)
