-- Read-only physical-frame evidence. Capture committed DMA OAM, mapper CHR
-- changes, HUD split register timing and actual audio writes/voice ownership.
-- No screenshot loop, emulated writes, save states or controller changes.
return function(cfg)
 local frame=0
 local finished=false
 local files={}
 local function file(name,header)
  local f=assert(io.open(cfg.out..name..'.csv','w'));f:write(header..'\n');files[#files+1]=f;return f
 end
 local render=file('render','frame,world,level,areaType,mode,task,engine,x,y,yHigh,camera,power,pose,crouch,attack,shoot,wall,ceiling,hover,pitFlight,playerChr,specialChr,worldMask,sourceMask,nativeMask,apuMask,apuWrites,expansionWrites,dmaCount,maxSprites,hudSprites,screenDisabled,lagNmi,behaviorVersion')
 local oam=file('oam','frame,world,level,engine,camera,pose,playerChr,specialChr,visible,maxSprites,hudSprites,chrBanks,oamHex')
 local chr=file('chr','frame,register,value,previous,lagNmi,world,level,engine,rawValue,upperLatch')
 local splits=file('scroll-writes','frame,scanline,dot,address,value,world,level,engine,mode,task,screenDisabled,renderingEnabled,writerPC,writerBank')
 local audio=file('audio-events','frame,event,value,world,level,engine')
 local stomps=file('stomp-events','frame,character,slot,enemyId,enemyFlag,enemyState,hpLo,hpHi,world,level,playerX,playerY,enemyX,enemyY,pc,bank,illegalGuest,behaviorVersion,behaviorSource')
 local function r(n,i)if not L[n]then return 0 end;return emu.read(L[n]+(i or 0),emu.memType.nesDebug)end
 local function pos(lo,hi)return r(lo)+256*r(hi)end
 -- A pre-options ROM has the legacy source2.02 policy. Never infer1.0
 -- from a missing label, nor change emulated settings during a route audit.
 local behaviorSource=L.CrossoverBehaviorVersion and 'menu-setting' or 'legacy-implicit-2.02'
 local function behavior()
  if not L.CrossoverBehaviorVersion then return 1 end
  local value=r('CrossoverBehaviorVersion')
  assert(value==0 or value==1,'Actual behavior preference must be0/1')
  return value
 end
 local lagNmi,inNmi=false,false
 local hardwareMask=0
 emu.addMemoryCallback(function(a,v)hardwareMask=v end,emu.callbackType.write,0x2001)
 local nmiDepth,irqDepth=0,0
 local stompCount,guestStompCount,stompOpcodeMismatches=0,0,0
 local guestEvents,allowedGuestEvents=0,0
 local failure
 local stompPc=assert(L.EnemyStomped,'Native stomp entry label is required by full audit')
 local enemyId=assert(L.Enemy_ID)
 -- Verify the actual resident LDA Enemy_ID,X / CMP #Spiny instructions.
 -- A CPU-address callback alone can also hit swapped audio/weapon code.
 local stompBytes=enemyId<256 and {0xb5,enemyId,0xc9,0x12}
  or {0xbd,enemyId%256,enemyId//256,0xc9,0x12}
 local function residentStomp()
  for i,b in ipairs(stompBytes)do
   if emu.read(stompPc+i-1,emu.memType.nesDebug)~=b then return false end
  end
  return true
 end
 local selector=0
 local banks={}
 local physicalChrChecks,highChrChecks,maxPhysicalChr=0,0,0
 local apuMask,apuWrites,expansionWrites,dmaCount,maxSprites,hudSprites=0,0,0,0,0,0
 local function bank(index,v,raw,upper)
  local old=banks[index]
  if old~=v then
   if frame>=500 then chr:write(table.concat({frame,index,v,old or -1,inNmi and lagNmi and 1 or 0,r('WorldNumber'),r('LevelNumber'),r('GameEngineSubroutine'),raw or v,upper or 0},',')..'\n')end
   banks[index]=v
  end
 end
 if cfg.mapper=='mmc5' then
  -- MMC5 captures5130 at each512x write. A later reset of the high latch
  -- does not move already published windows back into the first256 pages.
  local upper=0
  emu.addMemoryCallback(function(_,v)upper=v&3 end,emu.callbackType.write,0x5130)
  emu.addMemoryCallback(function(a,v)if not finished then bank(a-0x5120,v+256*upper,v,upper)end end,emu.callbackType.write,0x5120,0x512b)
 else
  emu.addMemoryCallback(function(a,v)selector=v&7 end,emu.callbackType.write,0x8000)
  emu.addMemoryCallback(function(a,v)if not finished and selector<6 then bank(selector,v)end end,emu.callbackType.write,0x8001)
 end
 emu.addMemoryCallback(function()nmiDepth=nmiDepth+1;inNmi=true;lagNmi=r('NmiDisable')>=128 end,emu.callbackType.exec,assert(L.NonMaskableInterrupt))
 emu.addMemoryCallback(function()nmiDepth=nmiDepth-1;inNmi=false end,emu.callbackType.exec,assert(L.NonMaskableInterrupt_RTI))
 if L.IrqScrollSplit and L.IrqScrollSplit_RTI then
  emu.addMemoryCallback(function()irqDepth=irqDepth+1 end,emu.callbackType.exec,L.IrqScrollSplit)
  emu.addMemoryCallback(function()irqDepth=irqDepth-1 end,emu.callbackType.exec,L.IrqScrollSplit_RTI)
 end
 emu.addMemoryCallback(function()
  if finished or frame<500 or nmiDepth~=0 or irqDepth~=0
   or r('CurrentBank')%128~=0 or r('OperMode')~=1
   or r('OperMode_Task')~=3 or r('GameEngineSubroutine')~=8 then return end
  if not residentStomp()then
   stompOpcodeMismatches=stompOpcodeMismatches+1
   failure=failure or 'native stomp resident opcode mismatch'
   return
  end
  local slot=emu.getState()['cpu.x']
  assert(slot and slot>=0 and slot<=5,'Native stomp enemy slot is valid')
  local character=r('SelectedCharacter')
  local version=behavior()
  local guest=character~=0 and character~=8
  local illegal=guest and version==1
  if guest then guestEvents=guestEvents+1;if version==0 then allowedGuestEvents=allowedGuestEvents+1 end end
  stompCount=stompCount+1
  if illegal then guestStompCount=guestStompCount+1;failure=failure or 'ordinary guest native stomp' end
  -- Callback is inside the physical frame following the last endFrame row.
  stomps:write(table.concat({frame+1,character,slot,r('Enemy_ID',slot),r('Enemy_Flag',slot),r('Enemy_State',slot),
   r('MmEnemyHealthLo',slot),r('MmEnemyHealthHi',slot),r('WorldNumber'),r('LevelNumber'),
   pos('Player_X_Position','Player_PageLoc'),r('Player_Y_Position'),
   r('Enemy_X_Position',slot)+256*r('Enemy_PageLoc',slot),r('Enemy_Y_Position',slot),
   stompPc,r('CurrentBank'),illegal and 1 or 0,version,behaviorSource},',')..'\n')
 end,emu.callbackType.exec,stompPc)
 emu.addMemoryCallback(function(a,v)
  if finished or frame<500 then return end
  local st=emu.getState();local line=st['ppu.scanline']
  -- Include every visible scanline. A HUD-window-only log cannot detect
  -- the late IRQ/NMI writes that can move the rest of the playfield.
  if line>=0 and line<=239 then
   local pc=st['cpu.pc'];local physical=emu.convertAddress(pc)
   local writerBank=physical and physical.memType==emu.memType.nesPrgRom and physical.address//8192 or -1
   splits:write(table.concat({frame,line,st['ppu.cycle'],a,v,r('WorldNumber'),r('LevelNumber'),r('GameEngineSubroutine'),r('OperMode'),r('OperMode_Task'),r('DisableScreenFlag'),(hardwareMask&0x18)~=0 and 1 or 0,pc,writerBank},',')..'\n')
  end
 end,emu.callbackType.write,0x2005,0x2006)
 emu.addMemoryCallback(function(a,v)
  if finished or frame<500 then return end
  if a==0x4014 then return end
  apuWrites=apuWrites+1
  local channel=a<0x4010 and math.floor((a-0x4000)/4)or 4
  apuMask=apuMask|(1<<channel)
 end,emu.callbackType.write,0x4000,0x4015)
 if cfg.mapper=='mmc5' then
  emu.addMemoryCallback(function(a,v)if not finished and frame>=500 then expansionWrites=expansionWrites+1 end end,emu.callbackType.write,0x5000,0x5015)
 end
 for _,name in ipairs({'Square1SoundQueue','Square2SoundQueue','NoiseSoundQueue','AvAudioRequest','BassAudioRequest','BassSourceId','MmAudioShotType'})do
  if L[name]then
   emu.addMemoryCallback(function(a,v)
    if not finished and frame>=500 and v~=0 then audio:write(table.concat({frame,name,v,r('WorldNumber'),r('LevelNumber'),r('GameEngineSubroutine')},',')..'\n')end
   end,emu.callbackType.write,L[name])
  end
 end
 emu.addMemoryCallback(function(a,page)
  if finished or frame<500 then return end
  dmaCount=dmaCount+1
  local bytes,edges={},{}
  local visible,hud=0,0
  for s=0,63 do
   local at=page*256+s*4
   local y=emu.read(at,emu.memType.nesDebug)+1
   for b=0,3 do bytes[#bytes+1]=string.format('%02x',emu.read(at+b,emu.memType.nesDebug))end
   if y<240 then
    visible=visible+1;if y<32 then hud=hud+1 end
    local first,last=math.max(32,y),math.min(240,y+16)
    if first<last then edges[first]=(edges[first]or 0)+1;edges[last]=(edges[last]or 0)-1 end
   end
  end
  local maximum,count=0,0
  for y=32,239 do count=count+(edges[y]or 0);maximum=math.max(maximum,count)end
  maxSprites,hudSprites=maximum,hud
  local physical={};for i=0,(cfg.mapper=='mmc5'and 11 or 5)do physical[#physical+1]=banks[i]or -1 end
  oam:write(table.concat({frame,r('WorldNumber'),r('LevelNumber'),r('GameEngineSubroutine'),pos('ScreenLeft_X_Pos','ScreenLeft_PageLoc'),r('RgPose'),r('PlayerChrBank'),r('SsChrActive'),visible,maximum,hud,table.concat(physical,':'),table.concat(bytes)},',')..'\n')
 end,emu.callbackType.write,0x4014)
 return {
  failure=function()return failure end,
  frame=function(f)
   frame=f;if finished or frame<500 then return end
   if cfg.mapper=='mmc5' then
    local hardware=emu.getState()
    for i=0,11 do
     local actual=hardware['mapper.chrBanks'..i]
     assert(actual~=nil and banks[i]~=nil,'MMC5 physical CHR evidence is available')
     assert(actual==banks[i],'MMC5 write-time latch model matches actual hardware window'..i..': '..tostring(banks[i])..' vs '..tostring(actual))
     physicalChrChecks=physicalChrChecks+1
     if actual>=256 then highChrChecks=highChrChecks+1 end
     maxPhysicalChr=math.max(maxPhysicalChr,actual)
    end
   end
   render:write(table.concat({frame,r('WorldNumber'),r('LevelNumber'),r('AreaType'),r('OperMode'),r('OperMode_Task'),r('GameEngineSubroutine'),pos('Player_X_Position','Player_PageLoc'),r('Player_Y_Position'),r('Player_Y_HighPos'),pos('ScreenLeft_X_Pos','ScreenLeft_PageLoc'),r('PlayerStatus'),r('RgPose'),r('RgCrouch'),r('RgAttack'),r('RgShootPose'),r('XgWall'),r('XgCeiling'),r('XgHoverActive'),r('XgPitFlight'),r('PlayerChrBank'),r('SsChrActive'),r('GuestMixMask'),r('AvAudioMask'),r('BassAudioPreviousMask')|r('MmAudioSfxMask'),apuMask,apuWrites,expansionWrites,dmaCount,maxSprites,hudSprites,r('DisableScreenFlag'),lagNmi and 1 or 0,behavior()},',')..'\n')
   apuMask,apuWrites,expansionWrites,dmaCount=0,0,0,0
  end,
  finish=function()
   if finished then return end;finished=true
   for _,f in ipairs(files)do f:close()end
   local f=assert(io.open(cfg.out..'stomp-summary.json','w'))
   f:write('{"events":'..stompCount..',"illegal_guest_events":'..guestStompCount..',"guest_events":'..guestEvents..',"allowed_mode_1_0_guest_events":'..allowedGuestEvents..',"behavior_version":'..behavior()..',"behavior_source":'..string.format('%q',behaviorSource)..',"resident_opcode_mismatches":'..stompOpcodeMismatches..',"hook_address":'..stompPc..',"nested_interrupt_guards":true,"physical_frame":"previous endFrame + 1","failure":'..(failure and string.format('%q',failure)or'null')..'}\n');f:close()
   local c=assert(io.open(cfg.out..'chr-audit-summary.json','w'))
   c:write(string.format('{"mapper":%q,"physical_window_checks":%d,"high_window_checks":%d,"maximum_physical_page":%d,"mmc5_write_time_upper_latch":true,"failure":null}\n',cfg.mapper,physicalChrChecks,highChrChecks,maxPhysicalChr));c:close()
  end
 }
end
