-- Controller-only smoke test. C contains exact ROM, labels and owned actor marker.
local frame, updates, pad = 0, 0, {}
local phases, samples, births = {}, {}, 0
local function rd(a) return emu.read(a,emu.memType.nesDebug) end
local function r(n,i) return rd(assert(C.ram[n],n)+(i or 0)) end
local function pos(lo,hi,i) return r(lo,i)+256*r(hi,i) end
local function active()
 return r('OperMode')==1 and r('OperMode_Task')==3 and
        r('GameEngineSubroutine')==8 and r('SelectedCharacter')==C.owner
end
local function snapshot()
 local actors={}
 for i=0,5 do
  if r('Enemy_Flag',i)~=0 and r('Enemy_ID',i)==C.actor and r('Enemy_State',i)==C.marker then
   actors[#actors+1]={slot=i,x=pos('Enemy_X_Position','Enemy_PageLoc',i),y=r('Enemy_Y_Position',i)}
  end
 end
 return {frame=frame,updates=updates,x=pos('Player_X_Position','Player_PageLoc'),
         y=r('Player_Y_Position'),state=r('Player_State'),lives=r('NumberofLives'),actors=actors,births=births}
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
 table.sort(out);return '{'..table.concat(out,',')..'}'
end
local function record(name)
 local s=snapshot();s.phase=name;samples[#samples+1]=s;return s
end
local function finish(ok,reason)
 local f=assert(io.open(OUTPUT..'result.json','w'))
 f:write(json({passed=ok,reason=reason,ROM_sha256=C.rom,owner=C.owner,
              controller_only=true,script_RAM_writes=false,samples=samples,terminal=snapshot()})..'\n');f:close()
 local image=assert(io.open(OUTPUT..'terminal.png','wb'));image:write(emu.takeScreenshot());image:close()
 emu.stop(ok and 0 or 1)
end
local function wait(n)
 local goal=updates+n
 while updates<goal do coroutine.yield() end
end
local function frames(n) for _=1,n do coroutine.yield() end end
local function press(key) pad={[key]=true};frames(4);pad={};frames(8) end
local function untilReady(test)
 for _=1,900 do if test() then return end;coroutine.yield() end
 error('Menu/game startup timeout')
end
local function one(name)
 local s=record(name);assert(#s.actors==1,name..': expected one owned helper');return s
end
local task=coroutine.create(function()
 untilReady(function() return frame>=70 and r('CrossoverTitleDrawn')==1 and r('DisableScreenFlag')==0 end)
 press('start')
 untilReady(function() return r('CrossoverMenuState')==2 and r('DisableScreenFlag')==0 end)
 assert(r('CrossoverMenuIndex')==0)
 for _,key in ipairs(C.menu_keys) do press(key) end
 assert(r('SelectedCharacter')==C.owner,'Wrong menu owner')
 press('start');untilReady(active);wait(24)
 assert(r('CheatStartLevel')==0 and r('CheatInvincible')==0,'Unexpected cheats')
 local initial=record('idle');assert(#initial.actors==0 and initial.lives==2)
 pad={select=true};wait(10);pad={};wait(8)
 assert(#record('select_only').actors==0,'Select alone created a helper')
 pad={up=true};wait(8);pad={};wait(8)
 assert(#record('up_only').actors==0,'Up alone created a helper')
 local before=record('before_combo')
 pad={up=true,select=true};wait(3)
 local first=one('first_combo');assert(first.births==1,'First combination must create once')
 assert(math.abs(first.actors[1].x+C.width/2-(before.x+C.player_center))<=2,'Helper not centered under player')
 local low,high=first.actors[1].y,first.actors[1].y
 local carried=false
 for _=1,60 do
  wait(1);local s=snapshot();assert(#s.actors==1 and s.births==1,'Held combination recreated helper')
  low=math.min(low,s.actors[1].y);high=math.max(high,s.actors[1].y)
  if s.y~=first.y and s.state==0 then carried=true end
 end
 assert(high-low>=4,'Platform did not move vertically');assert(carried,'Player was not carried')
 one('held_combo');pad={};wait(8)
 pad={right=true};wait(20);pad={};wait(8)
 local moved=record('moved');assert(math.abs(moved.x-before.x)>=8,'Player did not move before replacement')
 pad={up=true,select=true};wait(3)
 local second=one('replacement');assert(second.births==2,'Second combination must replace once')
 assert(math.abs(second.actors[1].x+C.width/2-(moved.x+C.player_center))<=2,'Replacement not below current player')
 wait(20);assert(one('replacement_held').births==2,'Held replacement repeated')
 pad={};assert(snapshot().lives==initial.lives,'Life lost during helper smoke')
 finish(true,'Two distinct Up+Select presses; one moving native helper, actual carry, replacement, no single-button trigger')
end)
emu.addMemoryCallback(function()
 local at=emu.convertAddress(C.main)
 if at and at.memType==emu.memType.nesPrgRom and at.address==C.main_physical and active() then updates=updates+1 end
end,emu.callbackType.exec,C.main)
emu.addMemoryCallback(function()
 local at=emu.convertAddress(C.spawn)
 if at and at.memType==C.spawn_mem and at.address==C.spawn_physical and active() then births=births+1 end
end,emu.callbackType.exec,C.spawn)
emu.addEventCallback(function() emu.setInput(pad,0) end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame>5000 then finish(false,'Physical frame timeout');return end
 local ok,err=coroutine.resume(task)
 if not ok then finish(false,tostring(err)) end
end,emu.eventType.endFrame)
