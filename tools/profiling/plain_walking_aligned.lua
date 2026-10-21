-- Aligned unit arena: seed only at actual foreground loop entry after two
-- stable real controller receipts; initialize inactive boxes too. All204
-- gameplay fields and60 measured updates remain; no CPU/register/PC writes.
-- Authored flat/crowd benchmark, not a gameplay route. Real Right or neutral
-- drives normal movement. No attacks, program-counter/ROM/register changes.
local char=assert(PROFILE_CHARACTER)
local prefix=assert(PROFILE_OUTPUT)
local metricsOnly=PROFILE_METRICS_ONLY or false
local frame,depth,irqCycles,nmis,interruptStart=0,0,0,0,nil
local scene,index,completed,needSetup=nil,0,0,false
local setup,pendingPolls=nil,0
local loopStart,loopIrq=nil,0
local routineActive,returns,totals={},{},{}
local owner,activeActor,dmaOwner={},nil,{}
local tileRows={}
local scenes={}
for _,outline in ipairs({0,1})do for _,mode in ipairs({'stand','walk'})do for _,count in ipairs({0,1,2,4,6})do
 scenes[#scenes+1]={outline=outline,mode=mode,count=count}
end end end
local samples=assert(io.open(prefix..'-updates.csv','w'))
samples:write('scene,character,outlinesOff,mode,enemies,update,hardwareFrame,cycles,foregroundCycles,interruptCycles\n')
local routines=assert(io.open(prefix..'-routines.csv','w'))
routines:write('scene,character,outlinesOff,mode,enemies,routine,calls,totalCycles,totalForegroundCycles,maxForegroundCycles\n')
local results=assert(io.open(prefix..'-scenes.csv','w'))
results:write('scene,character,outlinesOff,mode,enemies,updates,physicalFrames,skippedNmis,meanCycles,maxCycles,meanForegroundCycles,drawnEnemyFrames,visibleEnemyFrames,fullyInvisibleEnemyFrames,overloadRowsTotal,maxOverloadRows,meanVisibleSprites,physicalDmas,drawCalls,skippedRenders\n')
-- Completed-update behavior receipts are independent of renderer/DMA cadence.
-- They bind before/after hot-path changes to actual player, AI and contact state.
local canonical=assert(io.open(prefix..'-canonical.csv','w'))
local fields={}
local function field(n,count)for i=0,(count or 1)-1 do fields[#fields+1]={n,i}end end
for _,n in ipairs({'Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_X_Speed','Player_Y_Speed','Player_X_MoveForce','Player_Y_MoveForce','Player_State','PlayerFacingDir','Player_CollisionBits','CrouchingFlag','PlayerStatus','PlayerSize','InjuryTimer','TimerControl','GameEngineSubroutine','AvStopwatch','RgAttack','RgThrust','SmBall','SmCrouch','MmSliding','AvSlash','XgWall'})do field(n)end
for _,n in ipairs({'Enemy_Flag','Enemy_ID','Enemy_State','Enemy_PageLoc','Enemy_X_Position','Enemy_Y_Position','Enemy_Y_HighPos','Enemy_X_Speed','Enemy_Y_Speed','Enemy_X_MoveForce','Enemy_Y_MoveForce','Enemy_MovingDir','Enemy_CollisionBits','Enemy_BoundBoxCtrl','EnemyOffscrBitsMasked','EnemyIntervalTimer','RgEnemyStun','MmEnemyFlash','AvFrozen','AvFrozenHi'})do field(n,6)end
field('EnemyFrameTimer',5);field('EnemyBoundingBoxCoord',24);field('MmVX',3);field('MmVY',3);field('MmXFraction',2);field('MmYFraction',2);field('RgShotType',10);field('MmBulletType',4);field('SmShotType',3);field('SmBombAge',3)
canonical:write('scene,update');for _,f in ipairs(fields)do canonical:write(','..f[1]..'+'..f[2])end;canonical:write('\n')
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function cycles()return emu.getState()['cpu.cycleCount']end
local function inBank(b)return depth==0 and r('CurrentBank')%128==b end
local function observed()return scene and completed>=8 and completed<68 end
for _,pc in ipairs({assert(L.NonMaskableInterrupt),assert(L.IrqScrollSplit)})do emu.addMemoryCallback(function()
 if depth==0 then interruptStart=cycles()-7 end
 depth=depth+1
 if pc==L.NonMaskableInterrupt then
  nmis=nmis+1
  if observed()and r('NmiDisable')>=128 then scene.skipped=scene.skipped+1 end
 end
end,emu.callbackType.exec,pc)end
for _,pc in ipairs({assert(L.NonMaskableInterrupt_RTI),assert(L.IrqScrollSplit_RTI)})do emu.addMemoryCallback(function()
 depth=depth-1;assert(depth>=0,'Balanced benchmark interrupts')
 if depth==0 then irqCycles=irqCycles+cycles()+6-assert(interruptStart);interruptStart=nil end
end,emu.callbackType.exec,pc)end
local function captureRoutine(name,bank)
 if metricsOnly and name~='DrawAllMetasprites'then return end
 local pc=L[name];if not pc then return end
 emu.addMemoryCallback(function()
  if not observed()or not inBank(bank)then return end
  if name=='DrawAllMetasprites'then scene.drawCalls=scene.drawCalls+1 end
  local cpu=emu.getState();local sp=cpu['cpu.sp']
  local ret=(emu.read(0x100+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+1)%65536
  assert(not routineActive[name],'Profile routine is not recursively entered: '..name)
  routineActive[name]={clock=cpu['cpu.cycleCount'],irq=irqCycles,sp=(sp+2)%256,ret=ret,bank=bank}
  if not returns[ret]then
   returns[ret]=true
   emu.addMemoryCallback(function()
    if depth~=0 then return end
    local c=cycles();local s=emu.getState()['cpu.sp']
    for n,a in pairs(routineActive)do if a.ret==ret and a.sp==s and r('CurrentBank')%128==a.bank then
     local inc=c-a.clock;local fg=inc-(irqCycles-a.irq)
     local t=totals[n]or{calls=0,total=0,foreground=0,max=0};totals[n]=t
     t.calls=t.calls+1;t.total=t.total+inc;t.foreground=t.foreground+fg;t.max=math.max(t.max,fg)
     routineActive[n]=nil
    end end
   end,emu.callbackType.exec,ret)
  end
 end,emu.callbackType.exec,pc)
end
for _,pair in ipairs({
 {'ProcFireball_Bubble',0},{'EnemiesAndLoopsCore',0},{'EnemyMovementSubs',0},
 {'EnemyGraphicsEngine',0},{'EnemiesCollision',0},{'PlayerEnemyCollision',0},
 {'EnemyToBGCollisionDet',0},{'OffscreenBoundsCheck',0},{'GetEnemyBoundBox',0},
 {'GetEnemyOffscreenBits',0},{'RelativeEnemyPosition',0},{'BoundingBoxCore',0},
 {'DrawAllMetasprites',4},{'DrawMetasprite',4},
 {'InventoryUpdateDrops',59},{'SpecialWeapons',60},{'RemainingWeapons',6},
 {'ExpandedWeapons',37},{'RosterWeapons',8},{'MegaManWeapons',8},{'SamusWeapons',10},
 {'GuestPrepareEnemies',8},{'RunEnemyObjectsCore',0},{'RunEnemyObjectsBody',0},
 {'RemainingEnemyFrozen',6},{'LsrEffectsBeforeEnemies',61},{'LsrEffectsAfterEnemies',61},
})do captureRoutine(pair[1],pair[2])end
emu.addMemoryCallback(function()
 if depth~=0 then return end
 if needSetup then
  if pendingPolls<2 then return end
  local nextScene=scenes[index+1]
  if nextScene then assert((r('SavedJoypadBits')&3)==(nextScene.mode=='walk'and 1 or 0),'Actual stable controller receipt before arena seed')end
  setup()
 end
 if not scene then return end
 local pc=L.NoDecTimers;local op=emu.read(pc,emu.memType.nesDebug)
 assert(op==0xe6 or op==0xee,'Actual foreground FrameCounter INC anchors the profile')
 assert(not loopStart,'One complete foreground loop per profile update')
 loopStart=cycles();loopIrq=irqCycles
end,emu.callbackType.exec,assert(L.NoDecTimers))
local function flush()
 for name,t in pairs(totals)do routines:write(table.concat({index,char,scene.outline,scene.mode,scene.count,name,t.calls,t.total,t.foreground,t.max},',')..'\n')end
 local expected=scene.count*scene.hardware
 assert(scene.drawn<=expected and scene.visible<=scene.drawn,'Hardware visibility counters stay bounded by authored population')
 results:write(table.concat({index,char,scene.outline,scene.mode,scene.count,60,scene.hardware,scene.skipped,scene.cycles/60,scene.maxCycles,scene.fg/60,metricsOnly and 'NA'or scene.drawn,metricsOnly and 'NA'or scene.visible,metricsOnly and 'NA'or(expected-scene.visible),metricsOnly and 'NA'or scene.overload,metricsOnly and 'NA'or scene.maxOverload,metricsOnly and 'NA'or(scene.sprites/math.max(scene.hardware,1)),scene.dmas,scene.drawCalls,60-scene.drawCalls},',')..'\n');results:flush();routines:flush();samples:flush();canonical:flush()
 print('PROFILE c'..char..' outlinesOff'..scene.outline..' '..scene.mode..' enemies'..scene.count..' cycles'..math.floor(scene.cycles/60)..' fg'..math.floor(scene.fg/60)..' skipped'..scene.skipped..' DMA'..scene.dmas..' draws'..scene.drawCalls..(metricsOnly and ' visibilityNotCaptured'or(' hidden'..(expected-scene.visible)..'/'..expected)))
end
local finalPc=assert(L.PauseSkip)+2
emu.addMemoryCallback(function()
 if depth~=0 or not loopStart then return end
 local op=emu.read(finalPc,emu.memType.nesDebug)
 assert(op==0x85 or op==0x8d,'Actual final NmiDisable store anchors completion')
 local inc=cycles()-loopStart;local fg=inc-(irqCycles-loopIrq)
 if observed()then
  local live=0;for i=0,5 do if r('Enemy_Flag',i)~=0 then assert(r('Enemy_ID',i)==6,'Only authored Goombas in crowd benchmark');live=live+1 end end;assert(live==scene.count,'Actual live population matches crowd benchmark: '..live..'/'..scene.count)
  assert(r('GameEngineSubroutine')==8 and r('TimerControl')==0 and r('InjuryTimer')==0,'Plain walking benchmark has no injury, powerup or scripted pause')
  scene.cycles=scene.cycles+inc;scene.fg=scene.fg+fg;scene.maxCycles=math.max(scene.maxCycles,inc)
  samples:write(table.concat({index,char,scene.outline,scene.mode,scene.count,completed-7,frame,inc,fg,irqCycles-loopIrq},',')..'\n')
  if not metricsOnly then canonical:write(index..','..(completed-7));for _,f in ipairs(fields)do canonical:write(','..r(f[1],f[2]))end;canonical:write('\n')end
 end
 completed=completed+1;loopStart=nil
 if completed==68 then flush();needSetup=true;pendingPolls=0 end
end,emu.callbackType.exec,finalPc)
if not metricsOnly then emu.addMemoryCallback(function()
 if inBank(4)then activeActor=emu.getState()['cpu.y']end
end,emu.callbackType.exec,assert(L.DrawMetasprite))
emu.addMemoryCallback(function(address,value)
 if depth~=0 or not scene or(address-L.Sprite_Tilenumber)%4~=0 then return end
 local slot=(address-L.Sprite_Tilenumber)//4
 local tile=value&254
 owner[slot]=inBank(4)and activeActor and activeActor>=1 and activeActor<=scene.count and(tile==0xa2 or tile==0xa4)and activeActor or 0
end,emu.callbackType.write,assert(L.Sprite_Tilenumber),L.Sprite_Tilenumber+255)
end
emu.addMemoryCallback(function()
 if observed()then scene.dmas=scene.dmas+1 end
 if not metricsOnly then dmaOwner={};for i=0,63 do dmaOwner[i]=owner[i]or 0 end end
end,emu.callbackType.write,0x4014)
local function chr(address,state)
 if state then return emu.read(state['mapper.chrBanks'..address//1024]*1024+address%1024,emu.memType.nesChrRom)end
 return emu.read(address,emu.memType.nesPpuDebug)
end
local function visibility()
 if metricsOnly then scene.hardware=scene.hardware+1;return end
 local sprites,drawn,minY,maxY={},0,240,-1
 local state=ROM_NAME:find('mmc5')and emu.getState()or nil
 for i=0,63 do
  local y=emu.read(i*4,emu.memType.nesSpriteRam)+1
  local x=emu.read(i*4+3,emu.memType.nesSpriteRam)
  if y<240 and x<255 then
   local tile=emu.read(i*4+1,emu.memType.nesSpriteRam)
   local a=emu.read(i*4+2,emu.memType.nesSpriteRam)
   local own=dmaOwner[i]or 0
   if(tile&254)~=0xa2 and(tile&254)~=0xa4 then own=0 end
   sprites[#sprites+1]={x=x,y=y,t=tile,a=a,owner=own}
   if own>0 then drawn=drawn|(1<<(own-1));minY=math.min(minY,y);maxY=math.max(maxY,math.min(y+15,239))end
  end
 end
 local visible,overload=0,0
 for row=minY,maxY do
  local n=0
  for _,s in ipairs(sprites)do if row>=s.y and row<s.y+16 then
   n=n+1
   if n<=8 and s.owner>0 then
    local dy=s.a&128~=0 and 15-(row-s.y)or row-s.y
    local key=s.t*16+dy
    if tileRows[key]==nil then
     local addr=(s.t&1)*4096+(s.t&254)*16+(dy//8)*16+dy%8
     tileRows[key]=(chr(addr,state)|chr(addr+8,state))~=0
    end
    if tileRows[key]then visible=visible|(1<<(s.owner-1))end
   end
  end end
  if n>8 then overload=overload+1 end
 end
 local function bits(v)local n=0;while v>0 do n=n+(v&1);v=v>>1 end;return n end
 scene.hardware=scene.hardware+1;scene.drawn=scene.drawn+bits(drawn);scene.visible=scene.visible+bits(visible)
 scene.overload=scene.overload+overload;scene.maxOverload=math.max(scene.maxOverload,overload);scene.sprites=scene.sprites+#sprites
end
setup=function()
 index=index+1;scene=scenes[index]
 if not scene then samples:close();routines:close();results:close();canonical:close();print('PASS all20 standing/walking crowd benchmarks c'..char);emu.stop(0);return end
 assert(r('SelectedCharacter')==char,'Real menu launches benchmark character')
 for k,v in pairs({cycles=0,fg=0,maxCycles=0,hardware=0,skipped=0,drawn=0,visible=0,overload=0,maxOverload=0,sprites=0,dmas=0,drawCalls=0})do scene[k]=v end
 completed=0;needSetup=false;totals={};routineActive={};tileRows={};owner={};dmaOwner={};activeActor=nil
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for p=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,p*208+176+col)end end
 for i=0,5 do
  w('Enemy_Flag',i<scene.count and 1 or 0,i);w('Enemy_ID',6,i);w('Enemy_State',0,i);w('Enemy_BoundBoxCtrl',9,i)
  w('Enemy_PageLoc',1,i);w('Enemy_X_Position',88+24*i,i);w('Enemy_Y_Position',184,i);w('Enemy_Y_HighPos',1,i)
  w('Enemy_X_Speed',8,i);w('Enemy_Y_Speed',0,i);w('EnemyOffscrBitsMasked',0,i);w('Enemy_MovingDir',1,i);w('Enemy_X_MoveForce',0,i)
  w('Enemy_Y_MoveForce',0,i);w('EnemyIntervalTimer',0,i);if i<5 then w('EnemyFrameTimer',0,i)end
  w('RgEnemyStun',0,i);w('MmEnemyFlash',0,i);w('AvFrozen',0,i);w('AvFrozenHi',0,i);w('Enemy_CollisionBits',0,i)
 end
 for i=0,23 do w('ObjectMetasprite',0,i);w('EnemyBoundingBoxCoord',0,i)end
 for i=0,5 do w('FloateyNum_Control',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 for i=0,3 do w('MmBulletType',0,i)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i);w('SmShotType',0,i);w('SmBombAge',0,i)end
 w('Player_X_Position',char==10 and 0 or 8);w('Player_PageLoc',1);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0)
 w('PlayerStatus',0);w('PlayerSize',0);w('PlayerFacingDir',1);w('Player_X_Speed',0);w('Player_Y_Speed',0);w('Player_CollisionBits',3)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',1);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',1);w('HorizontalScroll',0);w('ScrollLock',1)
 w('AreaParserTaskNum',0);w('ScrollThirtyTwo',0);w('EnemyFrenzyBuffer',0);w('EnemyFrenzyQueue',0);w('EnemyObjectPageLoc',255)
 for _,n in ipairs({'InjuryTimer','TimerControl','GuestHurtKind','GuestHurtTicks','GuestInvulTicks','GuestPowerupActive','StarInvincibleTimer','RgAttack','RgThrust','RgCrouch','CrouchingFlag','SmBall','SmCrouch','SmFlip','MmSliding','AvSlash','AvStopwatch','XgWall','MmLastXSpeed'})do w(n,0)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 w('SwimmingFlag',0);w('AreaType',1);w('GameEngineSubroutine',8);w('PlayerOutlinesOff',scene.outline)
 w('Player_X_MoveForce',0);w('Player_Y_MoveForce',0);w('FrameCounter',0)
end
emu.addEventCallback(function()
 local choose=char<6 and frame>=80 and frame<80+20*char and frame%20==0 or char>=6 and frame>=100 and frame<100+20*(char-6)and frame%20==0
 local target=needSetup and scenes[index+1]or scene
 emu.setInput({start=frame==60 or frame==240,right=choose or(target and target.mode=='walk')or false,down=char>=6 and frame==80},0)
 if needSetup then pendingPolls=pendingPolls+1 end
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if observed()then visibility()end
 if frame==550 then needSetup=true;pendingPolls=0 end
 assert(frame<5000,'All bounded crowd benchmarks complete')
end,emu.eventType.endFrame)
