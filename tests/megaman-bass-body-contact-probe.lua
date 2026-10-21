-- Diagnostic only: explicit arena/body fixtures, real menu and Down+A start.
-- It records actual native collision dispatch without claiming source success.
local c=CONTACT_CHAR or 1
local frame,age,phase=0,0,0
local body,stomps,injures,damage=0,0,0,0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
for _,name in ipairs({'HandlePECollisions','EnemyStomped','InjurePlayer'})do
 emu.addMemoryCallback(function()if frame>=550 then if name=='HandlePECollisions'then body=body+1 elseif name=='EnemyStomped'then stomps=stomps+1;print('CONTACT_EVENT char'..c..' phase'..phase..' nativeStomp HP'..r('MmEnemyHealthLo')..' power'..r('PlayerStatus')) else injures=injures+1;print('CONTACT_EVENT char'..c..' phase'..phase..' nativeInjury HP'..r('MmEnemyHealthLo')..' power'..r('PlayerStatus')) end end end,emu.callbackType.exec,L[name])
end
emu.addEventCallback(function()
 emu.setInput({down=(c==9 and frame==80)or(phase==1 and age>=10 and age<14),right=(c==1 and frame==80)or(c==9 and(frame==100 or frame==120 or frame==140)),start=frame==200,a=phase==1 and age>=10 and age<14},0)
end,emu.eventType.inputPolled)
local function setup()
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+176+col)end end
 for i=0,5 do w('Enemy_Flag',0,i);w('MmEnemyHealthLo',0,i);w('MmEnemyHealthHi',0,i);w('Enemy_CollisionBits',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 for i=0,3 do w('MmBulletType',0,i)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 w('Player_X_Position',80);w('Player_PageLoc',0);w('Player_Y_Position',phase==0 and 158 or 176);w('Player_Y_HighPos',1)
 w('Player_State',phase==0 and 2 or 0);w('Player_Y_Speed',phase==0 and 2 or 0);w('Player_X_Speed',0);w('PlayerFacingDir',1);w('Player_CollisionBits',3)
 w('PlayerStatus',1);w('PlayerSize',0);w('InvOwnedLo',255,c);w('InvSelected',phase==0 and 0 or 5,c);w('InvAmmo',4,c*16+5);w('InvDirty',1)
 w('InjuryTimer',0);w('StompTimer',0);w('GameEngineSubroutine',8);w('TimerControl',0);w('MmDeathFlag',0);w('GuestPowerupActive',0);w('StarInvincibleTimer',0)
 w('MmSliding',0);w('XgDash',0);w('SsKick',0);w('SsFreeze',0);w('SsBodyStop',0);w('PreviousA_B_Buttons',0);w('A_B_Buttons',0);w('RgPreviousButtons',0)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 if phase==0 then
  w('MmVY',2,2);w('MmFrictionYActive',0)
  w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_X_Position',80);w('Enemy_PageLoc',0);w('Enemy_Y_Position',184);w('Enemy_Y_HighPos',1);w('Enemy_BoundBoxCtrl',9);w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0);w('MmEnemyHealthLo',75)
 end
 age=0;body=0;stomps=0;injures=0
end
emu.addEventCallback(function()
 frame=frame+1;if frame<550 then return end
 if frame==550 then assert(r('SelectedCharacter')==c,'Real selected character');setup();return end
 age=age+1
 if phase==1 and age==16 then
  w('Enemy_Flag',1);w('Enemy_ID',0);w('Enemy_State',0);w('Enemy_X_Position',r('Player_X_Position')+8);w('Enemy_PageLoc',r('Player_PageLoc'));w('Enemy_Y_Position',184);w('Enemy_Y_HighPos',1);w('Enemy_BoundBoxCtrl',9);w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0);w('MmEnemyHealthLo',100)
 end
 if phase==1 and age>=16 and age<30 then w('Enemy_Y_Position',184);w('Enemy_Y_Speed',0)end
 if age==40 then
  print(string.format('CONTACT char%d phase%d body%d stomps%d injuryCalls%d power%d engine%d HP%d enemyState%d VY%d kick%d slide%d dash%d ammo%d',c,phase,body,stomps,injures,r('PlayerStatus'),r('GameEngineSubroutine'),r('MmEnemyHealthLo'),r('Enemy_State'),r('Player_Y_Speed'),r('SsKick'),r('MmSliding'),r('XgDash'),r('InvAmmo',c*16+5)))
  phase=phase+1;if phase==2 then print('PASS diagnostic recorded actual contact outcomes; no source-fidelity acceptance is claimed');emu.stop(0)else setup()end
 end
end,emu.eventType.endFrame)

