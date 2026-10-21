-- AV Laser/Flare differential fixture, frozen v1 against optimization.
-- The original native-gun boundary cases are reused with converted projectiles.
-- This injects RAM deliberately; it is not a level-completion replay.
local frame,index=0,0
local cases={}
for power=0,2 do for dir=1,2 do for x=0,15 do for y=0,15 do
 cases[#cases+1]={power=power,dir=dir,x=112+x,y=160+y,corner=(x+y)%4,tile=({0x51,0x52,0x54,0xc0,0x23})[(x*3+y)%5+1],terrain=(x+y)%2}
end end end end
for power=0,2 do for dir=1,2 do for _,x in ipairs({0,1,2,3,253,254,255}) do for _,y in ipairs({32,33,34,35,237,238,239}) do
 cases[#cases+1]={power=power,dir=dir,x=x,y=y,corner=(x+y)%4,tile=0x51,terrain=0}
end end end end
for power=0,2 do for _,ey in ipairs({0,7,8,16,24,31,32,100,200,208,220,231,232,239,240,248,255}) do
 for _,delta in ipairs({-4,-3,-2,-1,0,1,15,16,17,18,19,20,21}) do
  local by=(ey+8+delta)%256
  if by>=32 and by<240 then cases[#cases+1]={power=power,dir=1,x=100,y=by,enemyY=ey} end
 end
end end
for _,id in ipairs({0,6,0x15,0x2e}) do for _,state in ipairs({0,2,0x20}) do for _,offscreen in ipairs({0,1}) do
 cases[#cases+1]={power=2,dir=1,x=100,y=194,enemyY=180,enemyID=id,enemyState=state,offscreen=offscreen}
end end end
for power=0,2 do for count=0,10 do cases[#cases+1]={power=power,spawn=count} end end
for _,enemies in ipairs({0,1,6}) do for _,count in ipairs({5,10}) do for phase=0,31 do
 cases[#cases+1]={power=2,perf=count,enemies=enemies,phase=phase}
end end end
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug) end
local log=assert(io.open(OUTPUT..ROM_NAME..'-bill-av-collision-equivalence.csv','w'))
log:write('case,impact,tile,health,coin,powerup,playerX,playerY,enemyHP,enemyState,enemyFlag,shots\n')
local perf=assert(io.open(OUTPUT..ROM_NAME..'-bill-av-fixed-performance.csv','w'))
perf:write('case,enemies,shots,cycles,elapsedCycles,interrupted\n')
local interrupts,entryInterrupt,entryCycle=0,0,0
local interruptCycles,interruptDepth,interruptStart,entryInterruptCycles=0,0,0,0
for _,pc in ipairs({L.NonMaskableInterrupt,L.IrqScrollSplit}) do
 emu.addMemoryCallback(function()
  interrupts=interrupts+1
  if interruptDepth==0 then interruptStart=emu.getState()['cpu.cycleCount']-7 end
  interruptDepth=interruptDepth+1
 end,emu.callbackType.exec,pc)
end
for _,pc in ipairs({L.NonMaskableInterrupt_RTI,L.IrqScrollSplit_RTI}) do
 emu.addMemoryCallback(function()
  interruptDepth=interruptDepth-1
  assert(interruptDepth>=0,'Balanced interrupt timing')
  if interruptDepth==0 then interruptCycles=interruptCycles+emu.getState()['cpu.cycleCount']+6-interruptStart end
 end,emu.callbackType.exec,pc)
end
local current,target,entrySp,returnPc
local function resetShot(slot)
 for _,n in ipairs({'RgShotType','RgShotImpact','RgShotAge','RgShotVXLo','RgShotVXHi','RgShotVYLo','RgShotVYHi','RgShotFracX','RgShotFracY','RgShotHits'}) do w(n,0,slot) end
 w('RgShotX',100,slot);w('RgShotPage',0,slot);w('RgShotY',100,slot);w('RgShotYHigh',1,slot);w('RgShotDir',1,slot)
end
emu.addMemoryCallback(function()
 if frame<550 or interruptDepth~=0 or r('CurrentBank')%128~=6 then return end
 assert(emu.read(L.NonMaskableInterrupt_RTI,emu.memType.nesDebug)==0x40 and emu.read(L.IrqScrollSplit_RTI,emu.memType.nesDebug)==0x40,'Mapped interrupt scopes end in RTI')
 index=index+1;current=cases[index]
 if not current then
  log:close();perf:close();print('PASS Bill AV differential fixture: '..#cases..' boundary, terrain, reward, shot-pool and fixed-load cases');emu.stop(0);return
 end
 assert(r('SelectedCharacter')==3,'Bill selected')
 w('TimerControl',0);w('GameEngineSubroutine',8);w('Player_State',0);w('PlayerStatus',current.power)
 w('Player_X_Position',72);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
 w('PlayerFacingDir',1);w('PlayerSize',0);w('CrouchingFlag',0);w('Player_Y_Speed',0)
 w('SavedJoypadBits',0);w('A_B_Buttons',0);w('PreviousA_B_Buttons',0);w('RgPreviousButtons',0)
 w('RgCooldown',0);w('RgAttack',0);w('RgShootPose',0);w('RgSfx',0);w('RgCrouch',0)
 w('InvOwnedLo',1,3);w('InvOwnedHi',0,3);w('InvSelected',0,3)
 w('CoinTallyFor1Ups',0);w('BlockBounceTimer',0);w('SprDataOffset_Ctrl',0)
 w('Square1SoundQueue',0);w('Square2SoundQueue',0);w('NoiseSoundQueue',0)
 for i=0,5 do w('Enemy_Flag',0,i);w('Enemy_State',0,i);w('MmEnemyHealthLo',0,i);w('MmEnemyHealthHi',0,i) end
 for i=0,1 do w('Block_State',0,i);w('Block_RepFlag',0,i) end
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i);w('MmBrickHealth',0,i);w('MmCoinHits',0,i) end
 for i=0,9 do resetShot(i) end
 target=nil
 if current.perf then
  for i=0,current.perf-1 do
   w('RgShotType',43,i);w('RgShotX',96+(current.phase%16)+i*7,i)
   w('RgShotY',128+(current.phase%16)+i%5,i);w('RgShotVXHi',3,i);w('RgShotVXLo',85,i)
  end
  for i=0,current.enemies-1 do
   w('Enemy_Flag',1,i);w('Enemy_ID',6,i);w('Enemy_State',0,i);w('EnemyOffscrBitsMasked',0,i)
   w('Enemy_X_Position',120+i*18,i);w('Enemy_PageLoc',0,i);w('Enemy_Y_Position',208,i);w('Enemy_Y_HighPos',1,i);w('MmEnemyHealthLo',100,i)
  end
 elseif current.spawn then
  for i=0,current.spawn-1 do w('RgShotType',(current.power==0 and 42 or 43),i);w('RgShotImpact',2,i) end
  w('A_B_Buttons',0x40);w('SavedJoypadBits',0x40)
 elseif current.enemyY then
  w('RgShotType',(current.power==0 and 42 or 43));w('RgShotX',current.x);w('RgShotY',current.y);w('RgShotDir',current.dir)
  w('Enemy_Flag',1);w('Enemy_ID',current.enemyID or 6);w('Enemy_State',current.enemyState or 0)
  w('EnemyOffscrBitsMasked',current.offscreen or 0);w('Enemy_X_Position',90);w('Enemy_PageLoc',0)
  w('Enemy_Y_Position',current.enemyY);w('Enemy_Y_HighPos',1);w('MmEnemyHealthLo',40)
 else
  w('RgShotType',(current.power==0 and 42 or 43));w('RgShotX',current.x);w('RgShotY',current.y);w('RgShotDir',current.dir)
  local radius=current.power==0 and 2 or 3
  local dx=current.corner%2==0 and radius or -radius
  if current.dir~=1 then dx=-dx end
  local px=(current.x+dx)%512
  local py=current.y+(current.corner<2 and -radius or radius)
  if py>=32 and py<240 then
   target=math.floor(px/256)*208+math.floor(px%256/16)+math.floor(py/16)*16-32
   w('Block_Buffer_1',current.tile,target);w('MmSolidTerrain',current.terrain,target)
  end
 end
 entrySp=emu.getState()['cpu.sp']
 entryCycle=emu.getState()['cpu.cycleCount'];entryInterrupt=interrupts;entryInterruptCycles=interruptCycles
 local pc=emu.read(0x100+(entrySp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(entrySp+2)%256,emu.memType.nesDebug)+1
 if not returnPc then
  returnPc=pc
  emu.addMemoryCallback(function()
   if not current or interruptDepth~=0 or r('CurrentBank')%128~=6 or emu.getState()['cpu.sp']~=entrySp+2 then return end
   local shots={}
   for i=0,9 do
    local fields={}
    for _,n in ipairs({'RgShotType','RgShotX','RgShotPage','RgShotY','RgShotDir','RgShotVXLo','RgShotVXHi','RgShotVYLo','RgShotVYHi','RgShotImpact','RgShotFracX','RgShotFracY'}) do fields[#fields+1]=r(n,i) end
    shots[#shots+1]=table.concat(fields,':')
   end
   log:write(table.concat({index,r('RgShotImpact'),target and r('Block_Buffer_1',target) or -1,target and r('MmBrickHealth',target) or -1,r('CoinTallyFor1Ups'),r('Enemy_Flag',5),r('Player_X_Position'),r('Player_Y_Position'),r('MmEnemyHealthLo'),r('Enemy_State'),r('Enemy_Flag'),table.concat(shots,';')},',')..'\n')
   if current.perf then
    local elapsed=emu.getState()['cpu.cycleCount']-entryCycle
    perf:write(table.concat({index,current.enemies,current.perf,elapsed-(interruptCycles-entryInterruptCycles),elapsed,interrupts~=entryInterrupt and 1 or 0},',')..'\n')
   end
   current=nil
  end,emu.callbackType.exec,pc)
 end
 assert(pc==returnPc,'Stable weapon caller')
end,emu.callbackType.exec,L.RemainingWeapons)
emu.addEventCallback(function()
 emu.setInput({right=frame==80 or frame==100 or frame==120,start=frame==200},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function() frame=frame+1 end,emu.eventType.endFrame)
