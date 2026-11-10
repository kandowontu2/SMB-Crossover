-- Native title navigation, preview writes and 1-1 startup. Controller input only.
local rom=os.getenv('SMB_STDOUT_ROM_SHA')or''
local route=tonumber(os.getenv('SMB_TEST_VARIANT')or'0')
local old='49295acff1d70349119b599882a2ec0b4e2f58d21f153c90b2228dc9aceee2a7'
local fixed='9897c2b85489024be25b4b296d0ea57975a579ba1e3ff37a71f7ac3e0b195b97'
local firstTier=rom==old and 1 or 0
local frame,bits,polls=0,0,0
local previews,writes={},{}
local firstActive,terminal
local stopped=false

local function read(a)return emu.read(a,emu.memType.nesDebug)end
local function snapshot()
 return{frame=frame,index=read(0x7309),owner=read(0x6002),status=read(0x75b),
  variant=read(0x5fe3),native_character=read(0x5c3e),health=read(0x5f98),
  private_size=read(0x5c74),size=read(0x759),mode=read(0x771),task=read(0x773),
  engine=read(0x0f),world=read(0x764),level=read(0x761),area=read(0x754),
  x=read(0x75)+256*read(0x5c),y=read(0xbd),lives=read(0x75f)}
end
local function quote(s)
 return'"'..s:gsub('[%z\1-\31\\"]',function(c)
  if c=='"'then return'\\"'elseif c=='\\'then return'\\\\'end
  return string.format('\\u%04x',string.byte(c))
 end)..'"'
end
local function json(v)
 local t=type(v)
 if t=='string'then return quote(v)end
 if t=='nil'then return'null'end
 if t~='table'then return tostring(v)end
 local out={}
 if #v>0 then
  for _,x in ipairs(v)do out[#out+1]=json(x)end
  return'['..table.concat(out,',')..']'
 end
 for k,x in pairs(v)do out[#out+1]=quote(k)..':'..json(x)end
 table.sort(out)
 return'{'..table.concat(out,',')..'}'
end
local function finish(ok,why)
 if stopped then return end
 stopped=true
 bits=0
 print('SMB_NATIVE_RECEIPT '..json({passed=ok,reason=why,ROM_SHA256=rom,variant=route,
  controller_only=true,script_RAM_writes=false,outputs_written=0,physical_frames=frame,
  input_polls=polls,previews=previews,export_writes=writes,initial_stage=firstActive,
  terminal=terminal or snapshot()}))
 emu.stop(ok and 0 or 1)
end
local function press(value)
 bits=value;for _=1,4 do coroutine.yield()end
 bits=0;for _=1,8 do coroutine.yield()end
end
local function wait(pred)
 for _=1,850 do if pred()then return end;coroutine.yield()end
 error('Native readiness timeout')
end
local function active()
 return read(0x771)==1 and read(0x773)==3 and read(0x0f)==8
end
local function preview(index,owner,tier)
 local s=snapshot()
 assert(s.index==index and s.owner==owner and s.status==tier,
  'Preview identity or tier '..json(s))
 previews[#previews+1]=s
 return s
end
local task=coroutine.create(function()
 assert(rom==old or rom==fixed,'Pinned ROM')
 assert(route>=0 and route<=2,'Known controller route')
 wait(function()return frame>=70 and read(0x6004)==1 and read(0x775)==0 end)
 press(16)
 wait(function()return read(0x7307)==2 and read(0x775)==0 end)
 assert(read(0x7309)==0 and read(0x75b)==0,'Natural menu starts at Mario, tier0')
 for _,index in ipairs({8,16,24})do
  press(4)
  assert(read(0x7309)==index,'Native down direction')
 end
 local first=preview(24,25,firstTier)
 assert(first.health==31 and first.private_size==0,'Original preview size and health')
 if route==0 then
  local native={0,3,2,1,0,1,2,3}
  for i=1,7 do
   press(32)
   local s=preview(24,25,firstTier)
   assert(s.variant==i and s.native_character==native[i+1] and s.health==31,
    'Original roster preview identity '..json(s))
  end
  press(1);preview(25,26,firstTier)
  press(32);preview(25,39,firstTier)
  press(32);preview(25,39,firstTier)
  press(32);preview(25,43,firstTier)
 elseif route==2 then
  for _=1,5 do press(32)end
  local lina=preview(24,25,firstTier)
  assert(lina.variant==5 and lina.native_character==1 and lina.health==31,
   'Native Lina variant and health')
 end
 press(16)
 wait(active)
 firstActive=snapshot()
 assert(firstActive.world==0 and firstActive.level==0 and firstActive.area==5
  and firstActive.x==40 and firstActive.lives==2,'Authored 1-1 cold entrance')
 assert(read(0x7ffb)==0 and read(0x7ffc)==0,'Ordinary game with no cheats')
 if route==0 then
  assert(firstActive.owner==43 and firstActive.status==firstTier,
   'Sonic cold tier '..json(firstActive))
  finish(true,rom==old and 'Old SMB2 preview contaminated Sonic startup'
                       or 'SMB2 previews no longer contaminate Sonic startup')
  return
 end
 assert(firstActive.owner==25 and firstActive.health==31,'Original SMB2 cold health')
 bits=1
 wait(function()return active() and read(0x75)+256*read(0x5c)>=100 end)
 terminal=snapshot()
 assert(terminal.owner==25 and terminal.lives==2 and terminal.status==1
  and terminal.health==31 and terminal.private_size==0 and terminal.size==0,
  'Original SMB2 active stage form '..json(terminal))
 finish(true,'SMB2 stage retains two hearts and large form')
end)

emu.addMemoryCallback(function(_,value)
 local pc=emu.getState()['cpu.pc']
 if pc~=0xaf8d then return end
 local mapped=emu.convertAddress(0xaf8a)
 if not mapped or mapped.memType~=emu.memType.nesPrgRom
  or mapped.address~=118*8192+(0xaf8a&8191) then return end
 local s=snapshot()
 if #writes<24 then writes[#writes+1]={frame=frame,tier=value,mode=s.mode,owner=s.owner}end
end,emu.callbackType.write,0x75b)
emu.addEventCallback(function()
 polls=polls+1
 emu.setInput({right=bits==1,down=bits==4,start=bits==16,select=bits==32},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 if stopped then return end
 frame=frame+1
 if frame>2400 then finish(false,'Bounded native run');return end
 local ok,why=coroutine.resume(task)
 if not ok then finish(false,why)end
end,emu.eventType.endFrame)
