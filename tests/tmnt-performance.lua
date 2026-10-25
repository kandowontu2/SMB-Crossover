-- Equal-update native performance arenas; inventory/terrain/targets arranged.
-- Real cold menus/input and ordinary native movement/combat; no cycle bypass.
local C=assert(TMNT_CFG);local wall=0;local entered=false
L.TnInputFrame=0x5c0b -- Source-owned constant, absent from exported linker labels.
local phase=C.mode=='hard'and'options-focus'or'start'
local step=0;local completed=false;local phaseIndex=0;local phaseStart=0
local names={'idle','walk','enemies','primary','secondary'}
local liveEnemySamples=0
local finish
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function bank(a)return emu.convertAddress(a).address//8192 end
local profile=dofile(C.observer)({out=TEST_DIR,phase=function()return names[phaseIndex]or'startup'end,
 onGameLoopReturn=function()if step==600 then completed=true;finish();return true end end})
local trace=assert(io.open(TEST_DIR..'gameplay.csv','w'));trace:write('update,phase,input,x,page,y,state,vx,vy,hp,gear,ammo,selected,seq,animationPhase,pose,attack,shot0,shot1,shot2,enemy0,enemyX0,enemyY0,enemyState0,enemy1,enemyX1,enemyY1,enemyState1\n')
local function arena()
 for a=0x5c00,0x5cff do emu.write(a,0,emu.memType.nesDebug)end
 for _,q in ipairs({{'TnSeq',0x80},{'TnTimer',6},{'TnPose',9},{'TnJumpStage',8},{'TnInputFrame',255}})do w(q[1],q[2])end
 w('TnHealth',128,C.variant);w('TnEquipment',phaseIndex==5 and 2 or 0,C.variant);w('TnAmmo',phaseIndex==5 and 99 or 0,C.variant);w('TnGearSelected',phaseIndex==5 and 1 or 0)
 -- Retain the native first-screen terrain and its collision/provenance cache.
 -- Inventing only a metatile array leaves native actor support inconsistent.
 for i=0,5 do w('Enemy_Flag',0,i);w('EnemyMetasprite',0,i)end
 for _,n in ipairs({'TimerControl','GamePauseStatus','MmDeathFlag','AreaParserTaskNum','ScrollThirtyTwo','EnemyFrenzyBuffer','EnemyFrenzyQueue','InjuryTimer','StarInvincibleTimer'})do w(n,0)end
 w('ScrollLock',1);w('CheatInvincible',0)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('Player_X_Position',64);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('Player_X_Speed',0);w('Player_Y_Speed',0);w('PlayerFacingDir',1)
 if phaseIndex>=3 then
  for i=0,1 do
   -- Native Goomba actor Y184 has feet at208; its sprite adds8 pixels.
   -- Y192 starts inside the floor and cannot establish native support.
   for _,q in ipairs({{'Enemy_Flag',1},{'Enemy_ID',6},{'Enemy_State',0},{'Enemy_BoundBoxCtrl',9},{'Enemy_X_Position',208+i*24},{'Enemy_PageLoc',0},{'Enemy_Y_Position',184},{'Enemy_Y_HighPos',1},{'Enemy_X_Speed',0xf8},{'Enemy_Y_Speed',0},{'Enemy_MovingDir',2},{'Enemy_CollisionBits',0},{'EnemyOffscrBitsMasked',0}})do w(q[1],q[2],i)end
  end
 end
end
finish=function()
 assert(liveEnemySamples>=100,'Enemy phase must retain live native actors')
 profile.finish();trace:close();local p=assert(io.open(TEST_DIR..'result.json','w'))
 p:write('{"passed":true,"variant":'..C.variant..',"mode":"'..C.mode..'","equal_game_updates":600,"video_frames":'..wall..',"arranged_native_component":true,"live_enemy_phase_samples":'..liveEnemySamples..'}\n');p:close();emu.stop(0)
end
local function menu()
 if wall<60 or wall%12~=0 then return{}end
 if phase=='options-focus'then phase='options-open';return{down=true}end
 if phase=='options-open'then phase='mode-focus';return{a=true}end
 if phase=='mode-focus'then
  if r('CrossoverMenuState')~=4 then return{}end
  if r('CrossoverOptionsFocus')~=1 then return{down=true}end
  phase='mode-set'
 end
 if phase=='mode-set'then if r('CrossoverBehaviorVersion')==0 then return{a=true}end;phase='back';return{}end
 if phase=='back'then phase='start';return{b=true}end
 if phase=='start'then if r('CrossoverMenuState')==2 then phase='select'else return{start=true}end end
 if r('CrossoverMenuState')~=2 then return{}end
 local ix=r('CrossoverMenuIndex');local row=ix<12 and ix//6 or 2
 if row~=2 then return{down=true}end
 if ix~=18 then return{right=true}end
 if r('TnVariant')~=C.variant then return{select=true}end
 return{a=true}
end
emu.addEventCallback(function()
 if not entered then emu.setInput(menu(),0);return end
 local u=(step-phaseStart)%64;local walking=phaseIndex>=2
 emu.setInput({right=walking and u<32,left=walking and u>=32,b=phaseIndex>=4 and step%16<4},0)
end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()
 if not entered or bank(L.TnMovement)~=B.TnMovement then return end
 if step%120==0 then phaseIndex=phaseIndex+1;assert(phaseIndex<=5,'Performance work remains bounded');phaseStart=step;arena()end
 local v={step,names[phaseIndex],r('SavedJoypadBits'),r('Player_X_Position'),r('Player_PageLoc'),r('Player_Y_Position'),r('Player_State'),r('TnVXHi'),r('TnVYHi'),r('TnHealth',C.variant),r('TnEquipment',C.variant),r('TnAmmo',C.variant),r('TnGearSelected'),r('TnSeq'),r('TnPhase'),r('TnPose'),r('TnAttack')}
 for i=0,2 do v[#v+1]=r('TnShotKind',i)end
 for i=0,1 do for _,n in ipairs({'Enemy_Flag','Enemy_X_Position','Enemy_Y_Position','Enemy_State'})do v[#v+1]=r(n,i)end end
 if phaseIndex==3 and(r('Enemy_Flag')~=0 or r('Enemy_Flag',1)~=0)then liveEnemySamples=liveEnemySamples+1 end
 trace:write(table.concat(v,',')..'\n');step=step+1
end,emu.callbackType.exec,L.TnMovement)
emu.addEventCallback(function()
 wall=wall+1
 if not entered and r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 then
  assert(r('SelectedCharacter')==19 and r('TnVariant')==C.variant,'Real requested turtle selected');entered=true
 end
 assert(wall<3000,'Performance arena deadline')
end,emu.eventType.endFrame)
