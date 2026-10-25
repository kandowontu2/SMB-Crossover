-- Enable the actual cheat through ordinary menu input, then author contact
-- arenas for every identity/power/mode. Never grant or refresh the cheat in RAM.
local frame,age,index=0,0,1
local cases={}
for c=0,12 do for v=0,(c==3 and 1 or 0)do for mode=0,1 do for power=0,2 do
 cases[#cases+1]={c=c,v=v,mode=mode,power=power}
end end end end
local current,guards,forced
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v&255,emu.memType.nesDebug)end
local function setup()
 current=cases[index];age=0;guards=0;forced=0
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for page=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,page*208+176+col)end end
 for i=0,5 do for _,n in ipairs({'Enemy_Flag','EnemyMetasprite','Enemy_CollisionBits','Enemy_State','MmEnemyFlash','MmEnemyHealthLo','MmEnemyHealthHi','RgEnemyStun','AvFrozen','AvFrozenHi','LsrFrozenPose'})do w(n,0,i)end end
 for i=0,12 do w('InvSelected',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 for i=0,3 do w('MmBulletType',0,i)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i);w('SmShotType',0,i);w('SmBombAge',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 for _,n in ipairs({'StarInvincibleTimer','InjuryTimer','TimerControl','MmDeathFlag','GuestPowerupActive','SmFlip','SmBall','SmCrouch','AvSlash','AvStopwatch','RgAttack','RgThrust','RgThrustReset','ScPogo','ScAttack','ScEnemy','XgDash','MmSliding','SsKick','SsFreeze','SsBodyStop','PreviousA_B_Buttons','A_B_Buttons','SavedJoypadBits','RgPreviousButtons','SwimmingFlag','Player_X_Speed','Player_Y_Speed','Player_X_MoveForce','Player_Y_MoveForce','MmFrictionYActive','GuestHurtKind','GuestHurtTicks','GuestInvulTicks','GuestFlickerPhase','GuestLegacyHurt','GuestBodyNow','GuestBodyPrev','GuestBodyAttack','PlayerChangeSizeFlag'})do w(n,0)end
 w('SelectedCharacter',current.c);w('BillVariant',current.v);w('PlayerStatus',current.power)
 w('CrossoverBehaviorVersion',current.mode)
 w('PlayerSize',(current.c==0 or current.c==8)and current.power==0 and 1 or 0)
 w('Player_X_Position',144);w('Player_PageLoc',0);w('Player_Y_Position',176)
 w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',1);w('Player_CollisionBits',3);w('GameEngineSubroutine',8)
 w('AreaType',1);w('StompTimer',0);w('ScrollLock',1)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0)
 w('Enemy_X_Position',146);w('Enemy_PageLoc',0);w('Enemy_Y_Position',184);w('Enemy_Y_HighPos',1)
 w('Enemy_BoundBoxCtrl',9);w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0);w('Enemy_MovingDir',1)
 w('MmEnemyHealthLo',75)
end
emu.addMemoryCallback(function()if current then guards=guards+1 end end,emu.callbackType.exec,L.CheatsInjuryTimer)
emu.addMemoryCallback(function()if current then forced=forced+1 end end,emu.callbackType.exec,L.ForceInjury)
emu.addEventCallback(function()
 emu.setInput({down=frame==60 or frame==120 or frame==140,
  start=frame==80 or frame==320 or frame==360,
  a=frame==160 or frame==200,b=frame==220 or frame==260},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<1000 then return end
 assert(r('CheatInvincible')==1,'Invincibility remains the setting enabled by ordinary menu input')
 if frame==1000 then assert(r('GameEngineSubroutine')==8,'Ordinary launch reaches gameplay');setup();return end
 age=age+1
 if age<20 then return end
 local tag='character'..current.c..' variant'..current.v..' mode'..current.mode..' power'..current.power
 assert(guards>0,'Actual native injury predicate executes for '..tag)
 assert(forced==0 and r('GameEngineSubroutine')==8 and r('MmDeathFlag')==0,'Invincibility rejects actual enemy injury for '..tag)
 assert(r('PlayerStatus')==current.power and r('GuestHurtTicks')==0 and r('GuestLegacyHurt')==0,'Invincibility retains power and avoids damage animation for '..tag)
 assert(r('InjuryTimer')==0 and r('StarInvincibleTimer')==0,'Invincibility uses neither flashing nor star mode for '..tag)
 assert(r('MmEnemyHealthLo')==75 and r('Enemy_State')&32==0,'Contact does not become a star attack for '..tag)
 print('PASS cheat native contact '..tag..' guards'..guards)
 index=index+1
 if index>#cases then print('PASS '..#cases..' actual injury arenas, all14 identities, both behavior modes, all3 power forms, menu-enabled invincibility without blink/star side effects');emu.stop(0)
 else setup()end
end,emu.eventType.endFrame)
