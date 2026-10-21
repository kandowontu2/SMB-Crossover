-- Passive entry-to-real-return timing on ordinary power-on inputs.
local c=assert(ATTACK_PROFILE)
local frame,depth,interruptCycles,interruptStart=0,0,0,nil
local regs,selector,mode={},0,0
local function rd(a)return emu.read(a,emu.memType.nesDebug)end
local function cycle()return emu.getState()['cpu.cycleCount']end
if c.mapper=='mmc3'then
 emu.addMemoryCallback(function(_,v)selector=v&7;mode=(v>>6)&1 end,emu.callbackType.write,0x8000)
 emu.addMemoryCallback(function(_,v)if selector>=6 then regs[selector]=v&63 end end,emu.callbackType.write,0x8001)
else
 for a=0x5114,0x5117 do
  emu.addMemoryCallback(function(_,v)regs[a-0x510e]=v&63 end,emu.callbackType.write,a)
 end
end
local function bank(pc)
 if pc>=0xe000 then return 63 end
 if c.mapper=='mmc5'then return regs[pc>=0xc000 and 8 or pc>=0xa000 and 7 or 6]or-1 end
 if pc>=0xc000 then return mode==0 and 62 or(regs[6]or-1)end
 if pc>=0xa000 then return regs[7]or-1 end
 return mode==0 and(regs[6]or-1)or 62
end
local function guard(h)
 if bank(h.address)~=h.physical_bank then return false end
 for i,v in ipairs(h.bytes)do assert(rd(h.address+i-1)==v,'Actual profile bank/bytes '..h.label)end
 return true
end
local intervals=assert(io.open(ROSTER_CONFIG.out..'attack-profile.csv','w'))
intervals:write('routine,frameStart,frameEnd,foregroundCycles,totalCycles,interruptionCycles,shots,enemies,returnPC,returnBank\n')
local interruptRows=assert(io.open(ROSTER_CONFIG.out..'attack-interrupts.csv','w'))
interruptRows:write('kind,frameStart,frameEnd,cycles\n')
local interruptEntries={}
for _,pair in ipairs({{'NMI','NMIEnd'},{'IRQ','IRQEnd'}})do
 local name=pair[1];local a,b=c.interrupts[name],c.interrupts[pair[2]]
 emu.addMemoryCallback(function()
  if not guard(a)then return end
  interruptEntries[name]={clock=cycle()-7,frame=frame}
  if depth==0 then interruptStart=cycle()-7 end;depth=depth+1
 end,emu.callbackType.exec,a.address)
 emu.addMemoryCallback(function()
  if not guard(b)then return end
  local started=assert(interruptEntries[name],'Paired actual interrupt')
  interruptRows:write(table.concat({name,started.frame,frame,cycle()+6-started.clock},',')..'\n')
  interruptEntries[name]=nil
  depth=depth-1;assert(depth>=0,'Balanced actual interrupts')
  if depth==0 then interruptCycles=interruptCycles+cycle()+6-assert(interruptStart);interruptStart=nil end
 end,emu.callbackType.exec,b.address)
end
local counts={}
for name,h in pairs(c.routines)do
 local active,returns=nil,{}
 counts[name]={entered=0,returned=0}
 emu.addMemoryCallback(function()
  if depth~=0 or frame<541 or not guard(h)then return end
  assert(not active,'Profile entry is not recursively replaced: '..name)
  assert(rd(c.ram.SelectedCharacter)==6 and rd(c.ram.CrossoverBehaviorVersion)==0,'Actual ordinary Pit/Easy profile identity')
  local sp=emu.getState()['cpu.sp']
  local pc=(rd(0x100+((sp+1)&255))+256*rd(0x100+((sp+2)&255))+1)&65535
  local shots,enemies=0,0
  for i=0,9 do if rd(c.ram.RgShotType+i)>0 then shots=shots+1 end end
  for i=0,5 do if rd(c.ram.Enemy_Flag+i)>0 then enemies=enemies+1 end end
  active={clock=cycle(),irq=interruptCycles,sp=(sp+2)&255,pc=pc,frame=frame,shots=shots,enemies=enemies}
  counts[name].entered=counts[name].entered+1
  if not returns[pc]then
   returns[pc]=true
   emu.addMemoryCallback(function()
    if not active or depth~=0 or emu.getState()['cpu.sp']~=active.sp or bank(h.address)~=h.physical_bank then return end
    local v=active;local total=cycle()-v.clock;local irq=interruptCycles-v.irq
    assert(total>=irq,'Nonnegative foreground profile span')
    intervals:write(table.concat({name,v.frame,frame,total-irq,total,irq,v.shots,v.enemies,pc,bank(pc)},',')..'\n')
    counts[name].returned=counts[name].returned+1;active=nil
   end,emu.callbackType.exec,pc)
  end
 end,emu.callbackType.exec,h.address)
end
emu.addEventCallback(function()frame=frame+1 end,emu.eventType.endFrame)
local stop=emu.stop
function emu.stop(code)
 intervals:close();interruptRows:close()
 local f=assert(io.open(ROSTER_CONFIG.out..'attack-profile-counts.csv','w'))
 f:write('routine,entered,returned\n')
 for name,v in pairs(counts)do f:write(table.concat({name,v.entered,v.returned},',')..'\n')end
 f:close();stop(code)
end
return function()return{}end
