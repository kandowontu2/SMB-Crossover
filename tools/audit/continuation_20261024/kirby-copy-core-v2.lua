-- Prefix supplies cold actual menus, r/w/tile and physical-frame counters.
-- Frozen target-family actors isolate copy acquisition. Attacks use an ordinary
-- unfrozen Goomba. No copied ability is injected; Select discards between cases.
local phase='boot';local tick=0;local pending=nil;local results={}
local mouthFrame,copyFrame,attackSeen,kills,guardContacts,spawned=0,0,false,0,0,false
local dropFrame,orbFrame,recovered=0,0,false
local guardProtected=false
local startY,minY,maxY=176,176,176
local out=assert(io.open(OUTPUT..'copy-trace.csv','w'))
out:write('frame,case,phase,tick,power,x,y,hp,copy,mouth,action,actionAge,enemyFlag,enemyY,drop,dropAge,shot0,shot1,shot2,kills,guardContacts\n')
local function setPhase(name)phase=name;tick=0 end
local function baseArena()
 assert(r('KbHealth')==6 and r('KbCopy')==0 and r('KbMouth')==0,'Prior ability naturally discarded without health loss')
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i);w('MmBrickHealth',0,i)end
 for p=0,1 do
  for row=2,14 do for col=0,15 do tile(p,col,row,row>=13 and 0x54 or 0)end end
  for col=0,15 do w('Block_Buffer_1',0x54,p*208+176+col);w('Block_Buffer_1',0x54,p*208+192+col)end
 end
 for i=0,5 do w('Enemy_Flag',0,i);w('Enemy_CollisionBits',0,i)end
 for i=0,3 do w('Block_State',0,i);w('BlockMetasprite',0,i)end
 for i=0,1 do w('Block_RepFlag',0,i);w('MmXFraction',0,i);w('MmYFraction',0,i)end
 for _,n in ipairs({'BlockBounceTimer','SmBall','SmCrouch','MmSliding','Player_X_Speed','Player_Y_Speed','ScrollThirtyTwo','AreaParserTaskNum','InjuryTimer','StarInvincibleTimer','GamePauseStatus','TimerControl'})do w(n,0)end
 w('ScrollLock',1);w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('Player_X_Position',96);w('Player_PageLoc',0);w('MmOldX',96);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',1);w('GameEngineSubroutine',8)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i);assert(r('KbShotType',i)==0,'Previous native projectile expired')end
 mouthFrame=0;copyFrame=0;attackSeen=false;kills=0;guardContacts=0;spawned=false;recovered=false;guardProtected=false;startY=176;minY=176;maxY=176
end
local function actor(id,x,y)
 for _,v in ipairs({{'Enemy_Flag',1},{'Enemy_ID',id},{'Enemy_State',0},{'Enemy_BoundBoxCtrl',9},{'Enemy_X_Position',x},{'Enemy_PageLoc',0},{'Enemy_Y_Position',y},{'Enemy_Y_HighPos',1},{'Enemy_X_Speed',0},{'Enemy_Y_Speed',0},{'Enemy_Y_MoveForce',0},{'Enemy_MovingDir',2},{'Enemy_CollisionBits',0}})do w(v[1],v[2])end
end
local function startCase()
 baseArena();local c=C.copies[stage]
 w('AvStopwatch',255);actor(c.enemy,136,184)
 results[stage]={power=c.power,enemy=c.enemy};setPhase('inhale')
