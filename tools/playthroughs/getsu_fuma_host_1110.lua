-- Real frontend, native terrain and controller-only Getsu 1-1 replay.
local frame, updates, draws = 0, 0, 0
local input, menuReady, started = {}, false, false
local screenshots, caps, pits = {}, {}, {}
local firstAttack, swordHit, liveRender, flag, lastX, jumpUntil = nil, nil, nil, nil, 0, 0
local launched = {}
local visualAge, visualRows, lastDraw = 0, {}, nil
local routePipes = {{448,176,404},{608,160,563},{736,144,679},{912,144,855}}
local routePits = {{1104,1136},{1376,1424},{2448,2480}}

local function r(name, i) return emu.read(assert(C.ram[name],name)+(i or 0),emu.memType.nesDebug) end
local function raw(at) return emu.read(at,emu.memType.nesDebug) end
local function ppu(at) return emu.read(at,emu.memType.nesPpuDebug) end
local function position(lo, hi, i) return r(lo,i)+256*r(hi,i) end
local function playerX() return position('Player_X_Position','Player_PageLoc') end
local function cameraX() return position('ScreenLeft_X_Pos','ScreenLeft_PageLoc') end
local function state()
 return {frame=frame,updates=updates,draws=draws,x=playerX(),y=r('Player_Y_Position'),
         y_page=r('Player_Y_HighPos'),camera=cameraX(),engine=r('GameEngineSubroutine'),
         lives=r('NumberofLives'),raw=r('SelectedCharacter'),world=r('WorldNumber')+1,level=r('LevelNumber')+1}
end
local function active()
 return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8
       and r('SelectedCharacter')==42
end
local function actor(i)
 return {slot=i,x=position('Enemy_X_Position','Enemy_PageLoc',i),y=r('Enemy_Y_Position',i),
         flag=r('Enemy_Flag',i),id=r('Enemy_ID',i),state=r('Enemy_State',i)}
end
local function solid(x,y)
 if y<32 or y>=240 then return false end
 local at=0x300+((x>>8)&1)*0xd0+(y&0xf0)-32+((x>>4)&15)
 return raw(C.tileAttribute+raw(at))&1~=0
