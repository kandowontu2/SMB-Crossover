-- Select each named prototype, then exercise its real host movement.
local frame,updates,pad=0,0,{}
local samples={}
local function r(n)return emu.read(assert(C.ram[n],n),emu.memType.nesDebug)end
local function choice()return emu.read(C.choice_address,emu.memType.nesDebug)&C.choice_mask end
local function state()return{frame=frame,updates=updates,x=r('Player_X_Position')+256*r('Player_PageLoc'),y=r('Player_Y_Position'),lives=r('NumberofLives'),owner=r('SelectedCharacter'),choice=choice(),engine=r('GameEngineSubroutine')}end
local function json(v)
 if type(v)=='string'then return string.format('%q',v)end
 if type(v)~='table'then return tostring(v)end
 local out={};if #v>0 then for _,x in ipairs(v)do out[#out+1]=json(x)end;return '['..table.concat(out,',')..']'end
 for k,x in pairs(v)do out[#out+1]=json(tostring(k))..':'..json(x)end;table.sort(out);return '{'..table.concat(out,',')..'}'
end
local function png(name)local f=assert(io.open(OUTPUT..name..'.png','wb'));f:write(emu.takeScreenshot());f:close()end
local function finish(ok,reason)
 local f=assert(io.open(OUTPUT..'result.json','w'));f:write(json({passed=ok,reason=reason,ROM_sha256=C.rom,name=C.name,controller_only=true,script_RAM_writes=false,samples=samples,terminal=state(),scope='Named menu and real idle/walk/jump/turn opening; prototype host abilities retained, original donor moves unqualified.'}));f:close();png('terminal');emu.stop(ok and 0 or 1)
end
local function frames(n)for _=1,n do coroutine.yield()end end
local function wait(n)local target=updates+n;while updates<target do coroutine.yield()end end
local function ready(test)for _=1,1800 do if test()then return end;coroutine.yield()end;error('Ready bound')end
local function press(key)pad={[key]=true};frames(4);pad={};frames(12)end
local function active()return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 and r('SelectedCharacter')==C.owner end
local task=coroutine.create(function()
 ready(function()return frame>=70 and r('CrossoverTitleDrawn')==1 and r('DisableScreenFlag')==0 end)
 press('start');ready(function()return r('CrossoverMenuState')==2 and r('DisableScreenFlag')==0 end)
 for _=1,math.floor(C.slot/8)do press('down')end
 for _=1,C.slot%8 do press('right')end
 for _=1,C.selects do press('select')end
 frames(20);assert(r('CrossoverMenuIndex')==C.slot and r('SelectedCharacter')==C.owner and choice()==C.choice,'Wrong prototype selection')
 local letters={};for i=0,15 do local tile=emu.read(0x2328+i,emu.memType.nesPpuDebug);letters[#letters+1]=tile>=10 and tile<=35 and string.char(tile+55)or' 'end
 local shown=table.concat(letters):match('^%s*(.-)%s*$');assert(shown==C.name,'Wrong visible name: '..shown)
 png('menu');press('start');ready(active);wait(24)
 assert(choice()==C.choice,'Choice lost on newgame')
 local start=state();samples[#samples+1]=start;local minimum=start.y;local maximum=start.x
 for age=1,110 do
  pad={right=age<=70,a=age>=37 and age<55,left=age>70 and age<=100}
  wait(1);local s=state();minimum=math.min(minimum,s.y);maximum=math.max(maximum,s.x)
  assert(active()and s.lives==2 and s.choice==C.choice,'Prototype lost life/control/identity')
  if age==36 or age==54 or age==70 or age==100 or age==110 then samples[#samples+1]=s end
 end
 assert(maximum>=start.x+16,'No walk');assert(minimum<start.y-3,'No jump');assert(state().x<maximum-2,'No left turn')
 finish(true,'Visible prototype name and real host walk/jump/turn passed')
end)
emu.addMemoryCallback(function()
 local at=emu.convertAddress(0x82d9);if at and at.memType==emu.memType.nesPrgRom and at.address==126*8192+0x2d9 and active()then updates=updates+1 end
end,emu.callbackType.exec,0x82d9)
emu.addEventCallback(function()emu.setInput(pad,0)end,emu.eventType.inputPolled)
emu.addEventCallback(function()frame=frame+1;if frame>9000 then return finish(false,'Frame bound')end;local ok,err=coroutine.resume(task);if not ok then finish(false,tostring(err))end end,emu.eventType.endFrame)
