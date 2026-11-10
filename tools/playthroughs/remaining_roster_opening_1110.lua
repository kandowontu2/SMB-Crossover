-- Cold menu and a short playable opening; no emulated state writes.
local frame,updates,pad=0,0,{}
local samples={}
local function r(n)return emu.read(assert(C.ram[n],n),emu.memType.nesDebug)end
local function snapshot()
 return {frame=frame,updates=updates,x=r('Player_X_Position')+256*r('Player_PageLoc'),y=r('Player_Y_Position'),
  lives=r('NumberofLives'),owner=r('SelectedCharacter'),engine=r('GameEngineSubroutine')}
end
local function json(v)
 if type(v)=='string' then return string.format('%q',v) end
 if type(v)~='table' then return tostring(v) end
 local out={};if #v>0 then for _,x in ipairs(v)do out[#out+1]=json(x)end;return '['..table.concat(out,',')..']' end
 for k,x in pairs(v)do out[#out+1]=json(tostring(k))..':'..json(x)end;table.sort(out);return '{'..table.concat(out,',')..'}'
end
local function finish(ok,reason)
 local f=assert(io.open(OUTPUT..'result.json','w'));f:write(json({passed=ok,reason=reason,ROM_sha256=C.rom,
  controller_only=true,script_RAM_writes=false,samples=samples,terminal=snapshot(),scope='Cold menu, authentic header, idle/walk/jump opening only; full1-1 not qualified.'}));f:close()
 f=assert(io.open(OUTPUT..'terminal.png','wb'));f:write(emu.takeScreenshot());f:close();emu.stop(ok and 0 or 1)
end
local function frames(n)for _=1,n do coroutine.yield()end end
local function wait(n)local target=updates+n;while updates<target do coroutine.yield()end end
local function ready(test)for _=1,1800 do if test()then return end;coroutine.yield()end;error('Ready timeout')end
local function press(key)pad={[key]=true};frames(4);pad={};frames(12)end
local function active()return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 and r('SelectedCharacter')==C.owner end
local task=coroutine.create(function()
 ready(function()return frame>=70 and r('CrossoverTitleDrawn')==1 and r('DisableScreenFlag')==0 end)
 press('start');ready(function()return r('CrossoverMenuState')==2 and r('DisableScreenFlag')==0 end)
 for _=1,3 do press('down')end
 for _=1,C.slot%8 do press('right')end
 assert(r('CrossoverMenuIndex')==C.slot,'Wrong roster slot')
 press('select');assert(r('SelectedCharacter')==C.owner,'Wrong alternate')
 press('start');ready(active);wait(24)
 for _,bank in ipairs({2,3})do
  for i,value in ipairs(C.cookie)do assert(emu.read(bank*8192+0x1fe0+i-1,emu.memType.nesWorkRam)==value,'Authentic kernel header mismatch')end
 end
 local start=snapshot();samples[#samples+1]=start;local minimum=start.y
 for age=1,92 do
  pad={right=age<=72,a=age>=37 and age<55}
  wait(1);local s=snapshot();minimum=math.min(minimum,s.y)
  assert(active() and s.lives==2,'Opening lost control/life')
  if age==36 or age==54 or age==72 or age==92 then samples[#samples+1]=s end
 end
 assert(snapshot().x>=start.x+16,'No playable horizontal movement')
 assert(minimum<start.y-3,'No playable jump')
 finish(true,'Authentic character selected, initialized and moved/jumped in1-1')
end)
emu.addMemoryCallback(function()
 local at=emu.convertAddress(0x82d9)
 if at and at.memType==emu.memType.nesPrgRom and at.address==126*8192+0x2d9 and active()then updates=updates+1 end
end,emu.callbackType.exec,0x82d9)
emu.addEventCallback(function()emu.setInput(pad,0)end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1;if frame>9000 then return finish(false,'Frame bound')end
 local ok,err=coroutine.resume(task);if not ok then finish(false,tostring(err))end
end,emu.eventType.endFrame)