end
emu.addMemoryCallback(function()
 if emu.convertAddress(L.GameLoop).address//8192~=B.GameLoop or not pending then return end
 local f=pending;pending=nil;f()
end,emu.callbackType.exec,L.GameLoop)
emu.addMemoryCallback(function()
 if entered and phase=='attack'and emu.convertAddress(0xa000).address//8192==B.KbWeapons then kills=kills+1 end
end,emu.callbackType.exec,L.ShellOrBlockDefeat)
emu.addMemoryCallback(function()
 if not entered or phase~='attack'or emu.convertAddress(L.KbBodyContact).address//8192~=B.KbBodyContact then return end
 local x=emu.getState()['cpu.x']
 if x==0 and r('Enemy_ID')==6 and r('KbCopy')==4 and r('KbAction')==4 then guardContacts=guardContacts+1 end
end,emu.callbackType.exec,L.KbBodyContact)
emu.addEventCallback(function()
 if not entered then emu.setInput(menu(),0);return end
 local b={}
 if phase=='inhale'then b.b=tick>=8
 elseif phase=='swallow'or phase=='reswallow'then b.down=tick>=1 and tick<6
 elseif phase=='attack'then b.b=tick>=4 and tick<35
 elseif phase=='drop'or phase=='expire'then b.select=tick>=1 and tick<5
 elseif phase=='reclaim'then b.b=tick>=2 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
local function finish()
 out:close();local f=assert(io.open(OUTPUT..'copy-result.json','w'));f:write('{"passed":true,"powers":[')
 for i,v in ipairs(results)do
  if i>1 then f:write(',')end
  f:write('{"power":'..v.power..',"enemy":'..v.enemy..',"mouthFrame":'..v.mouthFrame..',"copyFrame":'..v.copyFrame..',"attackFrame":'..v.attackFrame..',"kills":'..v.kills..',"guardContacts":'..v.guardContacts..',"recovered":true,"expired":true}')
 end
 f:write(']}\n');f:close();print('PASS all14 Kirby copied families, controller attacks, Select discard, re-inhale/recovery and expiry');emu.stop(0)
end
emu.addEventCallback(function()
 frame=frame+1;assert(frame<18000,'Kirby copy deadline case '..stage..' phase '..phase..' tick '..tick)
 if not entered then
  if r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 then
   assert(r('SelectedCharacter')==13 and r('KbVariant')==0 and r('CrossoverBehaviorVersion')==(C.hard and 1 or 0),'Actual Kirby identity/mode');entered=true
  end
  return
 end
 boot=boot+1;if boot<30 then return end
 if boot==30 then pending=startCase;setPhase('setup')end
 tick=tick+1;local c=C.copies[stage]
 COPY_CASE=stage;COPY_PHASE=phase;COPY_TICK=tick
 out:write(table.concat({frame,stage,phase,tick,c.power,r('Player_X_Position'),r('Player_Y_Position'),r('KbHealth'),r('KbCopy'),r('KbMouth'),r('KbAction'),r('KbActionAge'),r('Enemy_Flag'),r('Enemy_Y_Position'),r('KbDropKind'),r('KbDropAge'),r('KbShotKind'),r('KbShotKind',1),r('KbShotKind',2),kills,guardContacts},',')..'\n')
 assert(r('KbHealth')==6 and r('MmDeathFlag')==0,'Copy lifecycle does not injure/kill Kirby')
 if phase=='inhale'then
  if r('Enemy_Flag')~=0 then assert(r('Enemy_Y_Position')<=184,'Suction never buries the declared ground-aligned target')end
  if r('KbMouth')~=0 then
   assert(r('KbMouth')==c.enemy+1 and r('KbMouthCopy')==c.power and r('Enemy_Flag')==0 and r('KbCopy')==0,'Native inhaled family retained; copy waits for Down')
   mouthFrame=frame;results[stage].mouthFrame=frame;setPhase('swallow')
  end
  assert(tick<170,'Frozen source-family actor can be inhaled')
 elseif phase=='swallow'then
  if r('KbCopy')~=0 and copyFrame==0 then assert(r('KbCopy')==c.power and r('KbMouth')==0,'Down grants actual held family');copyFrame=frame;results[stage].copyFrame=frame end
  if tick>=40 then
   assert(copyFrame>mouthFrame,'Native swallow completed')
   pending=function()
    w('AvStopwatch',0);w('Enemy_Flag',0)
    if c.power==10 then w('Player_Y_Position',128);w('Player_State',2);w('Player_Y_Speed',1);w('MmVY',1,2);startY=128;minY=128;maxY=128 end
    setPhase('attack')
   end
   setPhase('setup')
  end
 elseif phase=='attack'then
  if r('KbAction')==4 then
   if not attackSeen then attackSeen=true;results[stage].attackFrame=frame end
   if not spawned and c.power~=10 then
    spawned=true
    pending=function()
     local x=r('Player_X_Position')+16
     if c.power==1 or c.power==14 then x=r('Player_X_Position')+32 end
     if c.power==4 or c.power==9 then x=r('Player_X_Position')+4 end
     actor(6,x,184)
    end
   end
   if c.power==10 and tick>=8 and tick<30 then minY=math.min(minY,r('Player_Y_Position'));maxY=math.max(maxY,r('Player_Y_Position'));assert(maxY-minY<=3,'Cloud hover limits vertical drift while B is held')end
  end
  if c.power==4 and tick>=28 and not guardProtected then
   assert(guardContacts>0 and r('Enemy_Flag')~=0 and r('KbHealth')==6,'Held Beetle guard protects actual overlapping contact')
   guardProtected=true;pending=function()w('Enemy_Flag',0)end
  end
  if tick>=85 then
   assert(attackSeen,'Actual B invokes copied ability')
   if c.power==4 then assert(guardProtected,'Beetle guard completed before its release')
   elseif c.power~=10 then assert(kills>0,'Copied ability defeats actual unfrozen Goomba power '..c.power)end
   results[stage].kills=kills;results[stage].guardContacts=guardContacts
   pending=function()w('Enemy_Flag',0)end;setPhase('drop')
  end
 elseif phase=='drop'then
  if tick>=8 then assert(r('KbCopy')==0 and r('KbDropKind')==c.power,'Select discards an actual owned copy into its world star')end
  if tick>=14 then dropFrame=frame;setPhase('reclaim')end
 elseif phase=='reclaim'then
  if r('KbMouth')~=0 then
   assert(r('KbMouth')==255 and r('KbMouthCopy')==c.power and r('KbDropKind')==0 and r('KbCopy')==0,'World copy star can be re-inhaled without auto-grant')
   orbFrame=frame;setPhase('reswallow')
  end
  assert(tick<130,'Discarded star remains reachable by ordinary inhale')
 elseif phase=='reswallow'then
  if tick>=32 then assert(r('KbCopy')==c.power and r('KbMouth')==0,'Down restores re-inhaled copy');recovered=true;setPhase('expire')end
 elseif phase=='expire'then
  if tick==10 then assert(r('KbCopy')==0 and r('KbDropKind')==c.power,'Second Select discards recovered ability')end
  if tick>=280 then
   assert(recovered and r('KbDropKind')==0 and r('KbCopy')==0 and r('KbMouth')==0,'Native dropped copy expires without free equipment')
   stage=stage+1;if stage>#C.copies then finish();return end
   setPhase('setup');pending=startCase
  end
 end
end,emu.eventType.endFrame)
