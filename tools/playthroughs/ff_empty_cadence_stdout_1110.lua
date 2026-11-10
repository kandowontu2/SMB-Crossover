-- Cold title/menu, four settled Main updates, then32 idle +48 Right-only.
-- Input/read-only callbacks only; no files, emulated writes, cheats or captures.
local pin=assert(os.getenv('SMB_STDOUT_ROM_SHA'))
local frame,polls,pad,settled,ticks=0,0,0,0,0
local started,done,menuDone=false,false,false
local live,beginFrame,beginSkipped,lastFrame
local completions,phases={},{}
local function r(a)return emu.read(a,emu.memType.nesDebug)end
local function active()return r(0x771)==1 and r(0x773)==3 and r(15)==8 end
local function x()return r(0x75)+256*r(0x5c)end
local function state()
 local enemies={};for i=0,5 do enemies[#enemies+1]=r(0x10+i)end
 return {frame=frame,ticks=ticks,x=x(),y=r(0xbd),engine=r(15),lives=r(0x75f),
  raw=r(0x6002),variant=r(0x5fef),power=r(0x5fc5),skipped=r(0x13a),enemies=enemies}
end
local function json(v)
 if type(v)=='string'then return string.format('%q',v)end
 if type(v)~='table'then return tostring(v)end
 local out={};if #v>0 then for i,a in ipairs(v)do out[i]=json(a)end;return '['..table.concat(out,',')..']'end
 for k,a in pairs(v)do out[#out+1]=json(tostring(k))..':'..json(a)end;table.sort(out);return '{'..table.concat(out,',')..'}'
end
local function finish(ok,why)
 if done then return end;done=true;pad=0
 local duration,zero,maximum,total=0,0,0,0
 if beginFrame and lastFrame then
  duration=lastFrame-beginFrame+1
  for f=beginFrame,lastFrame do
   local n=completions[f]or 0;total=total+n;maximum=math.max(maximum,n)
   if n==0 then zero=zero+1 end
  end
 end
 print('SMB_NATIVE_RECEIPT '..json({passed=ok,reason=why,ROM_SHA256=pin,
  controller_only=true,script_RAM_writes=false,output_files=0,physical_frames=frame,
  input_polls=polls,settled_Main=settled,measured_Main=ticks,
  inclusive_video_frames=duration,zero_completion_frames=zero,maximum_Main_per_frame=maximum,
  counted_completions=total,native_lag_NMI=beginSkipped and ((r(0x13a)-beginSkipped)&255)or -1,
  phases=phases,terminal=state(),
  scope='80 actual Main completions in inclusive physical frame interval, four warm settled updates, six empty enemy slots before/after every Main.32idle then48Right. Native NmiSkipped modulo256. Not forced60fps or exhaustive route/art/audio proof.'}))
 emu.stop(ok and 0 or 1)
end
local function guarded(fn)return function(...)
 if done then return end;local ok,why=pcall(fn,...);if not ok then finish(false,tostring(why))end
end end
local function native(pc)
 local a=emu.convertAddress(pc)
 return a and a.memType==emu.memType.nesPrgRom and a.address==126*8192+(pc&8191)
end
local function empty()
 assert(r(0x6002)==22 and r(0x5fef)==0 and r(0x75f)==2 and r(0x5fc5)==0,'Identity/life/power')
 assert(r(0x7ffc)==0 and r(0x7ffb)==0 and r(0x7fe1)==0,'Natural Easy without cheats')
 for i=0,5 do assert(r(0x10+i)==0,'Enemy entered empty profile')end
end
emu.addMemoryCallback(guarded(function()
 if not native(0x82d9)then return end
 assert(not live,'Synchronous Main')
 local s=emu.getState();local sp=s['cpu.sp']
 local ret=(r(0x100+((sp+1)&255))+256*r(0x100+((sp+2)&255))+1)&65535
 assert(ret==0x82be or ret==0x82d0,'Literal IdleLoop caller')
 local observe=menuDone and active()
 if observe then empty()end
 live={ret=ret,sp=(sp+2)&255,observe=observe}
end),emu.callbackType.exec,0x82d9)
for _,pc in ipairs({0x82be,0x82d0})do
 emu.addMemoryCallback(guarded(function()
  if not native(pc)or not live then return end
  local cpu=emu.getState();if cpu['cpu.sp']~=live.sp or pc~=live.ret then return end
  local observe=live.observe;live=nil
  if not observe then return end
  assert(active(),'Profile left ordinary gameplay');empty()
  if settled<4 then settled=settled+1;return end
  if not started then started=true;beginFrame=frame;beginSkipped=r(0x13a);phases[1]={name='idle32',before=state()}end
  ticks=ticks+1;lastFrame=frame;completions[frame]=(completions[frame]or 0)+1
  if ticks==32 then phases[1].after=state();phases[2]={name='Right48',before=state()};pad=1 end
  if ticks==80 then phases[2].after=state();pad=0 end
end),emu.callbackType.exec,pc)
end
local function frames(n)for _=1,n do coroutine.yield()end end
local function press(b)pad=b;frames(4);pad=0;frames(8)end
local function ready(fn)for _=1,900 do if fn()then return end;coroutine.yield()end;error('Natural menu timeout')end
local task=coroutine.create(function()
 ready(function()return frame>=70 and r(0x6004)==1 and r(0x775)==0 end)
 press(16);ready(function()return r(0x7307)==2 and r(0x775)==0 end)
 assert(r(0x7309)==0,'Initial roster slot')
 for _,b in ipairs({4,4,1,1,1,1,1})do press(b)end
 assert(r(0x7309)==21 and r(0x6002)==22 and r(0x5fef)==0,'Fighter slot')
 press(16);menuDone=true
 while true do coroutine.yield()end
end)
emu.addEventCallback(guarded(function()
 polls=polls+1
 emu.setInput({right=pad&1~=0,down=pad&4~=0,start=pad&16~=0},0)
end),emu.eventType.inputPolled)
emu.addEventCallback(guarded(function()
 frame=frame+1;assert(frame<=2000,'Physical bound')
 if ticks>=80 then assert(ticks==80 and x()>40 and x()<160,'Exact empty profile endpoint');finish(true,'Natural empty80-Main profile');return end
 local ok,why=coroutine.resume(task);assert(ok,why)
end),emu.eventType.endFrame)
