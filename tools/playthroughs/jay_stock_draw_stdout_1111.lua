-- Cold title, Mike's Jay alternate, and one genuine stock gun press.
local rom=os.getenv('SMB_STDOUT_ROM_SHA')or''
local cookie=os.getenv('SMB_JAY_COOKIE')or''
local frame,main,bits,polls=0,0,0,0
local playing,done=false,false
local motion,draw,hardware,chrWrites,drawn,retired=0,0,0,0,0,false
local positions,expected={},{}
local pending

local function read(at)return emu.read(at,emu.memType.nesDebug)end
local function ram(bank,at)return emu.read(bank*8192+at,emu.memType.nesWorkRam)end
local function mapped(at,kind,address)
 local m=emu.convertAddress(at)
 return m and m.memType==emu.memType[kind] and m.address==address
end
local function active()
 return read(0x6002)==16 and read(0x730b)&0x60==0x20 and
  read(0x771)==1 and read(0x773)==3 and read(0x0f)==8
end
local function header(bank)
 local out={}
 for at=0x1fe0,0x1fef do out[#out+1]=string.format('%02x',ram(bank,at))end
 return table.concat(out)
end
local function cell(at,kind)
 return string.format('%02x%02x%02x%02x',emu.read(at,kind),emu.read(at+1,kind),
  emu.read(at+2,kind),emu.read(at+3,kind))
end
local function quote(s)return '"'..tostring(s):gsub('[\\"]','\\%0'):gsub('\n','\\n'):gsub('\r','\\r')..'"'end
local function finish(ok,reason)
 if done then return end
 done=true;bits=0
 print(string.format('SMB_NATIVE_RECEIPT {"passed":%s,"reason":%s,"ROM_SHA256":%s,'..
  '"controller_only":true,"script_RAM_writes":false,"physical_frames":%d,"main":%d,"input_polls":%d,'..
  '"motion_calls":%d,"draw_calls":%d,"stock_positions":%d,"live_draws":%d,"hardware_dma_matches":%d,"chr216_writes":%d,'..
  '"first_cell":%s,"last_cell":%s,"retired":%s,"lives":%d,"cookie":%s}',
  tostring(ok),quote(reason),quote(rom),frame,main,polls,motion,draw,#positions,drawn,hardware,chrWrites,
  quote(positions[1]and positions[1].cell or ''),quote(positions[#positions]and positions[#positions].cell or ''),
  tostring(retired),read(0x75f),quote(cookie)))
 emu.stop(ok and 0 or 1)
end
local function guard(name,f)
 return function(...)
  if done then return end
  local ok,why=pcall(f,...)
  if not ok then finish(false,name..': '..tostring(why))end
 end
end
local function wait(pred)
 for _=1,1000 do if pred()then return end;coroutine.yield()end
 error('Menu or 1-1 readiness timed out')
end
local function press(value)
 bits=value;for _=1,4 do coroutine.yield()end
 bits=0;for _=1,8 do coroutine.yield()end
end
local setup=coroutine.create(function()
 assert(#rom==64 and #cookie==32 and cookie:sub(1,8)=='a7102007','Pinned ROM and Jay cookie')
 wait(function()return frame>=70 and read(0x6004)==1 and read(0x775)==0 end)
 press(16)
 wait(function()return read(0x7307)==2 and read(0x775)==0 end)
 assert(read(0x7309)==0,'Natural menu starts at Mario')
 press(4);for _=1,7 do press(1)end
 assert(read(0x7309)==15 and read(0x6002)==16 and read(0x730b)&0x60==0,'Mike Jones slot')
 press(32)
 assert(read(0x6002)==16 and read(0x730b)&0x60==0x20,'Jay McCray alternate')
 press(16)
 wait(active)
 assert(read(0x764)==0 and read(0x761)==0 and read(0x7ffb)==0 and read(0x7ffc)==0,'Natural 1-1')
 playing=true
end)
emu.addMemoryCallback(guard('authenticated mux',function()
 if not active() or not mapped(0xb303,'nesWorkRam',3*8192+0x1303)then return end
 local kind=emu.getState()['cpu.y']
 assert(header(2)==cookie and header(3)==cookie,'Both committed Jay headers')
 local flags=ram(2,0xa9)
 if kind==224 then
  main=main+1;motion=motion+1
  if flags==0 then
   if #positions>0 then retired=true end
   return
  end
  assert(not retired,'Single stock projectile')
  local x,y=ram(2,0xa6),ram(2,0xa7)
  local prev=positions[#positions]
  assert((not prev and x==56 or prev and x==prev.x+4) and y==191,'Exact stock flight step')
  positions[#positions+1]={x=x,cell=string.format('%02x2800%02x',y-8,x-4)}
  return
 end
 assert(kind==226,'Typed draw caller')
 draw=draw+1
 if flags==0 then
  return
 end
 local x,y=ram(2,0xa6),ram(2,0xa7)
 assert(x>=56 and x<=252 and (x-56)%4==0 and y==191,'Exact projected stock cell')
 expected[string.format('%02x2800%02x',y-8,x-4)]=true
 drawn=drawn+1
end),emu.callbackType.exec,0xb303)
emu.addMemoryCallback(guard('DMA publication',function(_,value)
 if value~=2 or not active()then return end
 pending=nil
 for i=0,63 do
  local c=cell(0x200+i*4,emu.memType.nesDebug)
  if expected[c]then
   assert(not pending,'One stock OAM cell per DMA')
   pending={index=i*4,cell=c}
  end
 end
end),emu.callbackType.write,0x4014)
emu.addMemoryCallback(guard('stock CHR',function(_,value)
 if active() and value==216 then chrWrites=chrWrites+1 end
end),emu.callbackType.write,0x5120)
emu.addEventCallback(guard('input',function()
 polls=polls+1
 emu.setInput({right=bits&1~=0,down=bits&4~=0,start=bits&16~=0,
  select=bits&32~=0,b=bits&64~=0},0)
end),emu.eventType.inputPolled)
emu.addEventCallback(guard('frame',function()
 frame=frame+1
 assert(frame<3600,'Physical bound')
 if not playing then local ok,why=coroutine.resume(setup);assert(ok,why);return end
 assert(active() and read(0x75f)==2,'Remain in active 1-1 with both lives')
 for at=0x5c20,0x5c25 do assert(read(at)==0,'No borrowed Mike shot')end
 if pending then
  assert(cell(pending.index,emu.memType.nesSpriteRam)==pending.cell,'Physical OAM equals DMA source')
  hardware=hardware+1;pending=nil
 end
 bits=main>=4 and main<20 and 64 or 0
 if main>=65 then
  assert(motion>=65 and #positions==50 and retired and drawn>=24 and hardware==drawn and chrWrites>=drawn,
   'Complete native motion, draw, DMA, CHR and retirement witnesses')
  assert(positions[1].cell=='b7280034' and positions[#positions].cell=='b72800f8','Exact first and last cells')
  finish(true,'Jay used the original stock projectile with real sprite DMA and retirement')
 end
end),emu.eventType.endFrame)
