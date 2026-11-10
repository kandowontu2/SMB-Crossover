-- Real controller input only: independent axes, replacement, and native carry.
local frame,updates,pad=0,0,{}
local births,samples={},{}
local function r(n,i) return emu.read(assert(C.ram[n],n)+(i or 0),emu.memType.nesDebug) end
local function pos(lo,hi,i) return r(lo,i)+256*r(hi,i) end
local function active() return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 and r('SelectedCharacter')==C.owner end
local function snapshot()
 local s={frame=frame,updates=updates,x=pos('Player_X_Position','Player_PageLoc'),y=r('Player_Y_Position'),lives=r('NumberofLives'),vertical={},horizontal={}}
 for i=0,5 do
  if r('Enemy_Flag',i)==1 then
   local id,mark=r('Enemy_ID',i),r('Enemy_State',i)
   local axis=id==0x25 and mark==0x41 and 'vertical' or (id==0x28 and mark==0x42 and 'horizontal' or nil)
   if axis then s[axis][#s[axis]+1]={slot=i,x=pos('Enemy_X_Position','Enemy_PageLoc',i),y=r('Enemy_Y_Position',i)} end
  end
 end
 return s
end
local function json(v)
 if type(v)=='string' then return string.format('%q',v) end
 if type(v)~='table' then return tostring(v) end
 local out={}
 if #v>0 then for _,x in ipairs(v) do out[#out+1]=json(x) end;return '['..table.concat(out,',')..']' end
 for k,x in pairs(v) do out[#out+1]=json(tostring(k))..':'..json(x) end
 table.sort(out);return '{'..table.concat(out,',')..'}'
end
local function finish(ok,reason)
 local f=assert(io.open(OUTPUT..'result.json','w'))
 f:write(json({passed=ok,reason=reason,ROM_sha256=C.rom,owner=C.owner,controller_only=true,script_RAM_writes=false,births=births,samples=samples,terminal=snapshot()})..'\n');f:close()
 local png=assert(io.open(OUTPUT..'terminal.png','wb'));png:write(emu.takeScreenshot());png:close()
 emu.stop(ok and 0 or 1)
end
local function frames(n) for _=1,n do coroutine.yield() end end
local function wait(n) local goal=updates+n;while updates<goal do coroutine.yield() end end
local function press(key) pad={[key]=true};frames(4);pad={};frames(8) end
local function ready(test) for _=1,900 do if test() then return end;coroutine.yield() end;error('Startup timeout') end
local function record(name)
 local s=snapshot();s.name=name;samples[#samples+1]=s
 assert(s.lives==2,'Lost a life in '..name);return s
end
local function counts(v,h,name)
 local s=record(name);assert(#s.vertical==v and #s.horizontal==h,name..': incorrect independent ownership');return s
end
local function newBirth(axis,offset)
 local s=births[#births];assert(s and #s[axis]==1,'Missing constructor birth')
 local actor=s[axis][1]
 assert(actor.y==s.y+32,'Incorrect initial platform top')
 assert(actor.x==math.max(0,s.x+offset),'Incorrect front/center position')
 return s
end
local task=coroutine.create(function()
 ready(function() return frame>=70 and r('CrossoverTitleDrawn')==1 and r('DisableScreenFlag')==0 end)
 press('start');ready(function() return r('CrossoverMenuState')==2 and r('DisableScreenFlag')==0 end)
 for _,key in ipairs(C.menu_keys) do press(key) end
 assert(r('SelectedCharacter')==C.owner,'Wrong owner')
 press('start');ready(active);wait(24)
 assert(r('CheatStartLevel')==0 and r('CheatInvincible')==0,'Unexpected cheats')
 counts(0,0,'initial')
 pad={select=true};wait(8);pad={};wait(8);counts(0,0,'Select alone')
 pad={down=true};wait(8);pad={};wait(8);counts(0,0,'Down alone')
 pad={up=true,select=true};wait(3);counts(1,0,'vertical first');assert(#births==1)
 newBirth('vertical',C.vertical_offset)
 wait(30);counts(1,0,'vertical held');assert(#births==1,'Held vertical repeated')
 pad={};wait(5)
 pad={down=true,select=true};wait(3);local first=counts(1,1,'horizontal first');assert(#births==2)
 newBirth('horizontal',C.horizontal_right)
 local left=first.horizontal[1].x
 wait(20);local moved=counts(1,1,'horizontal held');assert(#births==2,'Held horizontal repeated')
 assert(moved.horizontal[1].x~=left,'Horizontal actor did not move')
 -- Replace the horizontal platform near the player immediately before boarding.
 pad={};wait(5);pad={down=true,select=true};wait(3);counts(1,1,'horizontal replacement');assert(#births==3)
 newBirth('horizontal',C.horizontal_right)
 local jump=updates;local carried=0;local prior=nil
 for _=1,150 do
  local s=snapshot();local h=s.horizontal[1]
  assert(h and #s.vertical==1 and #births==3,'Ownership changed while boarding')
  local center=s.x+C.player_center
  pad={right=center<h.x+12,left=center>h.x+20,b=true,a=updates-jump<23}
  if center>=h.x+4 and center<h.x+28 and math.abs(s.y+32-h.y)<=1 then
   pad={}
   if prior and s.x>prior.x and h.x>prior.hx and math.abs((s.x-prior.x)-(h.x-prior.hx))<=1 then carried=carried+1 end
  end
  prior={x=s.x,hx=h.x}
  if carried>=6 then break end
  wait(1)
 end
 assert(carried>=6,'Player did not earn sustained horizontal carrying')
 local supported=counts(1,1,'horizontal carry');supported.carry_updates=carried
 pad={};wait(5);pad={up=true,select=true};wait(3);counts(1,1,'vertical replacement preserves horizontal');assert(#births==4)
 newBirth('vertical',C.vertical_offset)
 wait(12);assert(#births==4,'Held replacement repeated');counts(1,1,'terminal')
 finish(true,'Independent Up/Down+Select native platforms, held-edge handling, axis-only replacement and horizontal carry')
end)
emu.addMemoryCallback(function()
 local at=emu.convertAddress(C.main)
 if at and at.memType==emu.memType.nesPrgRom and at.address==C.main_physical and active() then updates=updates+1 end
end,emu.callbackType.exec,C.main)
emu.addMemoryCallback(function()
 local at=emu.convertAddress(C.spawn)
 if at and at.memType==emu.memType.nesPrgRom and at.address==C.spawn_physical and active() then births[#births+1]=snapshot() end
end,emu.callbackType.exec,C.spawn)
emu.addEventCallback(function() emu.setInput(pad,0) end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1;if frame>6000 then return finish(false,'Frame bound') end
 local ok,err=coroutine.resume(task);if not ok then finish(false,tostring(err)) end
end,emu.eventType.endFrame)
