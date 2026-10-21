-- Equal-workload CPU profiling with explicit RAM arenas. These samples do
-- not represent controller-only traversal or alter any claimed clear.
local frame,index=0,0
local cases={}
for _,enemies in ipairs({0,6})do for phase=0,31 do cases[#cases+1]={name='bombs',c=2,enemies=enemies,phase=phase,target='SamusWeapons',bank=10}end end
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function cycles()return emu.getState()['cpu.cycleCount']end
local log=assert(io.open(OUTPUT..ROM_NAME..'-samus-bomb-initial-performance.csv','w'))
log:write('case,character,variant,weapon,rapid,enemies,phase,cycles,elapsed\n')
local irqDepth,irqStart,irqCycles=0,0,0
for _,pc in ipairs({L.NonMaskableInterrupt,L.IrqScrollSplit})do emu.addMemoryCallback(function()
 if irqDepth==0 then irqStart=cycles()-7 end;irqDepth=irqDepth+1
end,emu.callbackType.exec,pc)end
for _,pc in ipairs({L.NonMaskableInterrupt_RTI,L.IrqScrollSplit_RTI})do emu.addMemoryCallback(function()
 irqDepth=irqDepth-1;assert(irqDepth>=0,'Interrupt scopes balance')
 if irqDepth==0 then irqCycles=irqCycles+cycles()+6-irqStart end
end,emu.callbackType.exec,pc)end
local function setup(c)
 w('SelectedCharacter',c.c);w('BillVariant',c.variant or 0)
 w('TimerControl',0);w('GameEngineSubroutine',8);w('PlayerStatus',1)
 w('Player_X_Position',40);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('PlayerFacingDir',1)
 w('SavedJoypadBits',0);w('A_B_Buttons',0);w('PreviousA_B_Buttons',0);w('RgPreviousButtons',0);w('RgCooldown',0)
 w('SmBall',0);w('SmCrouch',0);w('SmFlip',0);w('MmDeathFlag',0)
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i);w('MmBrickHealth',0,i)end
 for i=0,5 do
  w('Enemy_Flag',i<c.enemies and 1 or 0,i);w('Enemy_ID',6,i);w('Enemy_State',0,i);w('EnemyOffscrBitsMasked',0,i)
  w('Enemy_X_Position',96+i*18,i);w('Enemy_PageLoc',0,i);w('Enemy_Y_Position',208,i);w('Enemy_Y_HighPos',1,i)
  w('MmEnemyHealthLo',100,i);w('MmEnemyHealthHi',0,i)
 end
 for i=0,9 do
  for _,n in ipairs({'RgShotType','RgShotImpact','RgShotAge','RgShotVXLo','RgShotVXHi','RgShotVYLo','RgShotVYHi','RgShotFracX','RgShotFracY','RgShotHits','SsMode','SsAngleLo','SsAngleHi','SsHidden','SsHitTimer'})do w(n,0,i)end
  w('RgShotX',96+c.phase%16+i*7,i);w('RgShotPage',0,i);w('RgShotY',128+c.phase%16+i%5,i);w('RgShotYHigh',1,i);w('RgShotDir',1,i)
 end
 for i=0,2 do
  w('SmShotType',0,i);w('SmBombAge',0,i);w('SmShotImpact',0,i);w('SmShotAge',0,i);w('SmShotFraction',0,i);w('SmShotPolarity',i%2,i)
  w('SmShotX',96+c.phase%16+i*36,i);w('SmShotPage',0,i);w('SmShotY',128+c.phase%16,i);w('SmShotCenter',128+c.phase%16,i);w('SmShotDir',1,i)
 end
 if c.c==2 then
  w('InvOwnedLo',255,2);w('InvOwnedHi',0,2);w('InvSelected',0,2)
  if c.name=='bombs'or c.name=='wave+bombs'then for i=0,2 do
   w('SmBombAge',69+c.phase%3,i);w('SmBombX',96+i*48,i);w('SmBombPage',0,i);w('SmBombY',128,i);w('SmBombHits',0,i);w('SmBombBoosted',1,i);w('SmBombBlocksDone',0,i)
  end end
  local kind=({short=1,long=2,wave=3,['wave+bombs']=3})[c.name]
  if kind then for i=0,2 do w('SmShotType',kind,i)end end
  if c.name=='ice'or c.name=='missile'then for i=0,2 do w('RgShotType',c.name=='ice'and 46 or 41,i);w('RgShotVXHi',4,i);w('RgShotVXLo',43,i)end end
 else
  local owned=1+(c.gun~=0 and(1<<c.gun)or 0)+(c.rapid==1 and 2 or c.rapid==2 and 64 or 0)
  w('InvOwnedLo',owned,3);w('InvOwnedHi',0,3);w('InvSelected',c.gun,3)
  local kind=({[0]=1,[4]=2,[5]=3,[2]=42,[3]=43})[c.gun]
  local count=({[0]=4,[4]=6,[5]=10,[2]=4,[3]=6})[c.gun]
  for i=0,count-1 do
   w('RgShotType',kind,i);w('RgShotVXHi',3,i);w('RgShotVXLo',85,i)
   if kind==43 then w('SsAngleLo',r('RgShotX',i),i);w('SsHidden',r('RgShotY',i),i)end
  end
  w('RgEnemiesPresent',c.enemies>0 and 1 or 0)
 end
end
local pending,started,startedIrq,sp
local returns={}
local function entry(name,bank)
 if frame<550 or r('CurrentBank')%128~=bank or pending then return end
 local c=cases[index+1]
 if not c then log:close();print('PASS fixed Samus initial bomb-burst CPU profile: '..index..' equal-workload samples, IRQ/NMI excluded');emu.stop(0);return end
 if c.target~=name then return end
 index=index+1;setup(c);pending=c;started=cycles();startedIrq=irqCycles;sp=emu.getState()['cpu.sp']
 local pc=emu.read(0x100+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+1
 local key=name..'/'..pc
 if not returns[key]then
  returns[key]=true
  emu.addMemoryCallback(function()
   if not pending or pending.target~=name or r('CurrentBank')%128~=bank or emu.getState()['cpu.sp']~=sp+2 then return end
   local d=cycles()-started
   local exclusive=d-(irqCycles-startedIrq)
   assert(exclusive<=(pending.enemies==0 and 12500 or 14000),'Maximum three-bomb initial burst stays below the exclusive CPU budget: '..exclusive)
   log:write(table.concat({index,pending.c,pending.variant or 0,pending.name,pending.rapid or 0,pending.enemies,pending.phase,d-(irqCycles-startedIrq),d},',')..'\n');pending=nil
  end,emu.callbackType.exec,pc)
 end
end
for _,v in ipairs({{'SamusWeapons',10},{'RosterWeapons',8},{'RemainingWeapons',6}})do
 local name,bank=v[1],v[2]
 emu.addMemoryCallback(function()entry(name,bank)end,emu.callbackType.exec,assert(L[name],name))
end
emu.addEventCallback(function()emu.setInput({right=frame==80 or frame==100,start=frame==200},0)end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=550 and not pending and cases[index+1]then w('SelectedCharacter',cases[index+1].c)end
 assert(frame<12000,'All fixed CPU profile cases complete')
end,emu.eventType.endFrame)
