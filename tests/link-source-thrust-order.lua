-- Source HitTester executes a body attack and then a distinct sword rectangle.
-- C_HIT records this update; only L_HIT suppresses repeated rectangle contacts.
-- These are explicit contact arenas; no gameplay route is synthesized.
local frame,depth,index,pending,needArena=0,0,1,nil,true
local cases={}
for power=0,2 do for direction=1,2 do cases[#cases+1]={power=power,direction=direction}end end
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
for _,pc in ipairs({assert(L.NonMaskableInterrupt),assert(L.IrqScrollSplit)})do emu.addMemoryCallback(function()depth=depth+1 end,emu.callbackType.exec,pc)end
for _,pc in ipairs({assert(L.NonMaskableInterrupt_RTI),assert(L.IrqScrollSplit_RTI)})do emu.addMemoryCallback(function()depth=depth-1;assert(depth>=0,'Balanced Link order interrupts')end,emu.callbackType.exec,pc)end
emu.addEventCallback(function()emu.setInput({right=frame>=80 and frame<160 and(frame-80)%20==0,start=frame==200},0)end,emu.eventType.inputPolled)
local function arena()
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for i=0,5 do w('Enemy_Flag',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 w('Player_X_Position',128);w('Player_PageLoc',0);w('Player_Y_Position',146);w('Player_Y_HighPos',1)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0);w('HorizontalScroll',0)
 w('GameEngineSubroutine',8);w('AreaType',1);w('SwimmingFlag',0);w('TimerControl',0);w('GuestPowerupActive',0)
 w('Player_State',2);w('PlayerStatus',1);w('PlayerSize',0);w('Player_X_Speed',0);w('Player_Y_Speed',2)
 w('StarInvincibleTimer',0);w('InjuryTimer',0);w('StompTimer',0);w('Enemy_CollisionBits',0)
 w('RgAttack',0);w('RgThrust',0);w('RgThrustReset',0);w('RgCrouch',0)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end;w('MmVY',2,2)
 w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_BoundBoxCtrl',9)
 w('Enemy_X_Position',128);w('Enemy_PageLoc',0);w('Enemy_Y_Position',176);w('Enemy_Y_HighPos',1);w('Enemy_X_Speed',0);w('Enemy_Y_Speed',0);w('EnemyOffscrBitsMasked',0)
end
emu.addMemoryCallback(function()
 if frame<560 or depth~=0 or r('CurrentBank')%128~=8 then return end
 assert(not pending,'Body order arena waits for its deferred rectangle')
 local c=cases[index];pending={c=c,body=false}
 local p=c.direction==1 and{128,146,144,177}or{128,170,144,201}
 local lp=c.direction==1 and{128,112,144,143}or{128,180,144,211}
 local e=c.direction==1 and{128,160,144,175}or{128,148,144,163}
 for i=0,3 do w('BoundingBox_UL_Corner',p[i+1],i);w('BoundingBox_UL_Corner',e[i+1],4+i);w('LinkLastBoxes',lp[i+1],i);w('LinkLastBoxes',e[i+1],4+i)end
 w('LinkLastIds',6);w('LinkLastValid',1);w('LinkThrustPrev',1);w('LinkThrustNow',0);w('LinkThrustReceipt',0)
 w('RgThrust',c.direction);w('Player_State',1);w('PlayerStatus',c.power);w('InvOwnedLo',0,4);w('InvOwnedHi',0,4)
 w('Player_Y_Position',c.direction==1 and 146 or 162);w('Player_Rel_YPos',r('Player_Y_Position'))
 w('Enemy_Y_Position',c.direction==1 and 160 or 148);w('Enemy_X_Position',128)
 w('RgEnemiesPresent',1);w('MmEnemyHealthLo',500%256);w('MmEnemyHealthHi',1)
 w('MmVY',0);w('MmVY',0,1);w('MmVY',c.direction==2 and 254 or 2,2)
end,emu.callbackType.exec,assert(L.LinkBodyContact))
emu.addMemoryCallback(function()
 if not pending or depth~=0 or r('CurrentBank')%128~=8 then return end
 local damage=({50,75,100})[pending.c.power+1]
 assert(r('MmEnemyHealthLo')+256*r('MmEnemyHealthHi')==500-damage,'Matching source body applies one ring-dependent attack first')
 assert(r('LinkThrustPrev')==0 and r('LinkThrustNow')==1,'Source body clears last dictionary and records current attack')
 pending.body=true
end,emu.callbackType.exec,assert(L.LinkBodyContactProtected))
emu.addMemoryCallback(function()
 if not pending or depth~=0 or r('CurrentBank')%128~=B.LinkDeferredThrustFinish then return end
 local c=pending.c;local damage=({50,75,100})[c.power+1]
 assert(pending.body,'Actual native body contact precedes the independent sword pass')
 assert(r('MmEnemyHealthLo')+256*r('MmEnemyHealthHi')==500-2*damage,'Source C_HIT permits body plus overlapping sword, not an invented one-hit lock: power'..c.power..' dir'..c.direction..' hp'..(r('MmEnemyHealthLo')+256*r('MmEnemyHealthHi')))
 assert(r('LinkThrustReceipt')==1,'Only canonical body receipt remains after the enemy-only pass')
 pending=nil;index=index+1;needArena=true
 if not cases[index]then print('PASS six source Link body-then-thrust dual attacks at every ring tier, including Up and Down');emu.stop(0)end
end,emu.callbackType.exec,assert(L.LinkDeferredThrustFinish))
emu.addEventCallback(function()
 frame=frame+1
 if frame==550 then assert(r('SelectedCharacter')==4,'Real menu launches Link before ordering arenas')end
 if frame>=560 and not pending and needArena then arena();needArena=false end
 assert(frame<1000,'All source-ordered body/sword contacts complete')
end,emu.eventType.endFrame)
