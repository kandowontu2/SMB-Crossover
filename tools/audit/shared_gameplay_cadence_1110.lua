-- Count physical frames and actual controller reads during natural 1-1 play.
local frame, updates, contacts = 0, 0, 0
local polled, input = false, {}
local function read(addr) return emu.read(addr, emu.memType.nesDebug) end
local function x() return read(0x75) + 256 * read(0x5c) end
local function active()
 return read(0x771)==1 and read(0x773)==3 and read(0x0f)==8
    and read(0x754)==5 and read(0x75f)==2 and read(0x74a)==0
    and read(0x6002)==C.slot and read(0x7fe1)==0 and read(0x7ffb)==0 and read(0x7ffc)==0
end

local function observe(pc, bytes, action)
 emu.addMemoryCallback(function()
  if not active() then return end
  local at = emu.convertAddress(pc)
  if not at or at.memType~=emu.memType.nesPrgRom or at.address~=126*8192+(pc&8191) then return end
  for i, byte in ipairs(bytes) do assert(read(pc+i-1)==byte) end
  action()
 end, emu.callbackType.exec, pc)
end
observe(0x82d9, {0xa9,0xff,0x8d}, function() updates=updates+1 end)
observe(0x9659, {0xad,0x02,0x60}, function() contacts=contacts+1 end)
local function markPoll() polled=true end
emu.addMemoryCallback(markPoll,emu.callbackType.read,0x4016)
emu.addMemoryCallback(markPoll,emu.callbackType.read,0x4017)
emu.addEventCallback(function() emu.setInput(input,0) end,emu.eventType.inputPolled)

local function wait(n) for _=1,n do coroutine.yield() end end
local function press(key) input={[key]=true};wait(4);input={};wait(8) end
local function untilReady(predicate)
 for _=1,600 do if predicate() then return end;wait(1) end
 error('Title, roster or gameplay readiness timeout')
end
local function count(phase, countFrames, lastX)
 local out={phase=phase,frames=0,updates=0,contacts=0,no_controller_read=0,lag_nmi=0,zero_updates=0,
            with_enemy=0,x_initial=x(),x_final=x()}
 for _=1,countFrames do
  local previous, previousContacts, skipped = updates, contacts, read(0x13a)
  wait(1)
  assert(active(),'Expected uninterrupted Easy 1-1')
  out.frames=out.frames+1
  out.updates=out.updates+updates-previous
  out.contacts=out.contacts+contacts-previousContacts
  out.lag_nmi=out.lag_nmi+((read(0x13a)-skipped)&255)
  if not polled then out.no_controller_read=out.no_controller_read+1 end
  if updates==previous then out.zero_updates=out.zero_updates+1 end
  for slot=0,5 do
   if read(0x10+slot)==1 and read(0x17+slot)==6 then out.with_enemy=out.with_enemy+1;break end
  end
  out.x_final=x()
  if lastX and out.x_final>=lastX then break end
 end
 return out
end
local function row(out)
 local fields={string.format('"phase":%q',out.phase)}
 for _, name in ipairs({'frames','updates','contacts','no_controller_read','lag_nmi','zero_updates',
                       'with_enemy','x_initial','x_final'}) do
  fields[#fields+1]=string.format('%q:%d',name,out[name])
 end
 return '{'..table.concat(fields,',')..'}'
end
local task=coroutine.create(function()
 untilReady(function() return frame>=70 and read(0x6004)==1 and read(0x775)==0 end)
 press('start')
 untilReady(function() return read(0x7307)==2 and read(0x775)==0 end)
 assert(read(0x7309)==0)
 for _=1,C.slot do press('right') end
 assert(read(0x7309)==C.slot and read(0x6002)==C.slot)
 press('start')
 untilReady(active)
 wait(4)
 local idle=count('idle',120)
 input={right=true}
 local walk=count('walk',210,258)
 assert(idle.x_initial==idle.x_final and idle.with_enemy==0)
 assert(walk.x_final>=258 and walk.with_enemy>0 and walk.contacts>0)
 local file=assert(io.open(OUTPUT..'result.json','w'))
 file:write(string.format('{"ROM_sha256":%q,"raw":%d,"controller_only":true,"phases":[%s,%s]}\n',
                         C.rom,C.slot,row(idle),row(walk)))
 file:close()
 emu.stop(0)
end)
emu.addEventCallback(function()
 frame=frame+1
 local ok,message=coroutine.resume(task)
 assert(ok,message)
 polled=false
end,emu.eventType.endFrame)
