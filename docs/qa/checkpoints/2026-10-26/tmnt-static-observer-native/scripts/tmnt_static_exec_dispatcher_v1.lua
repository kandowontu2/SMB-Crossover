-- Observer successor only. No emulated reads/writes, rate or outcome changes.
-- Every actual host memory callback is registered at startup. Runtime exec
-- registrations become ordered Lua slots, including imported CHR observers.
assert(not TMNT_STATIC_EXEC,'One static dispatcher per generated harness')
local original=assert(emu.addMemoryCallback)
local slots,installed,serial,hostNonExec={},false,0,0
local function add(fn,kind,first,last,...)
 assert(type(fn)=='function' and type(first)=='number','Valid memory callback')
 if kind~=emu.callbackType.exec then
  assert(not installed,'No runtime host memory-callback registration')
  hostNonExec=hostNonExec+1
  return original(fn,kind,first,last,...)
 end
 assert(select('#',...)==0,'Pinned exec APIs have no extra mapping parameters')
 last=last or first
 assert(first>=0 and first<=last and last<=0xffff,'CPU exec-address range')
 serial=serial+1
 for pc=first,last do
  local list=slots[pc]
  if not list then list={};slots[pc]=list end
  list[#list+1]=fn
 end
 return serial
end
emu.addMemoryCallback=add
TMNT_STATIC_EXEC={}
function TMNT_STATIC_EXEC.install()
 assert(not installed,'Static dispatcher installed exactly once')
 installed=true
 original(function(pc,...)
  local list=slots[pc]
  if not list then return end
  -- Freeze this event's length. A callback added while dispatching first runs
  -- on the next event, retaining the historical registration order.
  for i=1,#list do list[i](pc,...)end
 end,emu.callbackType.exec,0,0xffff)
end
function TMNT_STATIC_EXEC.status()
 return{installed=installed,lua_exec_registrations=serial,host_nonexec_registrations=hostNonExec,host_exec_dispatchers=installed and 1 or 0}
end
