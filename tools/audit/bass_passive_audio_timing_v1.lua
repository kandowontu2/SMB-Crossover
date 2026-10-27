-- Passive scoped timings only. All host callbacks register once at startup.
-- Return close()->stats; caller may combine it with ROSTER_CONFIG.bass_close.
local C=assert(BASS_PASSIVE_AUDIO_TIMING)
local R=assert(ROSTER_CONFIG)
local f=assert(io.open((C.out or R.prefix or R.out)..'bass-audio-timing.csv','w'))
f:write('name,entryFrame,returnFrame,entryCycle,returnCycle,bodyCycles,nominalFullCycles,entrySP,returnSP,entryBank,returnBank,engine,power,state,world,level,sfxId,lzRemaining,delay,dmcActive\n')
local live,totals={},{}
local closed=false
local function r(n)return emu.read(assert(C.ram[n],n),emu.memType.nesDebug)end
local function physical(pc)local q=emu.convertAddress(pc);return q and q.address//8192 or-1 end
local function enabled()return r('SelectedCharacter')==9 and r('RlVariant')==0 and r('OperMode')==1 and r('OperMode_Task')==3 end
local function hook(h,fn)
 emu.addMemoryCallback(function()
  if closed then return end
  local b=physical(h.pc);local valid=false;for _,x in ipairs(h.banks)do if b==x then valid=true end end
  if not valid then return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==v,'Actual passive audio hook')end
  fn(emu.getState(),b)
 end,emu.callbackType.exec,h.pc)
end
for _,q in ipairs(C.scopes)do
 totals[q.name]={count=0,body_cycles=0,nominal_full_cycles=0,min_body=nil,max_body=0,dmc_active_calls=0,samples={}}
 hook(q.entry,function(s,b)
  if not enabled()then return end
  assert(not live[q.name],'No recursive passive timing scope '..q.name)
  live[q.name]={cycle=s['cpu.cycleCount'],frame=s['ppu.frameCount'],sp=s['cpu.sp'],bank=b,engine=r('GameEngineSubroutine'),power=r('PlayerStatus'),state=r('Player_State'),world=r('WorldNumber'),level=r('LevelNumber'),sfx=r('BassSourceId'),lz=r('XgLzRemaining'),delay=r('XgAudioDelay'),dmc=r('BassDmcActive')}
 end)
 for _,h in ipairs(q.returns)do
  hook(h,function(s,b)
   local a=live[q.name];if not a or s['cpu.sp']~=a.sp then return end
   local body=s['cpu.cycleCount']-a.cycle;assert(body>=0,'Monotonic actual cycle counter')
   local full=body+q.terminal_cycles+q.hardware_entry_cycles
   local t=totals[q.name];t.count=t.count+1;t.body_cycles=t.body_cycles+body;t.nominal_full_cycles=t.nominal_full_cycles+full;t.max_body=math.max(t.max_body,body);t.min_body=t.min_body and math.min(t.min_body,body)or body;t.samples[#t.samples+1]=body
   if a.dmc~=0 or r('BassDmcActive')~=0 then t.dmc_active_calls=t.dmc_active_calls+1 end
   f:write(table.concat({q.name,a.frame,s['ppu.frameCount'],a.cycle,s['cpu.cycleCount'],body,full,a.sp,s['cpu.sp'],a.bank,b,a.engine,a.power,a.state,a.world,a.level,a.sfx,a.lz,a.delay,a.dmc},',')..'\n')
   live[q.name]=nil
  end)
 end
end
return function()
 if closed then return{already_closed=true}end;closed=true;f:close()
 local pending={}
 for name,a in pairs(live)do pending[#pending+1]={name=name,entry_frame=a.frame,entry_cycle=a.cycle,entry_sp=a.sp}end
 for _,t in pairs(totals)do
  table.sort(t.samples)
  t.mean_body=t.count>0 and t.body_cycles/t.count or 0
  t.p50_body=t.count>0 and t.samples[math.max(1,math.ceil(t.count*.5))]or 0
  t.p95_body=t.count>0 and t.samples[math.max(1,math.ceil(t.count*.95))]or 0
  t.samples=nil
 end
 return{ROM_sha256=C.ROM_sha256,passive=true,scopes=totals,unfinished_at_harness_close=pending,
  scope='Actual entry-to-RTS/RTI opcode cycles, SP and physical-bank qualified. Full nominal totals add terminal6; NMI also adds hardware7. Nested scopes overlap: do not sum them.',
  limits='No game/input/state writes or instruction-wide callbacks. Terminal6/hardware7 are explicit architecture additions, not observed post-return edges; a DMC-active RTI tail may add stalls. Existing route observer owns restoration guards. Native endpoint can clip one final in-flight scope.'}
end
