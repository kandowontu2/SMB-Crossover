-- Equal-workload CPU profiling with explicit RAM arenas. These samples do
-- not represent controller-only traversal or alter any claimed clear.
local frame,index=0,0
local cases={}
for _,tile in ipairs({0,0x51,0x52,0x54,0xc0,0xc1,0xc2,0xc4})do
 for x=0,15 do for y=0,15 do for terrain=0,1 do
  cases[#cases+1]={name='bombs',c=2,enemies=0,phase=x+y,x=112+x,y=144+y,tile=tile,terrain=terrain,target='SamusWeapons',bank=10}
 end end end
end
for _,x in ipairs({0,1,15,16,239,240,254,255})do for _,y in ipairs({0,15,16,31,32,33,223,224,239,240,255})do
 cases[#cases+1]={name='bombs',c=2,enemies=0,phase=x+y,x=x,y=y,tile=0xc0,terrain=0,target='SamusWeapons',bank=10}
end end
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function cycles()return emu.getState()['cpu.cycleCount']end
local log=assert(io.open(OUTPUT..ROM_NAME..'-samus-bomb-block-equivalence.csv','w'))
log:write('case,terrain,player,bomb,rewards,blocks,health,coins\n')
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
 for dx=-16,16,16 do for dy=-16,16,16 do
  local x=(c.x+dx)%512;local y=(c.y+dy)%256
  if y>=32 and y<240 then
   local cell=math.floor(x/256)*208+math.floor(x%256/16)+math.floor((y-32)/16)*16
   w('Block_Buffer_1',c.tile,cell);w('MmSolidTerrain',c.terrain,cell)
  end
 end end
 for i=0,415 do w('MmCoinHits',0,i)end
 for i=0,1 do w('Block_State',0,i);w('Block_RepFlag',0,i)end
 w('CoinTallyFor1Ups',0);w('BlockBounceTimer',0);w('SprDataOffset_Ctrl',0)
 w('Square1SoundQueue',0);w('Square2SoundQueue',0);w('NoiseSoundQueue',0)
 w('VRAM_Buffer1_Offset',0);w('VRAM_Buffer2_Offset',0);w('VRAM_Buffer_AddrCtrl',0)
 if c.c==2 then
  w('InvOwnedLo',255,2);w('InvOwnedHi',0,2);w('InvSelected',0,2)
  if c.name=='bombs'or c.name=='wave+bombs'then for i=0,2 do
   w('SmBombAge',i==0 and 57 or 0,i);w('SmBombX',c.x,i);w('SmBombPage',0,i);w('SmBombY',c.y,i);w('SmBombHits',0,i);w('SmBombBoosted',1,i);w('SmBombBlocksDone',0,i)
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
local sfx={}
for _,name in ipairs({'Square1SoundQueue','Square2SoundQueue','NoiseSoundQueue'})do
 emu.addMemoryCallback(function(address,value)if pending and irqDepth==0 and value>0 then sfx[#sfx+1]=name..':'..value end end,emu.callbackType.write,L[name])
end
local returns={}
local function entry(name,bank)
 if frame<550 or irqDepth~=0 or r('CurrentBank')%128~=bank or pending then return end
 local c=cases[index+1]
 if not c then log:close();print('PASS fixed Samus bomb terrain differential fixture: '..index..' equal-workload samples, IRQ/NMI excluded');emu.stop(0);return end
 if c.target~=name then return end
 index=index+1;sfx={};setup(c);pending=c;started=cycles();startedIrq=irqCycles;sp=emu.getState()['cpu.sp']
 local pc=emu.read(0x100+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+1
 local key=name..'/'..pc
 if not returns[key]then
  returns[key]=true
  emu.addMemoryCallback(function()
   if not pending or irqDepth~=0 or pending.target~=name or r('CurrentBank')%128~=bank or emu.getState()['cpu.sp']~=sp+2 then return end
   local d=cycles()-started
   local function array(n,count)local t={};for i=0,count-1 do t[#t+1]=string.format('%02x',r(n,i))end;return table.concat(t)end
   local player=table.concat({r('Player_X_Position'),r('Player_PageLoc'),r('Player_Y_Position'),r('Player_Y_HighPos'),r('Player_State'),r('Player_Y_Speed')},':')
   local bomb=table.concat({r('SmBombAge'),r('SmBombX'),r('SmBombPage'),r('SmBombY'),r('SmBombBlocksDone')},':')
   local rewards=table.concat({r('CoinTallyFor1Ups'),r('Enemy_Flag',5),r('Enemy_ID',5),r('PowerUpType',5),r('Block_State'),r('Block_State',1),table.concat(sfx,';')},':')
   log:write(table.concat({index,pending.terrain,player,bomb,rewards,array('Block_Buffer_1',416),array('MmBrickHealth',416),array('MmCoinHits',416)},',')..'\n');pending=nil
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
 if frame>=550 and not pending and cases[index+1]then
  w('SelectedCharacter',2);w('GameEngineSubroutine',8);w('TimerControl',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('Player_X_Position',40)
 end
 assert(frame<12000 and(not pending or cycles()-started<2000000),'Bomb oracle progress index='..index..' pending='..tostring(pending~=nil)..' bank='..r('CurrentBank')..' sp='..emu.getState()['cpu.sp']..' expected='..tostring(sp)..' engine='..r('GameEngineSubroutine')..' pc='..tostring(emu.getState()['cpu.pc']))
end,emu.eventType.endFrame)

