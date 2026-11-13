-- Cold menu and real controller activation. The only seeded values are
-- the selected option, its ownership bit, and one unit of source stock.
local frame, age, state, done = 0, 0, 'title', false
local epoch, updates, lives, initial = nil, 0, nil, nil
local phase, timer = 'seed', 0
local phaseFrames, phaseCodes = {}, {}
local expectedTiles = {[128]={[0xc2]=true,[0xc4]=true},
 [129]={[0xc6]=true,[0xfa]=true},[130]={[0xc6]=true,[0xfa]=true},[131]={[0xfc]=true,[0xfe]=true}}
local visible, hit, nearby = {}, 0, 0
local bombX, bombY, originFrame, minimumSP = -1, -1, -1, 255
local function r(name, slot)
 return emu.read(assert(L[name],name)+(slot or 0),emu.memType.nesDebug)
end
local function source(offset)
 return emu.read(2*8192+offset,emu.memType.nesWorkRam)
end
local function world()
 return r('Player_PageLoc')*256+r('Player_X_Position')
end
local function finish(ok, reason)
 if done then return end
 done=true
 print('SMB_NATIVE_RECEIPT '..string.format(
  '{"passed":%s,"ROM_SHA256":"%s","reason":"%s","frames":%d,"updates":%d,"lives":%d,"fixture":true,"fixture_offsets":[142,143,187],"controller_activated":%s,"stock_after":%d,"phase_codes":[%s],"phase_updates":[%s],"original_armed_OAM":%s,"original_blast_OAM":%s,"native_blast_contacts":%d,"maximum_nearby_enemies":%d,"bomb_X":%d,"bomb_Y":%d,"minimum_contact_SP":%d}',
  tostring(ok),ROM_SHA,reason,frame,updates,r('NumberofLives'),tostring(originFrame>=0),source(0xbb),
  table.concat(phaseCodes,','),table.concat(phaseFrames,','),tostring(visible[128] or false),
  tostring(visible[130] or visible[131] or false),hit,nearby,bombX,bombY,minimumSP))
 emu.stop(ok and 0 or 1)
end

emu.addMemoryCallback(function()
 local sp=emu.getState()['cpu.sp']
 local lo=emu.read(0x100+((sp+1)&255),emu.memType.nesDebug)
 local hi=emu.read(0x100+((sp+2)&255),emu.memType.nesDebug)
 if state=='game' and r('SelectedCharacter')==34 and r('CurrentBankC')==2
   and lo+256*hi==BOMB_CONTACT_RETURN and source(0xc0)>=129 then
  local x=r('ObjectOffset')
  if x<6 and r('Enemy_Flag',x)>0 then
   hit=hit+1
   minimumSP=math.min(minimumSP,sp)
  end
 end
end,emu.callbackType.exec,L.HandleEnemyFBallCol)

emu.addEventCallback(function()
 local pad={}
 if age<4 then
  if state=='open' or state=='start' then pad.start=true
  elseif state=='left' then pad.left=true
  elseif state=='select' then pad.select=true end
 end
 if state=='game' and r('GameEngineSubroutine')==8 then
  if phase=='choose' then pad.select=true
  elseif phase=='arm' then pad.down=true;pad.b=true
  elseif phase=='retreat' then pad.right=world()<initial+36 end
 end
 emu.setInput(pad,0)
end,emu.eventType.inputPolled)

emu.addEventCallback(function()
 if done then return end
 frame=frame+1
 age=age+1
 if state=='title' and frame>=100 then state='open';age=0
 elseif state=='open' and age>=50 then
  assert(r('CrossoverMenuState')==2,'Real roster menu did not open');state='left';age=0
 elseif state=='left' and age>=30 then
  assert(r('CrossoverMenuIndex')==7,'Rygar menu slot');state='select';age=0
 elseif state=='select' and age>=30 then
  assert(r('SelectedCharacter')==34,'Karnov alternate');state='start';age=0
 elseif state=='start' and age>=300 then
  assert(r('GameEngineSubroutine')==8 and source(0x810)==167,'Real Karnov constructor');state='game';age=0
  lives=r('NumberofLives')
 elseif state=='game' then
  if r('NumberofLives')~=lives or r('GameEngineSubroutine')==11 then finish(false,'lost-life');return end
  local now=r('FrameCounter')
  if now~=epoch then
   epoch=now;updates=updates+1;timer=timer+1
   if phase=='seed' and timer>=4 and r('Player_State')==0 then
    emu.write(2*8192+0x8e,255,emu.memType.nesWorkRam)
    emu.write(2*8192+0x8f,2,emu.memType.nesWorkRam)
    emu.write(2*8192+0xbb,1,emu.memType.nesWorkRam)
    phase='choose';timer=0;initial=world()
   elseif phase=='choose' and source(0x8e)==1 then phase='release';timer=0
   elseif phase=='release' and timer>=2 then phase='arm';timer=0
   elseif phase=='arm' and source(0xc0)==128 then
    phase='retreat';timer=0;originFrame=frame
    local camera=r('ScreenLeft_PageLoc')*256+r('ScreenLeft_X_Pos')
    bombX=camera+source(0xc1);bombY=source(0xc2)-16
   end
   local code=source(0xc0)
   if originFrame>=0 and phaseCodes[#phaseCodes]~=code then
    phaseCodes[#phaseCodes+1]=code;phaseFrames[#phaseFrames+1]=updates
   end
   if originFrame>=0 and code==0 then
    local ok=table.concat(phaseCodes,',')=='128,129,130,131,0' and source(0xbb)==0 and visible[128] and (visible[130] or visible[131])
    finish(ok and true or false,ok and 'bomb-lifecycle' or 'bomb-lifecycle-or-art');return
   end
  end
  local code=source(0xc0)
  local tiles=expectedTiles[code]
  if tiles then
   local seen=0
   local camera=r('ScreenLeft_PageLoc')*256+r('ScreenLeft_X_Pos')
   local expectedX=bombX-camera-(code==128 and 4 or 8)
   for i=0,63 do
    local a=4*i
    local y=emu.read(a,emu.memType.nesSpriteRam)
    local tile=emu.read(a+1,emu.memType.nesSpriteRam)
    local x=emu.read(a+3,emu.memType.nesSpriteRam)
    if tiles[tile] and y==bombY and (x==expectedX or code~=128 and x==expectedX+8) then seen=seen+1 end
   end
   if seen==(code==128 and 1 or 2) then visible[code]=true end
   local n=0
   for x=0,5 do
    if r('Enemy_Flag',x)>0 and r('Enemy_ID',x)<21 then
     local ex=r('Enemy_PageLoc',x)*256+r('Enemy_X_Position',x)
     if math.abs(ex-bombX)<24 then n=n+1 end
    end
   end
   nearby=math.max(nearby,n)
  end
 end
 if frame>2600 then finish(false,'route-bound')end
end,emu.eventType.endFrame)
