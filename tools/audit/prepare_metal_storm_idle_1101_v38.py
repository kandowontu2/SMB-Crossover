"""Measure native empty-opening idle/walk throughput without state writes."""
from pathlib import Path
import prepare_metal_storm_shots_1101_v35 as P
from prepare_selected_native_packet_v1 import prepare,sha
O=P.P.R/'build/metal-storm-idle-1101-v38'

def main():
 O.mkdir(exist_ok=True)
 ref=P.P.R/'tools/reference/metal_storm_natural_armor_1101_v26.lua';t=ref.read_text()
 a=t.index('  local x=worldx()');z=t.index('  ticks=ticks+1',a)
 t=t[:a]+"  pad.right=age>=120\n"+t[z:]
 t=t.replace("local function finish(reason)","""local starts={0,0}
local sums={0,0}
local counts={0,0}
local maxCycles={0,0}
local startCycle=nil
local startBucket=nil
emu.addMemoryCallback(function()
 if phase~='play' or age>=240 then return end
 local b=age<120 and 1 or 2
 starts[b]=starts[b]+1;startBucket=b;startCycle=emu.getState()['cpu.cycleCount']
end,emu.callbackType.exec,assert(L.NoDecTimers))
emu.addMemoryCallback(function()
 if not startCycle then return end
 local n=emu.getState()['cpu.cycleCount']-startCycle
 sums[startBucket]=sums[startBucket]+n;counts[startBucket]=counts[startBucket]+1
 maxCycles[startBucket]=math.max(maxCycles[startBucket],n);startCycle=nil
end,emu.callbackType.exec,assert(L.PauseSkip)+2)
local function finish(reason)
 local p=assert(io.open(OUTPUT..'performance.json','w'))
 p:write(string.format('{"physical_frames_per_phase":120,"idle":{"completed_updates":%d,"mean_cycles":%.1f,"max_cycles":%d},"walk":{"completed_updates":%d,"mean_cycles":%.1f,"max_cycles":%d}}',counts[1],sums[1]/math.max(1,counts[1]),maxCycles[1],counts[2],sums[2]/math.max(1,counts[2]),maxCycles[2]));p:close()
""")
 t=t.replace('local passed=got and spawned and matured and', 'local passed=age>=240 and worldx()>40 and')
 t=t.replace("if r('PlayerStatus')==1 then got=true;finish('armor-collected')", "if age>=240 then finish('idle-walk-profile')")
 prepare(O/'native',P.O/'candidate.nes',t,[Path(__file__),ref],expected=sha(P.O/'candidate.nes'),timeout=90,scope='Controller-only cold selection;120 physical idle frames then120 walking, no attacks or state writes. Actual foreground NoDecTimers to PauseSkip+2 wall CPU cycles including interrupts; not a whole-roster benchmark.')
if __name__=='__main__':main()
