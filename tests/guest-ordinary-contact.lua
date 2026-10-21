-- Explicit collision arenas, not controller-only level progression. The
-- source oracle is Character.canStomp=false and MarioBase.canStomp=true.
-- Initial positions/power forms are fixtures; all contacts use the real
-- movement, prepared body rectangles and native enemy collision dispatch.
local frame, index, age = 0, 0, 0
local cases = {}
for _,character in ipairs({0,8,1,2,3,4,5,6,7,9,10,11,12}) do
 if not ORDINARY_CHARACTER or ORDINARY_CHARACTER==character then
 for variant=0,(character==3 and 1 or 0) do
 for power=0,2 do
  for _,stale in ipairs({false,true}) do
   cases[#cases+1]={character=character,power=power,stale=stale,variant=variant}
  end
 end
 end
 end
end
local current, bodies, stomps, injuries
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug) end
local function optional(n,v) if L[n] then w(n,v) end end
local function setup()
 age,bodies,stomps,injuries=0,0,0,0
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i) end
 for page=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,page*208+176+col) end end
 for i=0,5 do
  for _,name in ipairs({'Enemy_Flag','Enemy_CollisionBits','Enemy_State','MmEnemyFlash','MmEnemyHealthLo','MmEnemyHealthHi','RgEnemyStun','AvFrozen','AvFrozenHi'}) do w(name,0,i) end
 end
 for i=0,11 do w('InvSelected',0,i);w('InvOwnedLo',0,i);w('InvOwnedHi',0,i) end
 for i=0,9 do w('RgShotType',0,i) end
 for i=0,3 do w('MmBulletType',0,i) end
 for i=0,2 do
  w('MmVX',0,i);w('MmVY',0,i);w('SmShotType',0,i);w('SmBombAge',0,i)
 end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i) end
 for _,name in ipairs({'StarInvincibleTimer','InjuryTimer','TimerControl','MmDeathFlag','GuestPowerupActive','SmFlip','SmBall','SmCrouch','AvSlash','AvStopwatch','RgAttack','RgThrust','RgThrustReset','ScPogo','ScAttack','ScEnemy','XgDash','MmSliding','SsKick','SsFreeze','SsBodyStop','PreviousA_B_Buttons','A_B_Buttons','SavedJoypadBits','RgPreviousButtons','SwimmingFlag','Player_X_Speed','Player_X_MoveForce','Player_Y_MoveForce','MmFrictionYActive'}) do w(name,0) end
 optional('GuestBodyNow',0);optional('GuestBodyPrev',0);optional('GuestBodyAttack',0)
 for _,name in ipairs({'GuestHurtKind','GuestHurtTicks','GuestInvulTicks','GuestFlickerPhase'})do optional(name,0)end
 for _,name in ipairs({'MmDeathAge','MmDeathPit','RgDeathLanded','RgDeathDelay','PlayerChangeSizeFlag'})do w(name,0)end
 w('RgDeathTotal',0);w('RgDeathTotal',0,1)
 w('SelectedCharacter',current.character);w('PlayerStatus',current.power)
 w('BillVariant',current.variant)
 local native=current.character==0 or current.character==8
 w('PlayerSize',native and current.power==0 and 1 or 0)
 w('Player_X_Position',144);w('Player_PageLoc',0)
 w('Player_Y_Position',158)
 w('Player_Y_HighPos',1);w('Player_State',2);w('Player_Y_Speed',2);w('MmVY',2,2)
 w('PlayerFacingDir',1);w('Player_CollisionBits',3);w('GameEngineSubroutine',8)
 w('AreaType',1);w('StompTimer',current.stale and 3 or 0)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0)
 w('Enemy_X_Position',144);w('Enemy_PageLoc',0);w('Enemy_Y_Position',184);w('Enemy_Y_HighPos',1)
 w('Enemy_BoundBoxCtrl',9);w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0);w('Enemy_MovingDir',1)
 w('MmEnemyHealthLo',75)
end
emu.addMemoryCallback(function() if current then bodies=bodies+1 end end,emu.callbackType.exec,L.HandlePECollisions)
emu.addMemoryCallback(function() if current then stomps=stomps+1 end end,emu.callbackType.exec,L.EnemyStomped)
emu.addMemoryCallback(function() if current then injuries=injuries+1 end end,emu.callbackType.exec,L.ForceInjury)
emu.addEventCallback(function() emu.setInput({start=frame==200},0) end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<600 then return end
 if frame==600 then index=1;current=cases[index];setup();return end
 age=age+1
 if age<24 then return end
 local tag=string.format('character%d variant%d power%d stale%s',current.character,current.variant,current.power,tostring(current.stale))
 print(string.format('CONTACT %s body%d stomp%d injury%d Y%d speed%d enemyState%d engine%d',tag,bodies,stomps,injuries,r('Player_Y_Position'),r('Player_Y_Speed'),r('Enemy_State'),r('GameEngineSubroutine')))
 assert(bodies>0,'Real prepared body overlap: '..tag)
 if current.character==0 or current.character==8 then
  assert(stomps>0 and injuries==0,'MarioBase retains its native stomp: '..tag)
  assert(r('PlayerStatus')==current.power,'Native stomp retains power: '..tag)
 else
  assert(stomps==0,'Character.canStomp=false: '..tag..' native stomps='..stomps)
  assert(injuries>0,'Ordinary guest contact injures: '..tag)
  assert(r('MmEnemyHealthLo')==75 and r('Enemy_State')&32==0,'An ordinary body contact never damages the enemy: '..tag)
  if current.character==3 then
   assert(r('GameEngineSubroutine')==11 and r('MmDeathFlag')==1 and r('PlayerStatus')==0,
    'Bill.takeDamage dies in every weapon/power form: '..tag)
  end
 end
 print('PASS source ordinary body contact '..tag)
 index=index+1;current=cases[index]
 if current then setup() else print('PASS all'..#cases..' ordinary contact arenas, source injury and stale stomp timers');emu.stop(0) end
end,emu.eventType.endFrame)
