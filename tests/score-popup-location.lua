-- Explicit six-target arenas. Actual Bill shots defeat each target and the
-- native number renderer must use that target's position. A deliberately stale
-- shared relative-X value reproduces the ordinary-play failure; no clear claim.
SelectEasyRules()
local frame,case,age,observed,rendered=0,0,0,false,false
local pending,numberRender=nil,false
local callReturn;local returnHooks={};local returned=false
local cameras={0,224,256,511,512,768}
local screenX={112,96,160,80,200,128}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function pos(lo,hi,v,i)w(lo,v%256,i);w(hi,v//256,i)end
local function setup()
 age=0;observed=false;rendered=false;pending=nil;numberRender=false;callReturn=nil;returned=false
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+176+col)end end
 for i=0,5 do w('Enemy_Flag',0,i);w('FloateyNum_Control',0,i);w('MmEnemyFlash',0,i);w('AvFrozen',0,i);w('AvFrozenHi',0,i);w('InvPickup',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 for i=0,3 do w('MmBulletType',0,i);w('InvDropKind',0,i)end
 local cam=cameras[case];local slot=case-1
 pos('ScreenLeft_X_Pos','ScreenLeft_PageLoc',cam);pos('ScreenRight_X_Pos','ScreenRight_PageLoc',cam+255)
 w('HorizontalScroll',cam%256);w('ScrollAmount',0);w('ScrollLock',1);w('ScrollThirtyTwo',0);w('AreaParserTaskNum',0)
 pos('Player_X_Position','Player_PageLoc',cam+32);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0)
 w('PlayerFacingDir',1);w('Player_CollisionBits',3);w('Player_X_Speed',0);w('Player_Y_Speed',0);w('MmLastXSpeed',0)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 w('PlayerStatus',1);w('PlayerSize',0);w('CrouchingFlag',0);w('RgCrouch',0);w('MmSliding',0)
 w('GuestPowerupActive',0);w('GuestHurtKind',0);w('GuestHurtTicks',0);w('GuestInvulTicks',255);w('InjuryTimer',0);w('StarInvincibleTimer',0)
 w('TimerControl',0);w('GameEngineSubroutine',8);w('EnemyFrenzyBuffer',0);w('EnemyFrenzyQueue',0);w('RgCooldown',0)
 w('Enemy_Flag',1,slot);w('Enemy_ID',6,slot);w('Enemy_State',0,slot);w('Enemy_BoundBoxCtrl',9,slot)
 pos('Enemy_X_Position','Enemy_PageLoc',cam+screenX[case],slot);w('Enemy_Y_Position',184,slot);w('Enemy_Y_HighPos',1,slot)
 w('Enemy_X_Speed',0,slot);w('Enemy_Y_Speed',0,slot);w('Enemy_MovingDir',2,slot)
 w('MmEnemyHealthLo',1,slot);w('MmEnemyHealthHi',0,slot)
end
emu.addMemoryCallback(function()
 if case==0 or observed then return end
 local s=emu.getState();if s['cpu.x']~=case-1 then return end
 assert((r('Enemy_State',case-1)&32)~=0,'An actual weapon defeat produces this score')
 local wx=r('Enemy_X_Position',case-1)+256*r('Enemy_PageLoc',case-1)
 local camera=r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc')
 pending=(wx-camera)%256
 w('Enemy_Rel_XPos',(pending+128)%256) -- Authored stale cache, as in the movie.
 local selector=ROM_NAME:find('mmc3',1,true)and r('BankShadow')or nil
 local sp=s['cpu.sp'];local pc=(emu.read(0x100+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+1)%65536
 callReturn={pc=pc,sp=sp,x=s['cpu.x'],y=s['cpu.y'],p=s['cpu.ps'],bank=r('CurrentBank'),bankC=r('CurrentBankC'),selector=selector}
 if not returnHooks[pc]then
  returnHooks[pc]=true
  emu.addMemoryCallback(function()
   local z=callReturn;if not z or z.pc~=pc then return end
   local q=emu.getState();if q['cpu.sp']~=(z.sp+2)%256 then return end
   assert(q['cpu.a']==pending and q['cpu.x']==z.x and q['cpu.y']==z.y and(q['cpu.ps']&0x4d)==(z.p&0x4d),'Native score caller registers and preserved flags survive the cold call')
   assert(r('CurrentBank')==z.bank and r('CurrentBankC')==z.bankC,'Both actual mapper windows return to the caller')
   if z.selector then assert(r('BankShadow')==z.selector,'The actual MMC3 selector is restored')end
   callReturn=nil;returned=true
  end,emu.callbackType.exec,pc)
 end
end,emu.callbackType.exec,L.SetupFloateyNumber)
emu.addMemoryCallback(function(a,v)
 if pending==nil or a~=L.FloateyNum_X_Pos+case-1 then return end
 assert(v==pending,'Defeat score must follow its target instead of the stale shared position')
 observed=true
end,emu.callbackType.write,L.FloateyNum_X_Pos,L.FloateyNum_X_Pos+6)
emu.addMemoryCallback(function()
 if case>0 and observed and r('CurrentBank')%128==B.FloateyNumberRender and emu.getState()['cpu.x']==case-1 then numberRender=true end
end,emu.callbackType.exec,L.FloateyNumberRender)
emu.addMemoryCallback(function()
 if not numberRender or r('CurrentBank')%128~=B.MetaspriteRenderLoop then return end
 numberRender=false
 assert(r('R4')==pending and r('R5')==0,'The actual number renderer receives the target screen position')
 rendered=true
end,emu.callbackType.exec,L.MetaspriteRenderLoop)
emu.addEventCallback(function()
 -- Goomba's source body is below Bill's standing muzzle; use real prone fire.
 emu.setInput({start=frame==60 or frame==240,right=frame==80 or frame==100 or frame==120,down=case>0,b=case>0 and frame%12<5},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1;if frame<600 then return end
 if case==0 then case=1;setup();return end
 age=age+1
 if rendered and returned then
  print('PASS score target slot'..(case-1)..' camera'..cameras[case])
  if case==6 then print('PASS six native weapon defeats, stale-cache score anchors and actual number rendering across scroll/page boundaries');emu.stop(0);return end
  case=case+1;setup()
 end
 assert(age<240,'Every authored target is actually defeated and its score rendered')
end,emu.eventType.endFrame)
