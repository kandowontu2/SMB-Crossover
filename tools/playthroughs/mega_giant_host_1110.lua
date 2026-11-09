-- Actual Select/Start and the CPU-qualified Giant 1-1 controller policy.
local frame, updates, draws, lag = 0, 0, 0, 0
local input, entered, menuReady, polled = {}, false, false, false
local holdUntil, combatUntil = 0, 0
local firstJump, firstSettled, secondJump = false, false, false
local settled, launched, marks, jumps = {}, {}, {}, {}
local body, flag, upper, control = nil, nil, 0, 0
local chr = {}
local secondPipe, lastPipeUpdate = {}, -1
local pits = {{1104,1136},{1376,1424},{2448,2480}}
local thresholds = {448,482,608,640,736,768,912,944,1104,1136,1376,1424,2448,2480,2994,3008,3168,3266}

local function ram(at) return emu.read(at,emu.memType.nesDebug) end
local function r(name,i) return ram(assert(C.ram[name],name)+(i or 0)) end
local function pos(lo,hi,i) return r(lo,i)+256*r(hi,i) end
local function x() return pos('Player_X_Position','Player_PageLoc') end
local function owner() return r('SelectedCharacter')==0 and r('MarioVariant')==9 end
local function playing() return r('OperMode')==1 and r('OperMode_Task')==3 end
local function active() return playing() and r('GameEngineSubroutine')==8 and owner() end
local function state()
 return {frame=frame,updates=updates,x=x(),y=r('Player_Y_Position'),
   camera=pos('ScreenLeft_X_Pos','ScreenLeft_PageLoc'),engine=r('GameEngineSubroutine'),
   lives=r('NumberofLives'),world=r('WorldNumber')+1,level=r('LevelNumber')+1}
end