end
local function json(v)
 if type(v)=='string' then return string.format('%q',v) end
 if type(v)~='table' then return tostring(v) end
 local out={}
 if #v>0 then for _,a in ipairs(v) do out[#out+1]=json(a) end;return '['..table.concat(out,',')..']' end
 for k,a in pairs(v) do out[#out+1]=json(tostring(k))..':'..json(a) end
 table.sort(out);return '{'..table.concat(out,',')..'}'
end
local function shot(name)
 if screenshots[name] then return end
 local file=assert(io.open(OUTPUT..name..'.png','wb'))
 file:write(emu.takeScreenshot());file:close();screenshots[name]=frame
end
local function finish(ok,reason)
 shot('terminal')
 local file=assert(io.open(OUTPUT..'result.json','w'))
 file:write(json({passed=ok,reason=reason,ROM_sha256=C.rom,controller_only=true,
   first_attack=firstAttack,sword_hit=swordHit,live_render=liveRender,flag=flag,
   terminal=state(),max_x=lastX,caps=caps,pits=pits,screenshots=screenshots})..'\n')
 file:close()
 print('Getsu '..reason..' X='..playerX()..' draws='..draws)
 emu.stop(ok and 0 or 1)
end

local function hook(pc, mem, offset, action)
 emu.addMemoryCallback(function()
  local at=emu.convertAddress(pc)
  if at and at.memType==mem and at.address==offset and r('SelectedCharacter')==42 then action() end
 end,emu.callbackType.exec,pc)
end
hook(C.draw,emu.memType.nesWorkRam,3*8192+(C.draw&8191),function()
 draws=draws+1
 if C.probe then
  lastDraw={player=state(),cursor=r('CurrentOAMOffset'),rotation=r('RgOamRotation'),bank_c=r('CurrentBankC')}
 end
end)
hook(C.main,emu.memType.nesPrgRom,126*8192+(C.main&8191),function() if active() then updates=updates+1 end end)
hook(C.flag,emu.memType.nesPrgRom,126*8192+(C.flag&8191),function() if not flag then flag=state() end end)

local function renderEvidence()
 if draws==0 or ppu(0x3f11)~=0 or ppu(0x3f12)~=0x20 or ppu(0x3f13)~=5 then return end
 local rows={}
 local localX,y=playerX()-cameraX(),r('Player_Y_Position')
 for slot=0,63 do
  local at=slot*4
  local oy=emu.read(at,emu.memType.nesSpriteRam)
  local tile=emu.read(at+1,emu.memType.nesSpriteRam)
  local ox=emu.read(at+3,emu.memType.nesSpriteRam)
  if oy<240 and tile<60 and tile%2==0 and math.abs(ox-localX)<25 and math.abs(oy-y)<32 then
   for i=0,31 do if ppu(tile*16+i)~=C.atlas[tile*16+i+1] then return end end
   rows[#rows+1]={slot=slot,y=oy,tile=tile,x=ox}
  end
 end
 if #rows>=4 then
  liveRender={player=state(),parts=rows,palette={0,0x20,5}}
  shot('native-render')
 end
end

local function visualProbe()
 visualAge=visualAge+1
 input=visualAge>=30 and {right=true} or {}
 local marks={[1]=true,[4]=true,[8]=true,[16]=true,[29]=true,[42]=true,[64]=true,[90]=true}
 if marks[visualAge] then
  local row={player=state(),last_draw=lastDraw,palette={},hardware={},shadow={},chr_matches={},age=visualAge}
  for i=0,31 do row.palette[#row.palette+1]=ppu(0x3f00+i) end
  for slot=0,63 do
   local at=4*slot
   local hw={}
   for i=0,3 do hw[i+1]=emu.read(at+i,emu.memType.nesSpriteRam) end
   hw[5]=slot
   if hw[1]<240 then
    row.hardware[#row.hardware+1]=hw
    local tile=hw[2]
    if tile<60 and tile%2==0 then
     local matched=0
     for i=0,31 do if ppu(tile*16+i)==C.atlas[tile*16+i+1] then matched=matched+1 end end
     row.chr_matches[tostring(tile)]=matched
    end
   end
   if raw(0x200+at)<240 then
    row.shadow[#row.shadow+1]={raw(0x200+at),raw(0x201+at),raw(0x202+at),raw(0x203+at),slot}
   end
  end
  visualRows[#visualRows+1]=row
  if visualAge==29 then shot('idle') end
  if visualAge==64 then shot('walk') end
 end
 if visualAge==90 then
  local file=assert(io.open(OUTPUT..'visual.json','w'))
  file:write(json({ROM_sha256=C.rom,samples=visualRows,controller_only=true})..'\n');file:close()
  emu.stop(0)
 end
end

local function wait(n) for _=1,n do coroutine.yield() end end
local function press(key) input={[key]=true};wait(4);input={};wait(8) end
local function ready(test)
 for _=1,480 do if test() then return end;wait(1) end
 error('Title or roster did not become ready')
end
local menu=coroutine.create(function()
 ready(function() return frame>=70 and r('CrossoverTitleDrawn')==1 and r('DisableScreenFlag')==0 end)
 press('start')
 ready(function() return r('CrossoverMenuState')==2 and r('DisableScreenFlag')==0 end)
 for _=1,5 do press('right') end
 assert(r('CrossoverMenuIndex')==5 and r('SelectedCharacter')==5)
 for _=1,4 do press('select') end
 assert(r('Cv3Variant')==4 and r('CrossoverMenuIndex')==5)
 local name={}
 for i=0,15 do
  local tile=ppu(0x2328+i)
  name[#name+1]=tile==36 and ' ' or (tile>=10 and tile<=35 and string.char(tile+55) or '?')
 end
 assert(table.concat(name):match('^ *GETSU FUMA *$'),table.concat(name))
 shot('menu')
 press('start');menuReady=true
end)

local function choose()
 local x,y=playerX(),r('Player_Y_Position')
 local ground=r('Player_State')==0
 local target, threat
 for i=0,5 do
  local a=actor(i)
  if a.flag==1 and a.id<=6 and a.state<32 then
   local gap=a.x-x
   if a.id==6 and not firstAttack and x<350 and gap>=42 and gap<=49 then
    firstAttack={player=state(),target=a}
   end
   if gap>=23 and gap<=(x>970 and 34 or 43) and math.abs(a.y-y-8)<24 then threat=true end
  end
 end
 for _,q in ipairs(routePipes) do
  if not launched[q[1]] and x>=q[3] and x<q[1]-6 then target=q[1];break end
 end
 for _,q in ipairs(routePits) do
  if not target and not launched[q[1]] and x>=q[1]-30 and x<q[1] then target=q[1];break end
 end
 if x>=3150 and x<3176 and not launched[3168] then target=3168 end
 local combat=threat and ((x<380 and (not firstAttack or swordHit)) or (x>970 and x<3100))
 if ground and updates>=jumpUntil and (target or combat or (x>970 and x<3100 and solid(x+25,y+24))) then
  jumpUntil=updates+23
  if target then launched[target]=true end
 end
 input={right=true,a=updates<jumpUntil,b=firstAttack~=nil and updates<firstAttack.player.updates+4}
end

emu.addEventCallback(function() emu.setInput(input,0) end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if not menuReady then
  local ok,message=coroutine.resume(menu)
  if not ok then finish(false,tostring(message)) end
  return
 end
 if frame>=8800 then return finish(false,'bounded replay timeout') end
 if not active() then
  if started and r('GameEngineSubroutine')==11 then return finish(false,'native death') end
  input=started and {right=true} or {};return
 end
 if not started then
  started=true
  if r('NumberofLives')~=2 or r('CheatStartLevel')~=0 or r('CheatInvincible')~=0 then
   return finish(false,'unexpected stage or cheat state')
  end
 end
 if r('NumberofLives')~=2 then return finish(false,'life lost') end
 if C.probe then return visualProbe() end
 if not liveRender then renderEvidence() end
 local x,y=playerX(),r('Player_Y_Position')
 lastX=math.max(lastX,x)
 if firstAttack and not swordHit then
  local a=actor(firstAttack.target.slot)
  if a.flag==1 and a.id==6 and a.state&32~=0 then swordHit={player=state(),target=a};shot('sword-hit') end
 end
 for _,q in ipairs(routePipes) do
  if not caps[q[1]] and x+8>=q[1] and x+8<q[1]+32 and y+32<=q[2] then caps[q[1]]=state() end
 end
 for _,q in ipairs(routePits) do
  if not pits[q[1]] and x+8>=q[1] and x+8<q[2] and y<=176 and r('Player_State')~=0 then pits[q[1]]=state() end
 end
 if C.smoke and x>=486 and y==176 and r('Player_State')==0 then
  return finish(not not (liveRender and swordHit and caps[448]),'first pipe settled')
 end
 if r('WorldNumber')==0 and r('LevelNumber')==1 then
  return finish(not not (liveRender and swordHit and flag and caps[448] and caps[608] and caps[736] and caps[912]
                 and pits[1104] and pits[1376] and pits[2448]),'active 1-2')
 end
 choose()
end,emu.eventType.endFrame)
