-- Passive profile on actual power-on controller inputs. No emulated writes.
local c=assert(WHIP_PROFILE)
local frame,depth,irqCycles,irqStart=0,0,0,nil
local regs,selector,mode={},0,0
local active,totals={},{}
local rd=function(a)return emu.read(a,emu.memType.nesDebug)end
local cycles=function()return emu.getState()['cpu.cycleCount']end
if c.mapper=='mmc3' then
 emu.addMemoryCallback(function(_,v)selector=v&7;mode=(v>>6)&1 end,emu.callbackType.write,0x8000)
 emu.addMemoryCallback(function(_,v)if selector>=6 then regs[selector]=v&63 end end,emu.callbackType.write,0x8001)
else
 for a=0x5114,0x5117 do
  emu.addMemoryCallback(function(_,v)regs[a-0x510e]=v&63 end,emu.callbackType.write,a)
 end
end
local function bank(pc)
 if pc>=0xe000 then return 63 end
 if c.mapper=='mmc5' then return regs[pc>=0xc000 and 8 or pc>=0xa000 and 7 or 6]or-1 end
 if pc>=0xc000 then return mode==0 and 62 or(regs[6]or-1)end
 if pc>=0xa000 then return regs[7]or-1 end
 return mode==0 and(regs[6]or-1)or 62
end
local function guard(h)
 if bank(h.address)~=h.physical_bank then return false end
 for i,v in ipairs(h.bytes)do assert(rd(h.address+i-1)==v,'Actual profile bank/bytes '..h.label)end
 return true
end
for _,pair in ipairs({{'NMI','NMIEnd'},{'IRQ','IRQEnd'}})do
 local a,b=c.hooks[pair[1]],c.hooks[pair[2]]
 emu.addMemoryCallback(function()
  if not guard(a)then return end
  if depth==0 then irqStart=cycles()-7 end;depth=depth+1
 end,emu.callbackType.exec,a.address)
 emu.addMemoryCallback(function()
  if not guard(b)then return end
  depth=depth-1;assert(depth>=0,'Balanced profile interrupt')
  if depth==0 then irqCycles=irqCycles+cycles()+6-assert(irqStart);irqStart=nil end
 end,emu.callbackType.exec,b.address)
end
local file=assert(io.open(ROSTER_CONFIG.out..'whip-hot.csv','w'))
file:write('frame,kind,foregroundCycles,totalCycles\n')
for _,kind in ipairs({'Probe','Envelope'})do
 totals[kind]={calls=0,cycles=0,min=100000,max=0,helperCalls=0}
 local a,b,helper=c.hooks[kind],c.hooks[kind..'Resume'],c.hooks[kind..'Helper']
 emu.addMemoryCallback(function()
  if depth~=0 or frame<540 or not guard(a)then return end
  assert(not active[kind],'No recursive measured probe')
  active[kind]={clock=cycles(),irq=irqCycles}
 end,emu.callbackType.exec,a.address)
 emu.addMemoryCallback(function()
  if depth~=0 or frame<540 or not guard(helper)then return end
  totals[kind].helperCalls=totals[kind].helperCalls+1
 end,emu.callbackType.exec,helper.address)
 emu.addMemoryCallback(function()
  if depth~=0 or not active[kind]or not guard(b)then return end
  local v=active[kind];local all=cycles()-v.clock;local fg=all-(irqCycles-v.irq)
  local t=totals[kind];t.calls=t.calls+1;t.cycles=t.cycles+fg;t.min=math.min(t.min,fg);t.max=math.max(t.max,fg)
  file:write(table.concat({frame,kind,fg,all},',')..'\n');active[kind]=nil
 end,emu.callbackType.exec,b.address)
end
emu.addEventCallback(function()frame=frame+1 end,emu.eventType.endFrame)
local stop=emu.stop
function emu.stop(code)
 file:close()
 local f=assert(io.open(ROSTER_CONFIG.out..'whip-hot-summary.json','w'))
 f:write('{"frames":'..frame..',"exit":'..code..',"routines":{')
 local sep=''
 for _,kind in ipairs({'Probe','Envelope'})do
  local t=totals[kind]
  assert(t.calls>0,'Actual ordinary Pit arrows exercise measured path')
  f:write(sep..'"'..kind..'":{"calls":'..t.calls..',"cycles":'..t.cycles..',"min":'..t.min..',"max":'..t.max..',"helperCalls":'..t.helperCalls..'}');sep=','
 end
 f:write('}}\n');f:close();stop(code)
end
return function()return{}end