local function json(v)
 if type(v)=='string' then return string.format('%q',v) end
 if type(v)~='table' then return tostring(v) end
 local out={}
 if #v>0 then
  for _,value in ipairs(v) do out[#out+1]=json(value) end
  return '['..table.concat(out,',')..']'
 end
 for k,value in pairs(v) do out[#out+1]=string.format('%q',tostring(k))..':'..json(value) end
 table.sort(out)
 return '{'..table.concat(out,',')..'}'
end

local function shot(name)
 local file=assert(io.open(OUTPUT..name..'.png','wb'))
 file:write(emu.takeScreenshot());file:close()
end

local function finish(ok,reason)
 shot('terminal')
 local f=assert(io.open(OUTPUT..'result.json','w'))
 f:write(json({passed=ok,reason=reason,ROM_sha256=C.rom,controller_only=true,
  terminal=state(),body=body,flag=flag,milestones=marks,jumps=jumps,draws=draws,
  second_pipe=secondPipe,active_missed_reads=lag})..'\n')
 f:close()
 print('Mega Giant '..reason..' X='..x()..' draws='..draws)
 emu.stop(ok and 0 or 1)
end

local function hook(pc,mem,offset,action)
 emu.addMemoryCallback(function()
  local at=emu.convertAddress(pc)
  if at and at.memType==mem and at.address==offset and owner() then action() end
 end,emu.callbackType.exec,pc)
end
hook(C.main,emu.memType.nesPrgRom,126*8192+(C.main&8191),function()
 if playing() then updates=updates+1 end
end)
hook(C.draw,emu.memType.nesWorkRam,3*8192+(C.draw&8191),function() draws=draws+1 end)
hook(C.flag,emu.memType.nesPrgRom,126*8192+(C.flag&8191),function()
 if not flag then flag=state() end
end)
emu.addMemoryCallback(function(_,v) upper=v&3 end,emu.callbackType.write,0x5130)
emu.addMemoryCallback(function(_,v) chr[1]=v+256*upper end,emu.callbackType.write,0x5126)
emu.addMemoryCallback(function(_,v) chr[2]=v+256*upper end,emu.callbackType.write,0x5127)
emu.addMemoryCallback(function(_,v) control=v end,emu.callbackType.write,0x2000)
emu.addMemoryCallback(function() polled=true end,emu.callbackType.read,0x4016)
emu.addMemoryCallback(function() polled=true end,emu.callbackType.read,0x4017)
emu.addEventCallback(function() emu.setInput(input,0) end,emu.eventType.inputPolled)

local function observeBody()
 if body or draws<12 or not chr[1] or not chr[2] or control&32==0 then return end
 if chr[1]<168 or chr[1]>210 or chr[1]%2~=0 or chr[2]<168 or chr[2]>210 or chr[2]%2~=0 then return end
 local count,minY,maxY=0,255,0
 for i=0,63 do
  local sy=emu.read(i*4,emu.memType.nesSpriteRam)
  local tile=emu.read(i*4+1,emu.memType.nesSpriteRam)
  if sy>15 and sy<240 and tile>=0x81 and tile<0xff and tile%2==1 then
   count=count+1;minY=math.min(minY,sy);maxY=math.max(maxY,sy)
  end
 end
 if count>=24 and maxY-minY>=80 then
  body={state=state(),sprite_parts=count,y_extent=maxY-minY,chr={chr[1],chr[2]},control=control}
  shot('body')
 end
end

local function observeSecondPipe()
 local xx=x()
 if xx<580 or xx>675 or updates==lastPipeUpdate or #secondPipe>=96 then return end
 lastPipeUpdate=updates
 local q=state()
 q.status=r('PlayerStatus');q.timer=r('TimerControl');q.player_state=r('Player_State')
 q.vy=r('Player_Y_Speed');q.pad=r('A_B_Buttons');q.previous=r('PreviousA_B_Buttons');q.actors={}
 for i=0,5 do
  if r('Enemy_Flag',i)==1 then
   q.actors[#q.actors+1]={i,r('Enemy_ID',i),pos('Enemy_X_Position','Enemy_PageLoc',i),
                        r('Enemy_Y_Position',i),r('Enemy_State',i)}
  end
 end
 secondPipe[#secondPipe+1]=q
end

local function wait(n) for _=1,n do coroutine.yield() end end
local function press(key) input={[key]=true};wait(4);input={};wait(8) end
local function ready(test)
 for _=1,600 do if test() then return end;wait(1) end
 error('Title or roster did not become ready')
end
local menu=coroutine.create(function()
 ready(function() return frame>=70 and r('CrossoverTitleDrawn')==1 and r('DisableScreenFlag')==0 end)
 press('start')
 ready(function() return r('CrossoverMenuState')==2 and r('DisableScreenFlag')==0 end)
 assert(r('CrossoverMenuIndex')==0)
 for _=1,9 do press('select') end
 assert(owner())
 local name={}
 for i=0,15 do
  local tile=emu.read(0x2328+i,emu.memType.nesPpuDebug)
  name[#name+1]=tile==36 and ' ' or (tile>=10 and tile<=35 and string.char(tile+55) or '?')
 end
 assert(table.concat(name)=='MEGA GIANT MARIO',table.concat(name))
 shot('menu')
 press('start');menuReady=true
end)

local function launch(reason,hold)
 holdUntil=updates+hold
 jumps[#jumps+1]={reason=reason,state=state()}
end

local function choose()
 local xx,y,speed=x(),r('Player_Y_Position'),r('Player_X_Speed')
 local ground=r('Player_State')==0
 local function brake() input=(speed>0 and speed<128) and {left=true} or {} end
 if xx<482 then
  if xx>=264 and not firstJump then firstJump=true;launch('first_goomba',35) end
  if xx>=402 and not firstSettled then
   if y==176 and ground then firstSettled=true else brake();return end
  end
 elseif xx>=580 and xx<607 and ground and not secondJump then
  -- Start left of the overhang so the head clears its underside.
  secondJump=true;launch('second_pipe_approach',40)
 else
  local stop=(xx>=679 and xx<711 and not settled[679] and 679) or
             (xx>=853 and xx<885 and not settled[853] and 853)
  if stop then
   if y==176 and ground then settled[stop]=true;launch('pipe',28) else brake();return end
  elseif ground and updates>=holdUntil then
   local target
   for _,p in ipairs(pits) do
    if not launched[p[1]] and xx>=p[1]-30 and xx<p[1] then target=p[1];launched[p[1]]=true;break end
   end
   if not target and xx>=2973 and xx<3010 and not launched[2994] then
    target='castle_approach';launched[2994]=true
   end
   if not target and updates>=combatUntil then
    for i=0,5 do
     local gap=pos('Enemy_X_Position','Enemy_PageLoc',i)-xx
     if r('Enemy_Flag',i)==1 and r('Enemy_ID',i)<=6 and r('Enemy_State',i)<32 and
        gap>=10 and gap<=66 and math.abs(r('Enemy_Y_Position',i)-y-8)<24 then target='actor';break end
    end
   end
   if not target and xx>=3128 and xx<3168 and not launched[3168] then target=3168;launched[3168]=true end
   if target then launch(tostring(target),28);combatUntil=updates+30 end
  end
 end
 input={right=true,b=true,a=updates<holdUntil}
end

emu.addEventCallback(function()
 frame=frame+1
 local read=polled;polled=false
 if not menuReady then
  local ok,err=coroutine.resume(menu)
  if not ok then finish(false,tostring(err)) end
  return
 end
 if frame>=16000 then return finish(false,'physical frame bound') end
 if entered and playing() and owner() then observeSecondPipe() end
 if not active() then
  if entered and (r('GameEngineSubroutine')==11 or r('NumberofLives')~=2) then return finish(false,'native death') end
  input=entered and {right=true} or {}
  return
 end
 if not entered then
  entered=true
  if r('NumberofLives')~=2 or r('CheatStartLevel')~=0 or r('CheatInvincible')~=0 then
   return finish(false,'unexpected initial stage or cheats')
  end
 end
 if r('NumberofLives')~=2 then return finish(false,'life lost') end
 if not read then lag=lag+1 end
 observeBody()
 for _,mark in ipairs(thresholds) do if x()>=mark and not marks[mark] then marks[mark]=state() end end
 if r('LevelNumber')==1 and r('WorldNumber')==0 then
  return finish(not not (body and flag and marks[944] and marks[1136] and marks[1424] and marks[2480]),'active 1-2')
 end
 choose()
end,emu.eventType.endFrame)
