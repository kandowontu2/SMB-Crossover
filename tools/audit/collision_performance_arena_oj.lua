-- Matched native components, arranged at the actual GameLoop entry.
-- Cold real menus/controller inputs; no cycle/physics/collision bypass.
local C=assert(COLLISION_PERF_CFG)
local wall,entered,step,phaseIndex,phaseStart=0,false,0,0,0
local menuPhase=C.mode=='hard'and'options-focus'or'start'
local names={'idle','walk','enemies','primary','jump'}
local profile;local live=0;local queryCount,queryMismatch=0,0;local measuring=false
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v&255,emu.memType.nesDebug)end
local function bank(a)return emu.convertAddress(a).address//8192 end
local trace=assert(io.open(TEST_DIR..'gameplay.csv','w'))
trace:write('update,phase,input,x,page,y,state,vx,vy,power,pose,invSelected,attack,crouch,shot0,shot1,shot2,shot3,enemy0,enemyX0,enemyY0,enemyState0,enemy1,enemyX1,enemyY1,enemyState1\n')
local queries=assert(io.open(TEST_DIR..'query-inputs.csv','w'))
queries:write('video,update,name,inputA,character\n')
local function arena()
 for i=0,5 do w('Enemy_Flag',0,i);w('EnemyMetasprite',0,i)end
 for _,n in ipairs({'TimerControl','GamePauseStatus','MmDeathFlag','AreaParserTaskNum','ScrollThirtyTwo',
  'EnemyFrenzyBuffer','EnemyFrenzyQueue','InjuryTimer','StarInvincibleTimer','GuestHurtTicks','GuestHurtKind',
  'MmSliding','SmBall','SmCrouch','RgAttack','RgCooldown','RgShootPose'})do w(n,0)end
 w('ScrollLock',1);w('CheatInvincible',0)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('Player_X_Position',64);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
 w('Player_State',0);w('Player_X_Speed',0);w('Player_Y_Speed',0);w('PlayerFacingDir',1)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 for i=0,3 do w('MmBulletType',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 if phaseIndex>=3 then
  for i=0,1 do
   for _,q in ipairs({{'Enemy_Flag',1},{'Enemy_ID',6},{'Enemy_State',0},{'Enemy_BoundBoxCtrl',9},
    {'Enemy_X_Position',208+i*24},{'Enemy_PageLoc',0},{'Enemy_Y_Position',184},{'Enemy_Y_HighPos',1},
    {'Enemy_X_Speed',0xf8},{'Enemy_Y_Speed',0},{'Enemy_MovingDir',2},{'Enemy_CollisionBits',0},{'EnemyOffscrBitsMasked',0}})do w(q[1],q[2],i)end
  end
 end
end
local function menu()
 if wall<60 or wall%12~=0 then return{}end
 if menuPhase=='options-focus'then menuPhase='options-open';return{down=true}end
 if menuPhase=='options-open'then menuPhase='mode-focus';return{a=true}end
 if menuPhase=='mode-focus'then
  if r('CrossoverMenuState')~=4 then return{}end
  if r('CrossoverOptionsFocus')~=1 then return{down=true}end
  menuPhase='mode-set'
 end
 if menuPhase=='mode-set'then if r('CrossoverBehaviorVersion')==0 then return{a=true}end;menuPhase='back';return{}end
 if menuPhase=='back'then menuPhase='start';return{b=true}end
 if menuPhase=='start'then if r('CrossoverMenuState')==2 then menuPhase='select'else return{start=true}end end
 if r('CrossoverMenuState')~=2 then return{}end
 local ix=r('CrossoverMenuIndex');local row=ix<12 and ix//6 or 2;local wanted=C.slot<12 and C.slot//6 or 2
 if row~=wanted then return{down=true}end
 if ix~=C.slot then return{right=true}end
 return{a=true}
end
local function controls()
 local age=step-phaseStart;local u=age%64
 return {right=phaseIndex>=2 and u<32,left=phaseIndex>=2 and u>=32,
  b=phaseIndex==4 and age%16<4,a=phaseIndex==5 and age%48<18}
end
emu.addEventCallback(function()
 if not entered then emu.setInput(menu(),0);return end
 emu.setInput(controls(),0)
end,emu.eventType.inputPolled)
-- Register staging before the profiler so each new phase begins before its span.
emu.addMemoryCallback(function()
 if not entered or bank(L.GameLoop)~=B.GameLoop then return end
 assert(r('SelectedCharacter')==C.character,'Requested character remains active')
 if step%120==0 then phaseIndex=phaseIndex+1;assert(phaseIndex<=5,'Bounded600update arena');phaseStart=step;arena()end
 assert(not measuring,'A measured native update completes before the next one')
 -- Fixed logical stimulus makes the CPU-work comparison independent of which
 -- video-frame joypad poll the faster implementation happens to reach. The
 -- real controller supplies that same mask throughout this complete update.
 local b=controls();local mask=(b.right and 1 or 0)|(b.left and 2 or 0)|(b.b and 64 or 0)|(b.a and 128 or 0)
 w('SavedJoypadBits',mask);w('SavedJoypad1Bits',mask)
 measuring=true
 local row={step,names[phaseIndex],r('SavedJoypadBits'),r('Player_X_Position'),r('Player_PageLoc'),r('Player_Y_Position'),r('Player_State'),r('Player_X_Speed'),r('Player_Y_Speed'),r('PlayerStatus'),r('ObjectMetasprite'),r('InvSelected',C.character),r('RgAttack'),r('RgCrouch')}
 for i=0,3 do row[#row+1]=r('MmBulletType',i)end
 for i=0,1 do for _,n in ipairs({'Enemy_Flag','Enemy_X_Position','Enemy_Y_Position','Enemy_State'})do row[#row+1]=r(n,i)end end
 if phaseIndex==3 and(r('Enemy_Flag')~=0 or r('Enemy_Flag',1)~=0)then live=live+1 end
 trace:write(table.concat(row,',')..'\n')
end,emu.callbackType.exec,L.GameLoop)
for _,name in ipairs({'ExpandedCollisionAdder','ExpandedCollisionBox'})do
 emu.addMemoryCallback(function()
  if not entered or bank(L[name])~=B[name]then return end
  local a=emu.getState()['cpu.a'];queryCount=queryCount+1
  if a~=C.character then queryMismatch=queryMismatch+1 end
  queries:write(table.concat({wall,step,name,a,r('SelectedCharacter')},',')..'\n')
 end,emu.callbackType.exec,L[name])
end
local function finish()
 assert(live>=100,'Native enemy phase must retain live actors')
 assert(queryCount>=600,'At least one real native collision query per update on average')
 profile.finish();trace:close();queries:close()
 local out=assert(io.open(TEST_DIR..'result.json','w'))
 out:write(string.format('{"passed":true,"character":%d,"mode":"%s","updates":600,"video_frames":%d,"live_enemy_samples":%d,"queries":%d,"mismatched_query_inputs":%d,"arranged_native_component":true}',C.character,C.mode,wall,live,queryCount,queryMismatch));out:close()
 emu.stop(0)
end
profile=dofile(C.observer)({out=TEST_DIR,character=C.character,phase=function()return names[phaseIndex]or'startup'end,
 onGameLoopReturn=function()
  if measuring then measuring=false;step=step+1;if step==600 then finish();return true end end
 end})
emu.addEventCallback(function()
 wall=wall+1
 if not entered and r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 then
  assert(r('SelectedCharacter')==C.character,'Real requested profile selected')
  assert(r('CrossoverBehaviorVersion')==(C.mode=='hard'and 1 or 0),'Real requested mode selected');entered=true
 end
 assert(wall<3000,'Native performance arena deadline')
end,emu.eventType.endFrame)
